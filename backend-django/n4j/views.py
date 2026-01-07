import pandas as pd
import re
from typing import List, Any, Optional
from ninja import Router, File, Form, Body
from ninja.files import UploadedFile
from opencc import OpenCC
from .services import neo4j_analyzer

router = Router()
converter = OpenCC('t2s')

def parse_time_to_minutes(val):
    """处理 '0:18:24' 或 '124' 为分钟整数"""
    if pd.isna(val) or val == "": return 0
    val_str = str(val).strip()
    if ":" in val_str:
        p = val_str.split(":")
        try:
            if len(p) == 3: return int(p[0]) * 60 + int(p[1])
            if len(p) == 2: return int(p[0])
        except: return 0
    try: return int(float(val_str))
    except: return 0

def parse_problem_cell(val):
    """解析格式: AC/1/0:18:24"""
    val = str(val).strip()
    if not val or "/" not in val: return None
    parts = val.split("/")
    if len(parts) >= 3 and parts[0].upper() in ["AC", "FB"]:
        try:
            return {
                "status": parts[0].upper(),
                "attempts": int(parts[1]),
                "time": parse_time_to_minutes(parts[2])
            }
        except: return None
    return None

def parse_rank_and_medal(raw):
    """解析 '#': 1 (金奖) 或 * """
    if pd.isna(raw): return None, None
    raw = str(raw).strip()
    if raw == "*": return None, None 

    m = re.match(r"^(\d+)", raw)
    rank = int(m.group(1)) if m else None

    medal = None
    if "(" in raw and ")" in raw:
        inside = raw[raw.find("(")+1: raw.find(")")].lower()
        if "金" in inside or "gold" in inside: medal = "金"
        elif "银" in inside or "silver" in inside: medal = "银"
        elif "铜" in inside or "bronze" in inside: medal = "铜"
    return rank, medal

@router.post("/preview")
def preview_excel(request, file: UploadedFile = File(...)):
    df = pd.read_excel(file, sheet_name=0)
    prob_cols = [c for c in df.columns if re.match(r"^[A-M](\s|$|\()", str(c))]
    
    official_team_count = 0
    for r in df['#']:
        rank, _ = parse_rank_and_medal(r)
        if rank is not None: official_team_count += 1

    rows = []
    for _, row in df.iterrows():
        raw_rank_val = row.get('#', '')
        rank, excel_medal = parse_rank_and_medal(raw_rank_val)
        
        if rank is None and str(raw_rank_val).strip() == "*":
            continue

        team_name = converter.convert(str(row.get('Name', ''))).strip()
        org = converter.convert(str(row.get('Organization', ''))).strip()
        members = [m.strip() for m in re.split(r"[,\s，/]+", converter.convert(str(row.get('Team Members', '')))) if m.strip()]
        
        probs = {str(col)[0]: parse_problem_cell(row[col]) for col in prob_cols if parse_problem_cell(row[col])}
        medal = excel_medal
        if not medal and rank:
            ratio = rank / official_team_count
            if ratio <= 0.1: medal = "金"
            elif ratio <= 0.3: medal = "银"
            elif ratio <= 0.6: medal = "铜"
        
        if not medal: medal = "打铁"

        rows.append({
            "rank": rank,
            "medal": medal,
            "organization": org,
            "name": team_name,
            "members": members,
            "score": int(row.get('Score', 0)),
            "penalty": parse_time_to_minutes(row.get('Time', 0)),
            "problems": probs
        })
    return rows

@router.post("/save")
def save_data(request, data: Any = Body(...)):
    neo4j_analyzer.save_contest_data(data['contest_name'], data['items'])
    return {"status": "success"}

@router.get("/dashboard")
def get_dashboard_stats(request, contest_name: str = None):
    if not contest_name or contest_name == "null":
        contest_name = None
    return neo4j_analyzer.get_dashboard_data(contest_name)

@router.get("/contests")
def list_contests(request):
    return neo4j_analyzer.get_contests()