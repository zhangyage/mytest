#!/usr/bin/env python
# -*- coding:utf-8 -*-

from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth
from app.models import AnonymousUser, User
from app.api_1_0.errors import unauthorized,forbidden
from . import api


auth = HTTPBasicAuth()
# #简易版  每次都需要密码传递，不安全
# @auth.verify_password
# def verify_password(email, password):
#     if email == '':
#         g.current_user = AnonymousUser()
#         return True
#     user = User.query.filter_by(email = email).first()
#     if not user:
#         return False
#     g.current_user = user
#     return user.verify_password(password)

@auth.verify_password
def verify_password(email_or_token,password):
    if email_or_token == '':
        g.current_user = AnonymousUser()
        return True
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    user = User.query.filter_by(email=email_or_token).first()
    if not user:
        return False
    g.current_user = user
    g.token_used = False
    return user.verify_password(password)
        


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    print 3
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')



@api.route('/tokens', methods=['POST'])
def get_token():
    if g.current_user.is_anonymous() or g.token_used:
        return unauthorized('Invalid credentials')
    return jsonify({'token':g.current_user.generate_auth_token(expiration=3600),'expiration':3600})