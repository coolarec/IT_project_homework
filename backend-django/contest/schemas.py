from ninja import Schema
from typing import Optional, List
from datetime import date, datetime
from uuid import UUID

# ================= 用户组相关 (UserGroup) =================

class UserGroupIn(Schema):
    name: str
    description: Optional[str] = None

class UserGroupOut(Schema):
    id: UUID
    name: str
    description: Optional[str]
    creator_id: UUID 
    created_at: datetime
    member_count: int = 0

class GroupAddMembersIn(Schema):
    user_ids: List[UUID]

# ================= 虚拟题目相关 (VirtualProblem) =================

class VirtualProblemIn(Schema):
    name:str
    description: str
    order:int
    color:Optional[str]=None

class VirtualProblemOut(Schema):
    id: UUID
    name:str
    contest_id: UUID
    description: str
    author_id: UUID
    created_at: datetime
    real_problem_id: Optional[UUID] = None
    order: Optional[int] =None
    color:Optional[str] = None

class VirtualProblemBindIn(Schema):
    real_problem_id: UUID

# ================= 竞赛相关 (Contest) =================

class ContestIn(Schema):
    title: str
    contest_start_time: datetime
    contest_end_time: datetime
    description:str
    notice: Optional[str] = ''
    is_public: bool = False  # 对应模型中的拼写错误
    freeze_time: int = 0
    allowed_group_ids: List[UUID] = [] # 用于创建时关联用户组

class ContestUpdteIn(Schema):
    title: Optional[str] =None
    contest_start_time: Optional[datetime]=None
    contest_end_time: Optional[datetime]= None
    description:Optional[str]= None
    notice: Optional[str] = None
    is_public: Optional[bool] = None
    freeze_time: Optional[int]=None
    allowed_group_ids: List[UUID] = [] # 用于创建时关联用户组

class ContestOut(Schema):
    id: UUID
    title: str
    contest_start_time: datetime
    contest_end_time: datetime
    notice: str
    is_public: bool = False
    freeze_time: int
    created_at: datetime
    updated_at: datetime
    creator_id: UUID
    creator_name: Optional[str] = None  # 在 API 中通过 obj.creator.username 获取
    allowed_group_ids: List[UUID] = []

# 用于竞赛列表（不带详情，减少数据量）
class ContestListOut(Schema):
    id: UUID
    title: str
    contest_start_time: datetime
    contest_end_time: datetime
    creator_name: Optional[str] = None
    is_public:bool

# 用于竞赛详情（嵌套题目和虚拟题目）
class ContestDetailOut(ContestOut):
    virtual_problems: List[VirtualProblemOut] = []


# 虚拟题目输入：用于创建和修改属性
class VirtualProblemIn(Schema):
    name: str
    description: str
    order: int = 0
    color: str = "#409EFF"

# 绑定请求参数
class VirtualProblemBindIn(Schema):
    real_problem_id: UUID

# 虚拟题目输出：包含 9 个步骤进度
class VirtualProblemOut(Schema):
    id: UUID
    name: str
    description: str
    order: int
    color: str
    is_bound: bool
    real_problem_id: Optional[UUID] = None
    real_problem_title: Optional[str] = "未绑定"
    
    # 9个进度步骤字段 (默认为 0)
    step_title_done: int = 0
    step_limit_done: int = 0
    step_description_done: int = 0
    step_input_description_done: int = 0
    step_output_description_done: int = 0
    step_example_done: int = 0
    step_hint_done: int = 0
    step_testcase_done: int = 0
    step_solution_done: int = 0

# 竞赛详情输出
class ContestDetailOutWithVp(Schema):
    id: UUID
    title: str
    description: str
    contest_start_time: datetime
    contest_end_time: datetime
    is_public: bool
    creator_name: str
    virtual_problems: List[VirtualProblemOut]