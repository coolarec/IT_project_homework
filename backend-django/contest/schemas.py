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
    prepare_start_time: date
    prepare_end_time: date
    contest_start_time: date
    contest_end_time: date
    notice: Optional[str] = ''
    status: int = 0
    privite_permission: int = 0  # 对应模型中的拼写错误
    freeze_time: int = 0
    allowed_group_ids: List[UUID] = [] # 用于创建时关联用户组

class ContestOut(Schema):
    id: UUID
    title: str
    prepare_start_time: date
    prepare_end_time: date
    contest_start_time: date
    contest_end_time: date
    notice: str
    status: int
    privite_permission: int
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
    status: int
    prepare_start_time: date
    prepare_end_time: date
    contest_start_time: date
    contest_end_time: date
    creator_name: Optional[str] = None

# 用于竞赛详情（嵌套题目和虚拟题目）
class ContestDetailOut(ContestOut):
    virtual_problems: List[VirtualProblemOut] = []