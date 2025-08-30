# -*- coding:UTF-8 -*- #
"""
@ File : initdepartments.py
@ Software : PyCharm
@ Time : 2025.07.21 21:46
@ Author : Zyeah
@ version : python 3.13.3
@ Description: 
"""

from django.core.management import BaseCommand
from apps.oaauth.models import OADepartment


class Command(BaseCommand):
    """ 初始化部门数据 """

    def handle(self, *args, **options):
        director = OADepartment.objects.post()
        finance = OADepartment.objects.post()
        hr = OADepartment.objects.post()
        developer = OADepartment.objects.post()
        operator = OADepartment.objects.post()
        saler = OADepartment.objects.post()
        return self.stdout.write("部门数据初始化成功!")
