from typing import List
from uuid import UUID
from django.shortcuts import get_object_or_404
from ninja import Router
from ninja.errors import HttpError
from typing import Optional
from django.db.models import Count

from .models import Contest, UserGroup, VirtualProblem
from .schemas import (
    UserGroupIn, UserGroupOut, 
    ContestIn, ContestOut, ContestListOut, ContestDetailOut,
    VirtualProblemIn, VirtualProblemBindIn,
    VirtualProblemOut, GroupAddMembersIn
)
from .filters import UserGroupFilter, ContestFilter
# 导入你提供的 fu_crud 核心函数
from common.fu_crud import create, update, delete, retrieve, get_or_none

router = Router(tags=["竞赛管理"])

# ================= 用户组管理  =================
@router.post("/groups", response=UserGroupOut, summary="创建用户组")
def create_group(request, data: UserGroupIn):
    user = request.auth  # 当前登录用户对象
    payload = data.dict()
    payload['creator'] = user
    usergroup = UserGroup.objects.create(**payload)
    usergroup.members.add(user)
    usergroup.member_count = 1
    return usergroup

@router.get("/groups", response=List[UserGroupOut], summary="获取用户组列表")
def list_groups(request, name: Optional[str] = None):
    query_set = UserGroup.objects.annotate(member_count=Count('members'))
    if name:
        query_set = query_set.filter(name__icontains=name)
    
    query_set = query_set.order_by('-created_at')
    
    return query_set

@router.patch("/groups/{id}", response=UserGroupOut, summary="更新用户组")
def update_group(request, id: str, data: UserGroupIn):
    return update(request, id, data, UserGroup)

@router.delete("/groups/{id}", response=UserGroupOut, summary="删除用户组")
def delete_group(request, id: str):
    instance = get_object_or_404(UserGroup, id=id)
    # 权限校验：非创建者不能删除
    if str(instance.creator_id) != str(request.auth.id):
        raise HttpError(403, "无权删除他人创建的用户组")
    
    # 返回 delete 函数处理后的实例
    return delete(id, UserGroup)

@router.post("/groups/{id}/members", response=UserGroupOut, summary="向用户组增加成员")
def add_group_members(request, id: str, data: GroupAddMembersIn):
    """
    增加用户组成员
    """
    # 1. 获取实例
    instance = get_object_or_404(UserGroup, id=id)

    # 2. 权限校验：只有创建者可以向组内加人
    if str(instance.creator_id) != str(request.auth.id):
        raise HttpError(403, "只有创建者可以管理成员")

    # 3. 执行添加操作 (ManyToManyField 的标准操作)
    instance.members.add(*data.user_ids)

    # 4. 按照要求：return 实例
    return instance

@router.delete("/groups/{id}/members", response=UserGroupOut, summary="从用户组移除成员")
def remove_group_members(request, id: str, data: GroupAddMembersIn):
    """
    移除用户组成员
    """
    instance = get_object_or_404(UserGroup, id=id)

    if str(instance.creator_id) != str(request.auth.id):
        raise HttpError(403, "只有创建者可以移除成员")

    # 执行移除
    instance.members.remove(*data.user_ids)

    # return 实例
    return instance

# ================= 竞赛管理 (Contest) =================

@router.post("/contests", response=ContestOut, summary="创建竞赛")
def create_contest(request, data: ContestIn):
    payload = data.dict(exclude={'allowed_group_ids'})
    allowed_group_ids = data.allowed_group_ids
    instance = create(request, payload, Contest)
    if allowed_group_ids:
        instance.allowed_groups.set(allowed_group_ids)
        
    return instance

@router.get("/contests", response=List[ContestListOut], summary="获取竞赛列表")
def list_contests(request, filters: ContestFilter = ContestFilter()):
    query_set = retrieve(request, Contest, filters)
    
    for item in query_set:
        item.creator_name = item.creator.username
        
    return query_set

@router.get("/contests/{id}", response=ContestDetailOut, summary="获取竞赛详情")
def get_contest_detail(request, id: str):
    instance = get_or_none(Contest, id=id)
    if not instance:
        raise HttpError(404, "竞赛不存在")
    
    instance.creator_name = instance.creator.username
    instance.problems = list(instance.contest_problem.select_related('problem').all())
    # 补全关联题目中 Schema 需要的 title
    for cp in instance.problems:
        cp.title = cp.problem.title
        
    instance.virtual_problems = list(instance.virtual_problems.all())
    
    return instance

@router.patch("/contests/{id}", response=ContestOut, summary="更新竞赛")
def update_contest(request, id: str, data: ContestIn):
    # 处理 M2M 字段更新
    allowed_group_ids = data.dict().get('allowed_group_ids')
    
    # 调用 update
    instance = update(request, id, data, Contest)
    
    if allowed_group_ids is not None:
        instance.allowed_groups.set(allowed_group_ids)
        
    return instance

@router.delete("/contests/{id}", response=ContestOut, summary="删除竞赛")
def delete_contest(request, id: str):
    instance = get_object_or_404(Contest, id=id)
    if str(instance.creator_id) != str(request.auth.id):
        raise HttpError(403, "只有创建者可以删除此竞赛")
        
    return delete(id, Contest)

# ================= 虚拟题目管理 (VirtualProblem) =================

@router.post("/virtual-problems", response=VirtualProblemOut, summary="创建虚拟题目")
def create_v_problem(request, data: VirtualProblemIn):
    # 注意：fu_crud.create 默认注入 sys_creator_id
    # 请确保 VirtualProblem 模型中有此字段，或在 create 函数中映射 author
    instance = create(request, data, VirtualProblem)
    return instance

@router.patch("/virtual-problems/{id}/bind", response=VirtualProblemOut, summary="虚拟题转正")
def bind_v_problem(request, id: str, data: VirtualProblemBindIn):
    # 这里的 data 包含 real_problem_id
    # 调用 update 并返回实例
    return update(request, id, data, VirtualProblem)