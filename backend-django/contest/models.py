from django.db import models
from core.user.user_model import User
from problem.models import Problem
from core.dept.dept_model import Dept
# Create your models here.
import uuid

class UserGroup(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, help_text="用户组名称")
    description = models.TextField(blank=True, null=True, help_text="用户组描述")
    a=models.CharField(max_length=10,default="==")
    # 创建者
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='owned_groups',
        help_text="创建者"
    )

    # 组成员（多对多）
    members = models.ManyToManyField(
        User,
        related_name='user_groups',
        blank=True,
        help_text="组成员"
    )

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "用户组"
        verbose_name_plural = verbose_name
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class Contest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    STATUS_CHOICES = (
        (0, '未开始'),
        (1, '报名中'),
        (2, '进行中'),
        (3, '已结束'),
    )
    PRIVATE_PERMISSION = (
        (0, '仅个人可见'),
        (2, '指定用户组可见'),
        (3, '全体可见'),
    )
    title = models.CharField(max_length=200)
    prepare_start_time = models.DateField()
    prepare_end_time = models.DateField()
    contest_start_time = models.DateField()
    contest_end_time = models.DateField()
    notice = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    allowed_groups = models.ManyToManyField(
        UserGroup,
        blank=True,
        related_name='contests',
        help_text="允许参加的用户组（当权限为指定用户组可见时生效）"
    )
    privite_permission = models.IntegerField(choices=PRIVATE_PERMISSION, default=0)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_contests'
    )
    freeze_time = models.IntegerField(default=0)
    dept = models.ForeignKey(
        Dept,
        on_delete=models.CASCADE,
        related_name='created_contests',
        null=True
    )

# 虚拟问题
class VirtualProblem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100,default='')
    contest = models.OneToOneField(
        Contest,
        null=True,
        on_delete=models.CASCADE,
        related_name='virtual_problems'
    )
    description = models.CharField(max_length=200)
    author = models.ForeignKey(
        User,
        null=True,
        on_delete=models.CASCADE,
        related_name='virtual_problems'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    real_problem = models.OneToOneField(
        Problem,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='virtual'
    )
    order = models.IntegerField(default=0)
    color = models.CharField(max_length=50,default='')

    def __str__(self):
        return self.description
