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
    """
    初始化部门数据:
    董事会, 财务部, 人事部, 产品开发部, 运营部, 销售部
    """

    def handle(self, *args, **options):
        departments = [
            OADepartment(name="董事会", intro="董事会部门"),
            OADepartment(name="财务部", intro="财务报表，财务审核"),
            OADepartment(name="人事部", intro="员工招聘，员工培训，员工考核"),
            OADepartment(name="产品开发部", intro="产品设计，技术开发"),
            OADepartment(name="运营部", intro="客户运营，产品运营"),
            OADepartment(name="销售部", intro="产品销售"),
        ]
        OADepartment.objects.bulk_create(departments)
        return self.stdout.write("部门数据初始化成功!")
