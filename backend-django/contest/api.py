from ninja import Router
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Contest, ContestProblem, VirtualProblem
from problem.models import Problem
from .schemas import (
    ContestIn, ContestOut, ContestDetailOut,
    ContestProblemIn, ContestProblemOut,
    VirtualProblemIn, VirtualProblemOut,
    VirtualProblemBindIn,
)

router = Router(tags=["Contest"])

# 创建比赛（同时生成虚拟题）
@router.post("/", response=ContestOut)
def create_contest(request, payload: ContestIn):
    contest = Contest.objects.create(
        **payload.dict(),
        creator=request.user
    )

    # 创建一个默认虚拟题（占位）
    VirtualProblem.objects.create(
        contest=contest,
        description="未命名题目",
        author=request.user
    )

    return contest

# 比赛列表
@router.get("/", response=list[ContestOut])
def list_contests(request):
    return Contest.objects.all()

# 比赛详情（真实题 + 虚拟题）
@router.get("/{contest_id}", response=ContestDetailOut)
def contest_detail(request, contest_id: int):
    contest = get_object_or_404(Contest, id=contest_id)

    return {
        **contest.__dict__,
        "problems": contest.contest_problem.all(),
        "virtual_problems": contest.virtual_problems.all(),
    }

# 比赛题目（真实 Problem）
# 添加题目到比赛
@router.post("/{contest_id}/problems", response=ContestProblemOut)
def add_problem_to_contest(
    request,
    contest_id: int,
    payload: ContestProblemIn
):
    contest = get_object_or_404(Contest, id=contest_id)
    problem = get_object_or_404(Problem, id=payload.problem_id)

    obj = ContestProblem.objects.create(
        contest=contest,
        problem=problem,
        order=payload.order,
        color=payload.color,
        alias=payload.alias,
    )

    return obj

# 删除比赛题目
@router.delete("/{contest_id}/problems/{problem_id}")
def remove_problem_from_contest(request, contest_id: int, problem_id: int):
    ContestProblem.objects.filter(
        contest_id=contest_id,
        problem_id=problem_id
    ).delete()
    return {"success": True}

# 虚拟题接口
# 创建虚拟题（比赛编辑页用）
@router.post("/{contest_id}/virtual-problems", response=VirtualProblemOut)
def create_virtual_problem(
    request,
    contest_id: int,
    payload: VirtualProblemIn
):
    contest = get_object_or_404(Contest, id=contest_id)

    return VirtualProblem.objects.create(
        contest=contest,
        description=payload.description,
        author=request.user
    )

# 虚拟题目列表
@router.get("/{contest_id}/virtual-problems", response=list[VirtualProblemOut])
def list_virtual_problems(request, contest_id: int):
    return VirtualProblem.objects.filter(contest_id=contest_id)

# 虚拟题目转正
@router.post("/virtual-problems/{virtual_id}/bind")
def bind_virtual_problem(
    request,
    virtual_id: int,
    payload: VirtualProblemBindIn
):
    vp = get_object_or_404(VirtualProblem, id=virtual_id)
    problem = get_object_or_404(Problem, id=payload.real_problem_id)

    vp.real_problem = problem
    vp.save()

    return {"success": True}

# 删除虚拟题
@router.delete("/virtual-problems/{virtual_id}")
def delete_virtual_problem(request, virtual_id: int):
    VirtualProblem.objects.filter(id=virtual_id).delete()
    return {"success": True}
