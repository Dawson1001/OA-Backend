from django.db import models
from apps.oaauth.models import OAUser, OADepartment


# Create your models here.

class Inform(models.Model):
    """ 消息通知模型 """
    title = models.CharField(max_length=100)
    content = models.TextField()
    author = models.ForeignKey(OAUser, on_delete=models.CASCADE,
                               related_name='informs', related_query_name='informs')
    create_time = models.DateTimeField(auto_now_add=True)
    # public 通过序列化时的 departments_ids 列表中只用含 '0' 进行判别
    public = models.BooleanField(default=False)
    departments = models.ManyToManyField(OADepartment, related_name='informs', related_query_name='informs')

    class Meta:
        ordering = ['-create_time']


class InformRead(models.Model):
    """ 通知被阅模型: 用于记录某条通知哪些人已阅 """
    inform = models.ForeignKey(Inform, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    reader = models.ForeignKey(OAUser, on_delete=models.CASCADE, related_name='reads', related_query_name='reads')
    read_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('inform', 'reader')
