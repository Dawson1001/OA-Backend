# -*- coding:UTF-8 -*- #
"""
@ File : urls.py
@ Software : PyCharm
@ Time : 2025.08.03 23:09
@ Author : Zyeah
@ version : python 3.13.3
@ Description: 
"""
from django.urls import path
from . import views

urlpatterns = [

    path('upload',views.UploadImageView.as_view(), name='upload'),

]