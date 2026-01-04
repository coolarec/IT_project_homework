from django.db import models
from core.user.user_model import User
from problem.models import Problem
# Create your models here.


class Contest(models):
    STATUS_CHOICES = (
        (0, '未开始'),
        (1, '报名中'),
        (2, '进行中'),
        (3, '已结束'),
    )

    title = models.CharField(max_length=200)
    prepare_start_time = models.DateField()
    prepare_end_time = models.DateField()
    contest_start_time = models.DateField()
    contest_end_time = models.DateField()
    notice = models.TextField(blank=True)
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    is_public = models.BooleanField(default=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_contests'
    )
    freeze_time = models.IntegerField(default=0)

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

# 
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