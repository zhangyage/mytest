#!/usr/bin/env python
# -*- coding:utf-8 -*-

'''
    导入蓝图定义蓝图
'''
from flask import Blueprint

main = Blueprint('main',__name__)

from . import views,errors