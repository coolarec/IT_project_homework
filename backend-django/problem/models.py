from django.db import models
from core.user.user_model import User
import uuid

class Tag(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=50, unique=True)
    def __str__(self): return self.name

class Problem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    DIFFICULTY_CHOICES = [(i, f"{i}星") for i in range(1, 6)]
    
    title = models.CharField(max_length=200)
    description = models.TextField()
    input_description = models.TextField(blank=True, null=True)
    output_description = models.TextField(blank=True, null=True)
    analysis = models.TextField(blank=True, null=True)
    difficulty = models.IntegerField(choices=DIFFICULTY_CHOICES, default=3)
    is_public = models.BooleanField(default=True)
    time_limit = models.IntegerField()
    memory_limit = models.IntegerField()
    tags = models.ManyToManyField(Tag, blank=True, related_name="problems")
    problem_setter = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    STEP_CHOICES = (
        (0,"未开始"),
        (1,"进行中"),
        (2,"已完成")
    )
    
    # ===== 出题步骤完成状态 =====
    step_title_done = models.IntegerField(choices=STEP_CHOICES,default=0)               # 标题完成成状态
    step_limit_done = models.IntegerField(choices=STEP_CHOICES,default=0)               # 题解测试样例完成状态
    step_description_done = models.IntegerField(choices=STEP_CHOICES,default=0)         # 题目描述完成状态
    step_input_description_done = models.IntegerField(choices=STEP_CHOICES,default=0)   # 输入描述完成状态
    step_output_description_done = models.IntegerField(choices=STEP_CHOICES,default=0)  # 输出描述完成状态
    step_example_done = models.IntegerField(choices=STEP_CHOICES,default=0)             # 测试样例完成状态
    step_hint_done = models.IntegerField(choices=STEP_CHOICES,default=0)                # 提示完成状态
    step_testcase_done = models.IntegerField(choices=STEP_CHOICES,default=0)            # 后台测试样例完成状态
    step_solution_done = models.IntegerField(choices=STEP_CHOICES,default=0)            # 题解测试样例完成状态


class Example(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="examples")
    input_data = models.TextField()
    output_data = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

class TestCase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="test_cases")
    size=models.IntegerField()
    input_filename = models.CharField(
        max_length=40,
        null=False,
    )
    output_filename = models.CharField(
        max_length=40,
        null=False
    )
    input_file = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        help_text="输入文件UUID",
    )
    output_file = models.CharField(
        max_length=36,
        null=True,
        blank=True,
        help_text="输出文件UUID",
    )
    weight = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

class Solution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    problem = models.ForeignKey(Problem, on_delete=models.CASCADE, related_name="solutions")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    code = models.TextField()
    language = models.CharField(max_length=50, default="Python")
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)