#!/usr/bin/env python
# -*- coding:utf-8 -*-

from hello import app
from flask import current_app
'''
print current_app.name   #我们直接导入我们刚写的hello程序。没有激活直接获取当前运行程序的名称是会报错的
                         #RuntimeError: Working outside of application context.
                         #没有工作的上下文
'''                         
app_ctx = app.app_context()   #app.app_context() 可获得一个程序上下文
app_ctx.push()                #激活程序上下文 
print current_app.name           #输出hello