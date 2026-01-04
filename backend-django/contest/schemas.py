from ninja import Schema
from typing import Optional, List
from datetime import date, datetime

# Contest 基础输出（列表 / 详情用)
class ContestOut(Schema):
    id: int
    title: str
    prepare_start_time: date
    prepare_end_time: date
    contest_start_time: date
    contest_end_time: date
    notice: str
    status: int
    is_public: bool
    freeze_time: int
    created_at: datetime
    updated_at: datetime

# Contest 创建 / 更新
class ContestIn(Schema):
    title: str
    prepare_start_time: date
    prepare_end_time: date
    contest_start_time: date
    contest_end_time: date
    notice: Optional[str] = ''
    is_public: bool = True
    freeze_time: int = 0

# ContestProblem（比赛-题目关系）
# 输出 schema
class ContestProblemOut(Schema):
    id: int
    problem_id: int
    order: int
    color: str
    alias: str

# 创建 / 编辑
class ContestProblemIn(Schema):
    problem_id: int
    order: int
    color: str
    alias: str

# VirtualProblem（虚拟题目）
# 输出 schema（核心）
class VirtualProblemOut(Schema):
    id: int
    contest_id: int
    description: str
    author_id: int
    created_at: datetime
    real_problem_id: Optional[int]

# 创建虚拟题（创建比赛时用）
class VirtualProblemIn(Schema):
    description: str

# 虚拟题转正（绑定真实题）
class VirtualProblemBindIn(Schema):
    real_problem_id: int

# 组合型 schema
class ContestDetailOut(ContestOut):
    problems: List[ContestProblemOut]
    virtual_problems: List[VirtualProblemOut]


