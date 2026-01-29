from django.db import transaction
from django.db.models import Q  # 必须导入 Q 对象
from django.shortcuts import get_object_or_404
from ninja import Router, File, Form
import os
import zipfile
import tempfile
from ninja.files import UploadedFile
from core.file_manager.file_manager_model import FileManager
from core.file_manager.storage_backends import get_storage_backend
from django.http import FileResponse, HttpResponse
from typing import List
import re
from common.fu_crud import create, retrieve, delete, batch_delete
from .models import Tag, Problem, Example, Solution
from .schemas import ProblemCreateIn, ProblemListOut, ProblemDetailOut, TagOut, SolutionOut, SolutionIn, TestCaseOut, TestCase, TagIn,ProblemUpdateIn,ProblemStatusUpdate
from core.file_manager.file_manager_services import save_file_to_manager
from core.user.user_model import User
from typing import List, Optional
from uuid import UUID
from urllib.parse import quote

router = Router(tags=["Problems"])


@router.post("/", response=ProblemDetailOut)
def create_problem(request, payload: ProblemCreateIn):
    data = payload.dict()
    tags = data.pop('tags', [])
    examples_data = data.pop('examples', [])

    # 保证 Problem 和 Example 同时成功
    with transaction.atomic():
        problem = Problem.objects.create(problem_setter=request.auth, **data)

        if tags:
            problem.tags.set(Tag.objects.filter(id__in=tags))

        if examples_data:
            Example.objects.bulk_create([
                Example(problem=problem, **ex) for ex in examples_data
            ])
    return problem

@router.patch("/{problem_id}",response=ProblemDetailOut)
def update_problem(
    request,
    problem_id: UUID,
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

@router.delete("/{problem_id}",response=ProblemDetailOut)
def delete_problem(request,problem_id:UUID):
    problem = get_object_or_404(Problem,id=problem_id)
    return delete(problem_id,Problem)

@router.get('/{problem_id}/status',response=ProblemStatusUpdate)
def getProblemStatus(request,problem_id:UUID):
    problem=get_object_or_404(Problem,id=problem_id)
    return problem

@router.patch('/{problem_id}/status',response=ProblemStatusUpdate)
def getProblemStatus(request,problem_id:UUID ,data:ProblemStatusUpdate):
    problem=get_object_or_404(Problem,id=problem_id)
    update_data = data.dict(exclude_unset=True)
    for attr,value in update_data.items():
        setattr(problem,attr,value)
    return problem


@router.get("/", response=List[ProblemListOut])
def list_problems(request, keyword: Optional[str] = None):
    # 预加载标签并按时间排序
    queryset = Problem.objects.prefetch_related('tags').order_by('-created_at')

    # 权限过滤逻辑
    if request.auth.USER_TYPE_CHOICES not in [0, 1]:
        queryset = queryset.filter(
            Q(is_public=True) | Q(problem_setter=request.auth)
        )

    # 关键词搜索逻辑
    if keyword:
        queryset = queryset.filter(
            Q(title__icontains=keyword)           # 标题包含关键词（不区分大小写）
        )
    return queryset

@router.get("/{problem_id}",response=ProblemDetailOut)
def getProblemDetail(request,problem_id:UUID):
    
    print(request.auth.user_type)

    if request.auth.user_type == 0 or request.auth.user_type == 1 :
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
def deleteTag(request,tag_id:UUID):
    return delete(tag_id,Tag)

@router.get("/{problem_id}/testcases", response=List[TestCaseOut])
def list_testcases(request, problem_id: UUID):
    # 确认题目是否存在
    problem = get_object_or_404(Problem, id=problem_id)

    # 获取该题目下的所有测试用例
    testcases = TestCase.objects.filter(problem=problem)

    return testcases



@router.get("/{problem_id}/testcases/zip")
def download_testcases(request, problem_id: UUID):
    """打包并下载指定题目的所有测试点为 zip 文件"""
    problem = get_object_or_404(Problem, id=problem_id)

    # 权限校验：管理员或出题者可以下载
    # try:
    #     user_type = request.auth.user_type
    # except Exception:
    #     user_type = None

    # if user_type not in (0, 1) and problem.problem_setter != request.auth:
    #     return HttpResponse('Forbidden', status=403)

    testcases = TestCase.objects.filter(problem=problem)
    if not testcases.exists():
        return HttpResponse('No testcases found', status=404)

    storage = get_storage_backend()

    # 创建临时文件用于写入 zip
    tmp_file = tempfile.NamedTemporaryFile(suffix='.zip', delete=False)
    tmp_name = tmp_file.name
    tmp_file.close()

    try:
        with zipfile.ZipFile(tmp_name, 'w', zipfile.ZIP_DEFLATED) as zf:
            for tc in testcases:
                # 每个测试点包含 input 和 output
                for kind, file_field, fname in (
                    ('in', tc.input_file, tc.input_filename),
                    ('out', tc.output_file, tc.output_filename),
                ):
                    if not file_field:
                        continue
                    try:
                        fm = FileManager.objects.get(id=UUID(str(file_field)))
                    except Exception:
                        continue

                    arcname = f"{(fname or os.path.basename(fm.storage_path))}"

                    try:
                        if fm.storage_type == 'local':
                            full_path = os.path.join(storage.base_path, fm.storage_path)
                            if os.path.exists(full_path):
                                zf.write(full_path, arcname)
                        elif hasattr(storage, 'get_file_content'):
                            # 读取远端存储内容并写入 zip
                            file_stream = storage.get_file_content(fm.storage_path)
                            # file_stream 可能是 file-like 或包含 .data
                            try:
                                data = file_stream.read()
                            except Exception:
                                data = getattr(file_stream, 'data', None)
                            if data is not None:
                                zf.writestr(arcname, data)
                        else:
                            # 无法直接访问的存储类型，跳过
                            continue
                    except Exception:
                        # 单个文件打包失败不影响其他文件
                        continue


        zip_name = f"{problem.title}.zip"

        response = FileResponse(
            open(tmp_name, 'rb'),
            as_attachment=True,
        )
        response['Content-Disposition'] = (
            f"attachment; filename*=UTF-8''{quote(zip_name)}"
        )
        return response
    finally:
        try:
            os.remove(tmp_name)
        except Exception:
            pass


@router.delete("/testcase/{testcase_id}",response=TestCaseOut)
def delete_testcase(request, testcase_id: UUID):
    # 找到对应的测试点
    testcase = get_object_or_404(TestCase, id=testcase_id)

    # 执行删除

    return delete(testcase.id,TestCase)

@router.get('/{problem_id}/solutions',response=List[SolutionOut])
def getSolutions(request,problem_id:UUID):
    user=request.auth
    problem = get_object_or_404(Problem,id=problem_id)
    solution = problem.solutions.all()
    return solution

@router.post("/{problem_id}/solutions", response=SolutionOut)
def create_solution(request, problem_id: UUID, payload: SolutionIn):
    problem = get_object_or_404(Problem, id=problem_id)
    solution = Solution.objects.create(
        problem=problem,
        user=request.auth,
        **payload.dict()
    )
    return solution

@router.delete('solution/{solution_id}',response=SolutionOut)
def delete_solution(request,solution_id:UUID):
    solution = get_object_or_404(Solution,id=solution_id)
    return delete(solution_id,Solution)

@router.post("/{problem_id}/testcase", response=TestCaseOut)
def upload_testcase(
    request,
    problem_id: UUID,
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