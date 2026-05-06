from datetime import datetime
from typing import List, Optional
from uuid import UUID

from django.shortcuts import get_object_or_404
from django.utils import timezone
from ninja import Query, Router
from ninja.errors import HttpError
from django.db.models import Count
from django.db import transaction
from django.db.models import Q
from django.db.models import Count, F


from problem.models import Problem
from core.user.user_model import User
from core.user.user_schema import UserSchemaAvatarOut
from .models import Contest, UserGroup, VirtualProblem
from .schemas import (
    UserGroupIn, UserGroupOut, 
    ContestIn, ContestOut, ContestListOut, ContestDetailOut,
    VirtualProblemIn, VirtualProblemBindIn,
    VirtualProblemOut, GroupAddMembersIn,ContestUpdteIn,ContestDetailOutWithVp,
    GroupDeleteMembersIn
)
from .filters import ContestFilter
# 导入你提供的 fu_crud 核心函数
from common.fu_crud import create, update, delete, retrieve, get_or_none

router = Router(tags=["竞赛管理"])


def ensure_contest_owner(request, contest: Contest) -> Contest:
    if request.auth.is_superuser or str(contest.creator_id) == str(request.auth.id):
        return contest
    raise HttpError(403, "只有创建者可以管理此竞赛")


def validate_contest_payload(data: ContestIn | ContestUpdteIn):
    start_time = getattr(data, 'contest_start_time', None)
    end_time = getattr(data, 'contest_end_time', None)
    is_public = getattr(data, 'is_public', None)
    allowed_group_ids = getattr(data, 'allowed_group_ids', None)

    if start_time and end_time and start_time >= end_time:
        raise HttpError(400, "比赛结束时间必须晚于开始时间")

    if is_public is False and allowed_group_ids is not None and len(allowed_group_ids) == 0:
        raise HttpError(400, "私有比赛至少需要绑定一个用户组")


def annotate_contest_status(contest: Contest) -> Contest:
    now = timezone.now()
    if contest.contest_start_time and now < contest.contest_start_time:
        contest.status = "pending"
    elif contest.contest_end_time and now > contest.contest_end_time:
        contest.status = "finished"
    else:
        contest.status = "running"
    return contest

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
    query_set = UserGroup.objects.annotate(member_count=Count('members'),creator_name=F('creator__name')).prefetch_related('members')
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
def remove_group_members(request, id: str, data: GroupDeleteMembersIn):
    """
    移除用户组成员
    """
    instance = get_object_or_404(UserGroup, id=id)

    if str(instance.creator_id) != str(request.auth.id):
        raise HttpError(403, "只有创建者可以移除成员")

    if str(data.user_id) == request.auth.id:
        raise HttpError(403, "不可删除自己")
    # 执行移除
    instance.members.remove(data.user_id)

    # return 实例
    return instance

# ================= 竞赛管理 (Contest) =================

@router.post("/contests", response=ContestOut, summary="创建竞赛")
def create_contest(request, data: ContestIn):
    validate_contest_payload(data)
    payload = data.dict(exclude={'allowed_group_ids'})
    
    with transaction.atomic():
        instance = Contest.objects.create(
            **payload,
            creator=request.auth
        )
        
        if data.allowed_group_ids:
            instance.allowed_groups.set(data.allowed_group_ids)
            
    return instance

@router.get("/contests", response=List[ContestListOut], summary="获取竞赛列表")
def list_contests(
    request,
    filters: ContestFilter = Query(...),
    is_public: Optional[bool] = None,
    status: Optional[str] = None,
):
    user = request.auth
    qs = Contest.objects.select_related('creator').all()

    if not user.is_superuser:
        qs = qs.filter(
            Q(is_public=True) | Q(creator=user) | Q(allowed_groups__members=user)
        ).distinct()

    if filters.title:
        qs = qs.filter(title__icontains=filters.title)

    if is_public is not None:
        qs = qs.filter(is_public=is_public)

    now = timezone.now()
    if status == "pending":
        qs = qs.filter(contest_start_time__gt=now)
    elif status == "running":
        qs = qs.filter(contest_start_time__lte=now, contest_end_time__gte=now)
    elif status == "finished":
        qs = qs.filter(contest_end_time__lt=now)

    for item in qs:
        item.creator_name = item.creator.username if item.creator else "未知"
        annotate_contest_status(item)
        
    return qs

# @router.get("/contests/{id}", response=ContestDetailOut, summary="获取竞赛详情")
# def get_contest_detail(request, id: str):
#     instance = get_or_none(Contest, id=id)
#     if not instance:
#         raise HttpError(404, "竞赛不存在")
    
