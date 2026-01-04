from django.db import transaction
from django.db.models import Q  # 必须导入 Q 对象
from django.shortcuts import get_object_or_404
from ninja import Router, File, Form
import os
from ninja.files import UploadedFile
from core.file_manager.file_manager_model import FileManager
from typing import List
from common.fu_crud import create, retrieve, delete, batch_delete
from .models import Tag, Problem, Example, Solution
from .schemas import ProblemCreateIn, ProblemListOut, ProblemDetailOut, TagOut, SolutionOut, SolutionIn, TestCaseOut, TestCase, TagIn,ProblemUpdateIn,ProblemStatusUpdate
from core.file_manager.file_manager_services import save_file_to_manager
from core.user.user_model import User
from typing import List, Optional


router = Router(tags=["Problems"])


@router.post("/", response=ProblemDetailOut)
def create_problem(request, payload: ProblemCreateIn):
    data = payload.dict()
    tags = data.pop('tags', [])
    examples_data = data.pop('examples', [])

    # 使用事务保证 Problem 和 Example 同时成功
    with transaction.atomic():
        problem = Problem.objects.create(problem_setter=request.auth, **data)

        if tags:
            problem.tags.set(Tag.objects.filter(id__in=tags))

        if examples_data:
            Example.objects.bulk_create([
                Example(problem=problem, **ex) for ex in examples_data
            ])
    problem.step_description_done=0
    return problem

@router.patch("/{problem_id}",response=ProblemDetailOut)
def update_problem(
    request,
    problem_id: int,
    payload: ProblemUpdateIn,
):
    problem = get_object_or_404(Problem, id=problem_id)

    data = payload.dict(exclude_unset=True)

    #  普通字段
    for field, value in data.items():
        print()
        if field not in ("tags", "examples"):
            setattr(problem, field, value)
    problem.save()

    problem.tags.clear()
    #  多对多：标签
    if "tags" in data:
        problem.tags.set(data["tags"])

    #  一对多：样例（全量替换）
    if "examples" in data:
        problem.examples.all().delete()
        Example.objects.bulk_create(
            [
                Example(problem=problem, **ex)
                for ex in data["examples"]
            ]
        )
    problem.save()
    return problem

@router.get('/{problem_id}/status',response=ProblemStatusUpdate)
def getProblemStatus(request,problemId:int):
    problem=get_object_or_404(Problem,id=problemId)
    return problem

@router.patch('/{problem_id}/status',response=ProblemStatusUpdate)
def getProblemStatus(request,problem_id:int,data:ProblemStatusUpdate):
    problem=get_object_or_404(Problem,id=problem_id)
    update_data = data.dict(exclude_unset=True)
    for attr,value in update_data.items():
        setattr(problem,attr,value)
    return problem


@router.get("/", response=List[ProblemListOut])
def list_problems(request, keyword: Optional[str] = None):
    # 1. 预加载标签并按时间排序
    queryset = Problem.objects.prefetch_related('tags').order_by('-created_at')

    # 2. 权限过滤逻辑
    if request.auth.USER_TYPE_CHOICES not in [0, 1]:
        queryset = queryset.filter(
            Q(is_public=True) | Q(problem_setter=request.auth)
        )

    # 3. 关键词搜索逻辑
    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword)           # 标题包含关键词（不区分大小写）
        )

    return queryset

@router.get("/{problem_id}",response=ProblemDetailOut)
def getProblemDetail(request,problem_id:int):
    if request.auth.USER_TYPE_CHOICES == 0 or request.auth.USER_TYPE_CHOICES == 1 :
        return get_object_or_404(Problem,id=problem_id)
    return get_object_or_404(
        Problem,
        id=problem_id,
        problem_setter=request.auth
    )

@router.get("/tags/all", response=List[TagOut])
def list_tags(request):
    return Tag.objects.all()


@router.post("/tag/",response=TagOut)
def createTag(request,payload:TagIn):
    data = payload.dict()
    return Tag.objects.create(**data)

@router.delete("/tag/{tag_id}",response=TagOut)
def deleteTag(request,tag_id:int):
    return delete(tag_id,Tag)

@router.get("/{problem_id}/testcases", response=List[TestCaseOut])
def list_testcases(request, problem_id: int):
    # 确认题目是否存在
    problem = get_object_or_404(Problem, id=problem_id)

    # 获取该题目下的所有测试用例
    testcases = TestCase.objects.filter(problem=problem)

    return testcases


@router.delete("/testcase/{testcase_id}",response=TestCaseOut)
def delete_testcase(request, testcase_id: int):
    # 找到对应的测试点
    testcase = get_object_or_404(TestCase, id=testcase_id)

    # 执行删除
    # 注意：TestCase 如果有 FileField，数据库记录删了，但物理文件默认还会留在硬盘上
    # 如果需要删掉物理文件，建议在 delete() 之前处理，或者使用信号(signals)

    return delete(testcase.id,TestCase)

@router.get('/{problem_id}/solutions',response=List[SolutionOut])
def getSolutions(request,problem_id:int):
    user=request.auth
    problem = get_object_or_404(Problem,id=problem_id)
    solution = problem.solutions.all()
    return solution

@router.post("/{problem_id}/solutions", response=SolutionOut)
def create_solution(request, problem_id: int, payload: SolutionIn):
    problem = get_object_or_404(Problem, id=problem_id)
    solution = Solution.objects.create(
        problem=problem,
        user=request.auth,  # 确保已登录
        **payload.dict()
    )
    return solution

@router.delete('solution/{solution_id}',response=SolutionOut)
def delete_solution(request,solution_id:int):
    solution = get_object_or_404(Solution,id=solution_id)
    return delete(solution_id,Solution)

@router.post("/{problem_id}/testcase", response=TestCaseOut)
def upload_testcase(
    request,
    problem_id: int,
    input_file: UploadedFile = File(...),
    output_file: UploadedFile = File(...),
    weight: int = Form(1)
):
    # 1. 获取题目
    problem = get_object_or_404(Problem, id=problem_id)

    with transaction.atomic():
        # 2. 自动维护目录结构: testcases -> {problem_id}
        # 获取或创建根目录 'testcases'
        root_dir, _ = FileManager.objects.get_or_create(
            name="testcases",
            parent=None,
            type='folder',
            defaults={'path': 'testcases', 'sys_creator_id': request.auth.id}
        )

        # 获取或创建题目目录 str(problem_id)
        problem_dir_path = f"testcases/{problem_id}"
        problem_dir, _ = FileManager.objects.get_or_create(
            name=str(problem_id),
            parent=root_dir,
            type='folder',
            defaults={'path': problem_dir_path,
                      'sys_creator_id': request.auth.id}
        )
        size = 0
        # 3. 调用公共 Service 保存输入文件
        in_file_obj = save_file_to_manager(
            file=input_file,
            user_id=request.auth.id,
            parent=problem_dir
        )

        # 4. 调用公共 Service 保存输出文件
        out_file_obj = save_file_to_manager(
            file=output_file,
            user_id=request.auth.id,
            parent=problem_dir
        )
        size = in_file_obj.size+out_file_obj.size
        # 5. 创建 TestCase 记录，引用文件管理系统的 UUID (id)
        testcase = TestCase.objects.create(
            problem=problem,
            input_filename=input_file.name,
            output_filename=output_file.name,
            input_file=str(in_file_obj.id),  # 存入 UUID 字符串
            output_file=str(out_file_obj.id),     # 存入 UUID 字符串
            weight=weight,
            size=size
        )

    return testcase