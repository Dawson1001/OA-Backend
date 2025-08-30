# -*- coding:UTF-8 -*- #
"""
@ File : initabsenttype.py
@ Software : PyCharm
@ Time : 2025.07.31 15:52
@ Author : Zyeah
@ version : python 3.13.3
@ Description: 
"""
from django.core.management import BaseCommand
from apps.attendance.models import AbsentType


class Command(BaseCommand):
    def handle(self, *args, **options):
        absent_types = ["事假", "病假", "工伤假", "婚假", "丧假", "产假", "探亲假", "公假", "年休假"]
        absent_type_list = []

        for absent_type in absent_types:
            absent_type_list.append(AbsentType(name=absent_type))

        AbsentType.objects.bulk_create(absent_type_list)
        return self.stdout.write(self.style.SUCCESS('请假数据类型初始化成功!'))
