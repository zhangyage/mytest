#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
    导入蓝图定义蓝图
'''
from flask import Blueprint

auth = Blueprint('auth',__name__)

from . import views