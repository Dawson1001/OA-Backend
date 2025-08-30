# -*- coding:UTF-8 -*- #
"""
@ File : initusers.py
@ Software : PyCharm
@ Time : 2025.07.21 23:03
@ Author : Zyeah
@ version : python 3.13.3
@ Description: 
"""

from django.core.management import BaseCommand
from apps.oaauth.models import OAUser, OADepartment


class Command(BaseCommand):
    """
    初始化用户数据

        Mike    M  董事会      leader
        Jason	M  董事会
        Amy     F  财务部      leader      manager -> Mike
        Emily	F  人事部      leader      manager -> Mike
        David	M  产品开发部   leader      manager -> Jason
        Tom	    M  运营部      leader      manager -> Jason
        Lily	F  销售部      leader      manager -> Jason

    """

    def handle(self, *args, **options):
        init_password = "111111"
        director = OADepartment.objects.get(name="董事会")
        finance = OADepartment.objects.get(name="财务部")
        hr = OADepartment.objects.get(name="人事部")
        developer = OADepartment.objects.get(name="产品开发部")
        operator = OADepartment.objects.get(name="运营部")
        saler = OADepartment.objects.get(name="销售部")

        # 董事会的员工全是超级用户
        Mike = OAUser.objects.create_superuser(
            email="Mike@outlook.com", real_name="迈克",
            password=init_password, department=director)
        Jason = OAUser.objects.create_superuser(email="Jason@outlook.com", real_name="杰森",
                                                password=init_password, department=director)

        # 财务部的员工全是staffuser用户
        Amy = OAUser.objects.create_user(email="Amy@outlook.com", real_name="埃米",
                                         password=init_password, department=finance)

        # 人事部的员工全是staffuser用户
        Emily = OAUser.objects.create_user(email="Emily@outlook.com", real_name="艾米莉",
                                           password=init_password, department=hr)

        # 产品开发部的员工全是staffuser用户
        David = OAUser.objects.create_user(email="David@outlook.com", real_name="大卫",
                                           password=init_password, department=developer)

        # 运营部的员工全是staffuser用户
        Tom = OAUser.objects.create_user(email="Tom@outlook.com", real_name="汤姆",
                                         password=init_password, department=operator)

        # 销售部的员工全是staffuser用户
        Lily = OAUser.objects.create_user(email="Lily@outlook.com", real_name="莉莉",
                                          password=init_password, department=saler)

        # 董事会
        # director.leaders = Mike
        # director.manager = None
        # director.save()
        OADepartment.objects.filter(name="董事会").update(leader=Mike.pk)

        # 财务部
        OADepartment.objects.filter(name="财务部").update(leader_id=Amy.pk, manager_id=Mike.pk)

        # 人事部
        OADepartment.objects.filter(name="人事部").update(leader_id=Emily.pk, manager_id=Mike.pk)

        # 产品开发部
        OADepartment.objects.filter(name="产品开发部").update(leader_id=David.pk, manager_id=Jason.pk)

        # 运营部
        OADepartment.objects.filter(name="运营部").update(leader_id=Tom.pk, manager_id=Jason.pk)

        # 销售部
        OADepartment.objects.filter(name="销售部").update(leader_id=Lily.pk, manager_id=Jason.pk)

        return self.stderr.write("用户数据初始化成功!")
