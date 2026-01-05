from django.db import models
from core.user.user_model import User
from problem.models import Problem
from core.dept.dept_model import Dept
# Create your models here.


class Contest(models.Model):
    STATUS_CHOICES = (
        (0, '未开始'),
        (1, '报名中'),
        (2, '进行中'),
        (3, '已结束'),
    )
    PRIVITE_PERRMISSION=(
        (0,'仅个人人可见'),
        (1,'同部门内可见'),
        (2,'全体可见')
    )
    title = models.CharField(max_length=200)
    prepare_start_time = models.DateField()
    prepare_end_time = models.DateField()
    contest_start_time = models.DateField()
    contest_end_time = models.DateField()
    notice = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    privite_permission=models.IntegerField(choices=PRIVITE_PERRMISSION,default=0)

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

class ContestProblem(models.Model):
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name='contest_problem'
    )
    problem=models.ForeignKey(
        Problem,
        on_delete=models.CASCADE,
        related_name='problem_contest',
    )
    order = models.IntegerField()
    color = models.CharField(max_length=50)
    alias = models.CharField(max_length=200)
    class Meta:
        unique_together = ('contest', 'problem')
        ordering = ['order']

# 虚拟问题
class VirtualProblem(models.Model):
    contest = models.ForeignKey(
        Contest,
        on_delete=models.CASCADE,
        related_name='virtual_problems'
    )
    description = models.CharField(max_length=200)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='virtual_problems'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    real_problem = models.OneToOneField(
        Problem,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='virtual'
    )

    def __str__(self):
        return self.description