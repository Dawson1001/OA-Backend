from django.contrib.auth import get_user_model
from django.db import models

# Create your models here.


OAUser = get_user_model()


class AbsentStatusChoices(models.IntegerChoices):
    """ 假期状态 """
    AUDITING = 1  # 审核中
    APPROVAL = 2  # 批准
    REJECT = 3  # 拒绝


class AbsentType(models.Model):
    """ 请假类型 """
    name = models.CharField(max_length=100)
    create_time = models.DateTimeField(auto_now_add=True)


class Absence(models.Model):
    """ 请假实例模型 """

    # 标题
    title = models.CharField(max_length=100)

    # 请假内容
    absence_content = models.TextField()

    # 请假类型
    absent_type = models.ForeignKey(AbsentType, on_delete=models.CASCADE,
                                    related_name='absents', related_query_name='absents')

    # 发起人
    requester = models.ForeignKey(OAUser, on_delete=models.CASCADE,
                                  related_name='my_absents', related_query_name='my_absents')

    # 审批人
    responder = models.ForeignKey(OAUser, on_delete=models.CASCADE, null=True,
                                  related_name='sub_absents', related_query_name='sub_absents')

    # 假期状态
    status = models.IntegerField(choices=AbsentStatusChoices, default=AbsentStatusChoices.AUDITING)

    # 假期开始时间
    start_time = models.DateTimeField()

    # 假期结束时间
    end_time = models.DateTimeField()

    # 审批人回复
    responder_content = models.TextField(blank=True)

    # 发起时间
    create_time = models.DateTimeField(auto_now_add=True)