#     instance.creator_name = instance.creator.username
#     instance.problems = list(instance.contest_problem.select_related('problem').all())
#     # 补全关联题目中 Schema 需要的 title
#     for cp in instance.problems:
#         cp.title = cp.problem.title
        
#     instance.virtual_problems = list(instance.virtual_problems.all())
    
#     return instance

@router.patch("/contests/{id}", response=ContestOut, summary="更新竞赛")
def update_contest(request, id: str, data: ContestUpdteIn):
    instance = get_object_or_404(Contest, id=id)
    ensure_contest_owner(request, instance)
    validate_contest_payload(data)
    
    update_data = data.dict(exclude={'allowed_group_ids'}, exclude_unset=True)
    
    allowed_group_ids = data.allowed_group_ids
    
    with transaction.atomic():
        for attr, value in update_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        
        if allowed_group_ids is not None:
            instance.allowed_groups.set(allowed_group_ids)
            
    return instance

@router.delete("/contests/{id}", response=ContestOut, summary="删除竞赛")
def delete_contest(request, id: str):
    instance = get_object_or_404(Contest, id=id)
    ensure_contest_owner(request, instance)

    return delete(id, Contest)

# ================= 虚拟题目管理 (VirtualProblem) =================

@router.get("/contests-vp/{id}", response=ContestDetailOutWithVp)
def get_contest_detail(request, id: UUID):
    # 预加载虚拟题目及其关联的真实题目，提升性能
    contest = get_object_or_404(
        Contest.objects.select_related('creator').prefetch_related('virtual_problems__real_problem'), 
        id=id
    )
    
    step_fields = [
        'step_title_done', 'step_limit_done', 'step_description_done',
        'step_input_description_done', 'step_output_description_done',
        'step_example_done', 'step_hint_done', 'step_testcase_done', 'step_solution_done'
    ]

    vp_list = []
    # 遍历所有虚拟题目
    for vp in contest.virtual_problems.all().order_by('order'):
        data = {
            "id": vp.id,
            "name": vp.name,
            "description": vp.description,
            "order": vp.order,
            "color": vp.color,
            "is_bound": vp.is_bound,
        }
        
        if vp.real_problem:
            rp = vp.real_problem
            data["real_problem_id"] = rp.id
            data["real_problem_title"] = rp.title
            # 填充进度
            for field in step_fields:
                data[field] = getattr(rp, field)
        else:
            # 未绑定时进度全为 0
            for field in step_fields:
                data[field] = 0
        vp_list.append(data)

    return {
        "id": contest.id,
        "title": contest.title,
        "description": contest.description,
        "contest_start_time": contest.contest_start_time,
        "contest_end_time": contest.contest_end_time,
        "is_public": contest.is_public,
        "creator_name": contest.creator.username,
        "virtual_problems": vp_list
    }

@router.post("/contests/{id}/virtual-problems", response=VirtualProblemOut)
def create_virtual_problem(request, id: UUID, data: VirtualProblemIn):
    contest = get_object_or_404(Contest, id=id)
    ensure_contest_owner(request, contest)
    vp = VirtualProblem.objects.create(
        contest=contest,
        author=request.auth,
        **data.dict()
    )
    return vp

@router.patch("/virtual-problems/{id}", response=VirtualProblemOut)
def update_virtual_problem(request, id: UUID, data: VirtualProblemIn):
    instance = get_object_or_404(VirtualProblem, id=id)
    ensure_contest_owner(request, instance.contest)
    for attr, value in data.dict(exclude_unset=True).items():
        setattr(instance, attr, value)
    instance.save()
    return instance

@router.patch("/virtual-problems/{id}/bind", response=VirtualProblemOut)
def bind_virtual_problem(request, id: UUID, data: VirtualProblemBindIn):
    instance = get_object_or_404(VirtualProblem, id=id)
    ensure_contest_owner(request, instance.contest)
    real_p = get_object_or_404(Problem, id=data.real_problem_id)
    instance.real_problem = real_p
    instance.is_bound = True
    instance.save()
    return instance

@router.delete("/virtual-problems/{id}",response=VirtualProblemOut)
def delete_virtual_problem(request, id: UUID):
    instance = get_object_or_404(VirtualProblem, id=id)
    ensure_contest_owner(request, instance.contest)
    instance.delete()
    return instance

@router.get("/allUser/", response=List[UserSchemaAvatarOut], summary="获取所有用户头像信息")
def get_all_users_avatars(request):
    """
    返回系统中所有用户的 ID、用户名和头像
    """
    # 建议只取需要的字段，优化性能
    users = User.objects.all().only('id', 'name', 'avatar')
    return users
