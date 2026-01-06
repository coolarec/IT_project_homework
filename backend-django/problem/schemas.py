from typing import List, Optional
from ninja import Schema, ModelSchema
from .models import Tag, Problem, Example, TestCase, Solution
from uuid import UUID

# --- Tag ---


class TagOut(ModelSchema):
    class Config:
        model = Tag
        model_fields = ['id', 'name']


class TagIn(ModelSchema):
    class Config:
        model = Tag
        model_fields = ['name']

# --- Example ---


class ExampleSchema(Schema):
    input_data: str
    output_data: str

# --- Problem ---


class ProblemListOut(ModelSchema):
    tags: List[TagOut]
    class Config:
        model = Problem
        model_fields = ['id','title', 'difficulty', 'is_public', 'created_at']


class ProblemDetailOut(ModelSchema):
    tags: List[TagOut]
    examples: List[ExampleSchema] = []

    class Config:
        model = Problem
        model_fields = "__all__"


class ProblemCreateIn(Schema):
    title: str
    description: str
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    analysis: Optional[str] = None
    difficulty: int = 3
    is_public: bool = True
    time_limit: int
    memory_limit: int
    tags: List[UUID] = []
    examples: List[ExampleSchema] = []  # 支持创建时直接传入样例
    step_title_done: int = 0
    step_limit_done: int = 0
    step_description_done: int = 0
    step_input_description_done: int = 0
    step_output_description_done: int = 0
    step_example_done: int = 0
    step_hint_done: int = 0
    step_testcase_done: int = 0
    step_solution_done: int = 0


class ProblemUpdateIn(Schema):
    title: Optional[str] = None
    description: Optional[str] = None
    input_description: Optional[str] = None
    output_description: Optional[str] = None
    analysis: Optional[str] = None
    difficulty: Optional[int] = None
    is_public: Optional[bool] = None
    time_limit: Optional[int] = None
    memory_limit: Optional[int] = None
    tags: Optional[List[UUID]] = None
    examples: Optional[List[ExampleSchema]] = None
    step_title_done: Optional[int] = None
    step_description_done: Optional[int] = None
    step_limit_done: Optional[int] = None
    step_input_description_done: Optional[int] = None
    step_output_description_done: Optional[int] = None
    step_example_done: Optional[int] = None
    step_hint_done: Optional[int] = None
    step_testcase_done: Optional[int] = None
    step_solution_done: Optional[int] = None


# --- Problem_Status(管理每道题的设计进程) ---
class ProblemStatusUpdate(Schema):
    step_title_done: Optional[int] = None
    step_limit_done: Optional[int] = None
    step_description_done: Optional[int] = None
    step_input_description_done: Optional[int] = None
    step_output_description_done: Optional[int] = None
    step_example_done: Optional[int] = None
    step_hint_done: Optional[int] = None
    step_testcase_done: Optional[int] = None
    step_solution_done: Optional[int] = None


# --- TestCase & Solution (保留原有) ---
class TestCaseOut(ModelSchema):
    class Config:
        model = TestCase
        model_fields = "__all__"


class SolutionOut(ModelSchema):
    user_name: str = None

    class Config:
        model = Solution
        model_fields = ['id', 'language', 'code', 'description', 'created_at']

    @staticmethod
    def resolve_user_name(obj):
        return obj.user.username


class SolutionIn(Schema):
    language: str
    code: str
    description: Optional[str] = None
