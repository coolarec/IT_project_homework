from common.fu_schema import FuFilters
from ninja import Field
from typing import Optional
from uuid import UUID

class UserGroupFilter(FuFilters):
    # q="icontains" 表示生成查询时使用 name__icontains=value (模糊搜索)
    name: Optional[str] = Field(None, alias="name", q="icontains")
    creator_id: Optional[UUID] = None

class ContestFilter(FuFilters):
    # 搜索竞赛标题
    title: Optional[str] = Field(None, alias="title", q="icontains")
    
    # 精确匹配状态和权限
    status: Optional[int] = None
    privite_permission: Optional[int] = None
    
    # 匹配创建者
    creator_id: Optional[UUID] = None
    
    # 如果需要按部门搜索
    dept_id: Optional[UUID] = None