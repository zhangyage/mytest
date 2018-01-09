#!/usr/bin/env python
# -*- coding:utf-8 -*-

#创建api蓝本
from flask import Blueprint
api = Blueprint('api', __name__)
from . import authentication, posts, users, comments, errors