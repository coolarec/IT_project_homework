from neo4j import GraphDatabase

class Neo4jAnalyzer:
    def __init__(self):
        self.driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "12345678"))

    def save_contest_data(self, contest_name, items):
        with self.driver.session() as session:
            for item in items:
                # 1. 建立比赛节点和参与关系
                session.run("""
                    MERGE (c:Contest {name: $c_name})
                    ON CREATE SET c.created_at = timestamp()
                    
                    MERGE (o:Organization {name: $org})
                    WITH c, o
                    UNWIND $members AS m_name
                    MERGE (u:User {name: m_name})
                    MERGE (u)-[:BELONGS_TO]->(o)
                    
                    MERGE (u)-[r:PARTICIPATED_IN]->(c)
                    SET r.rank = $rank, r.medal = $medal, r.score = $score, r.penalty = $penalty
                """, {
                    "c_name": contest_name, "org": item['organization'],
                    "members": item['members'], "rank": item['rank'],
                    "medal": item['medal'], "score": item['score'], "penalty": item['penalty']
                })
                
                # 2. 存储题目：题目节点加上 contest 属性作为唯一键的一部分
                probs = item.get('problems', {})
                for code, info in probs.items():
                    session.run("""
                        MATCH (c:Contest {name: $c_name})
                        MATCH (u:User) WHERE u.name IN $members
                        
                        MERGE (p:Problem {code: $code, contest: $c_name})
                        
                        MERGE (u)-[s:SOLVED]->(p)
                        SET s.time = $time, s.attempts = $attempts, s.status = $status
                    """, {
                        "c_name": contest_name, "members": item['members'],
                        "code": code, "time": info['time'], 
                        "attempts": info['attempts'], "status": info['status']
                    })

    def get_dashboard_data(self, contest_name=None):
        """核心查询：如果 contest_name 为空，则查全局；如果不为空，则查单场"""
        
        match_contest = "MATCH (c:Contest {name: $c_name})" if contest_name else "MATCH (c:Contest)"
        
        with self.driver.session() as session:
            params = {"c_name": contest_name}

            org_res = session.run(f"""
                {match_contest}
                MATCH (o:Organization)<-[:BELONGS_TO]-(u:User)-[r:PARTICIPATED_IN]->(c)
                RETURN o.name as name, 
                sum(case when r.medal='金' then 3 when r.medal='银' then 2 when r.medal='铜' then 1 else 0 end) as power_score
                ORDER BY power_score DESC LIMIT 20
            """, params)

            prob_res = session.run(f"""
                {match_contest}
                MATCH (p:Problem {{contest: c.name}})<-[s:SOLVED]-(u:User)
                RETURN p.code as code, avg(s.time) as avg_time, count(s) as solve_count, avg(s.attempts) as avg_attempts
                ORDER BY code
            """, params)

            medal_res = session.run(f"""
                {match_contest}
                MATCH ()-[r:PARTICIPATED_IN]->(c)
                WHERE r.medal IN ['金', '银', '铜']
                RETURN r.medal as label, count(r) as value
            """, params)

            synergy_res = session.run(f"""
                {match_contest}
                MATCH (u1:User)-[r1:PARTICIPATED_IN]->(c)<-[r2:PARTICIPATED_IN]-(u2:User)
                WHERE id(u1) < id(u2) AND r1.rank = r2.rank
                RETURN u1.name + ' & ' + u2.name as pair, count(c) as together_count
                ORDER BY together_count DESC LIMIT 500
            """, params)

            return {
                "org_ranking": [dict(r) for r in org_res],
                "problem_profile": [dict(r) for r in prob_res],
                "medal_pie": [dict(r) for r in medal_res],
                "member_synergy": [dict(r) for r in synergy_res]
            }

    def get_contests(self):
        with self.driver.session() as session:
            res = session.run("MATCH (c:Contest) RETURN c.name as name ORDER BY c.created_at DESC")
            return [r["name"] for r in res]

neo4j_analyzer = Neo4jAnalyzer()