#!/usr/bin/env python
# -*- coding:utf-8 -*-
from app import db
from werkzeug.security import generate_password_hash,check_password_hash
from flask_login import UserMixin
from . import login_manager
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from flask import current_app,request
from flask_login import UserMixin,AnonymousUserMixin
from datetime import datetime
import hashlib
from markdown import markdown
import bleach




class Permission:
    FOLLOW = 1          #关注用户
    COMMENT = 2         #评论他人的文章
    WRITE = 4           #写文章
    MODERATE = 8        #管理他人发表的评论  
    ADMIN = 16          #管理员权限

class Role(db.Model):
    __tablename__ = 'roles'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), unique=True)
    default = db.Column(db.Boolean,default=False,index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')
   
    def __init__(self, **kwargs):
        super(Role, self).__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0
    
    @staticmethod
    def insert_roles():
        '''
        @pram
        'User'  普通用户  具有发布文章、发表评论和关注其他用户的权限。这是新用户的默认角色
        'Moderator'  协调员  增加审查不当评论的权限
        'Administrator' 管理员  具有所有权限，包括修改其他用户所属角色的权限
        '''
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT, Permission.WRITE],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Administrator': [Permission.FOLLOW, Permission.COMMENT,
                              Permission.WRITE, Permission.MODERATE,
                              Permission.ADMIN],
        }
        default_role = 'User'
        for r in roles:
            role = Role.query.filter_by(name=r).first()
            if role is None:
                role = Role(name=r)
            role.reset_permissions()
            for perm in roles[r]:
                role.add_permission(perm)
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def add_permission(self, perm):
        if not self.has_permission(perm):
            self.permissions += perm

    def remove_permission(self, perm):
        if self.has_permission(perm):
            self.permissions -= perm

    def reset_permissions(self):
        self.permissions = 0

    def has_permission(self, perm):
        return self.permissions & perm == perm
    
    def __repr__(self):
        return '<Role %r>' % self.name

#用户关注关系记录表
class Follow(db.Model):
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, index=True)
    email = db.Column(db.String(64), unique=True, index=True)
    password_hash = db.Column(db.String(255))
    role_id = db.Column(db.Integer, db.ForeignKey('roles.id'))
    confirmed = db.Column(db.Boolean,default=False)
    name = db.Column(db.String(64)) #名字
    avatar_hash = db.Column(db.String(32))   #图片的临时缓存hash值
    location = db.Column(db.String(64)) #所在地
    about_me = db.Column(db.Text())  #关于我
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  #注册日期
    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)    #最后访问日期
    posts = db.relationship('Post', backref='author', lazy='dynamic')
    followed = db.relationship('Follow',
                                foreign_keys=[Follow.follower_id],
                                backref=db.backref('follower', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')
    #关注功能
    def follow(self, user):
        if not self.is_following(user):
            f = Follow(follower=self, followed=user)
            db.session.add(f)
    def unfollow(self, user):
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            db.session.delete(f)
    def is_following(self, user):
        return self.followed.filter_by(followed_id=user.id).first() is not None
    def is_followed_by(self, user):
        return self.followers.filter_by(follower_id=user.id).first() is not None
    
        
    def __init__(self,**kwargs):
        super(User,self).__init__(**kwargs)
        if self.role is None:
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Administrator').first()
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        #调用关注函数，自我关注
        self.follow(self)
    
    #这个是我们程序开发的时候没有考虑到自我关注也一块，后期为了补全功能添加的脚本
    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()
        
    @property
    def password(self):
        raise AttributeError('password is not a readble attibute')
    
    @password.setter
    def password(self,password):
        self.password_hash = generate_password_hash(password)
        
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def generate_confirmation_token(self,expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'],expiration)
        return s.dumps({'confirm':self.id})
    
    def confirm(self,token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return False
            
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        db.session.commit()
        return True
    
    def generate_reset_token(self, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        user = User.query.get(data.get('reset'))
        if user is None:
            return False
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        s = Serializer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.avatar_hash = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        db.session.add(self)
        return True

    def can(self, perm):
        return self.role is not None and self.role.has_permission(perm)

    def is_administrator(self):
        return self.can(Permission.ADMIN)
    
    #用户操作记录，每次操作都会调用一下这个函数
    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)
        
    #图像生成函数    
    def gravatar(self,size=100,default='identicon',rating='g'):
        '''
        @param
         size:图片大小  单位：像素
         default:针对没有设置图片的设置默认值
         rating:图片级别
        '''
        if request.is_secure:
            url = 'https://secure.gravatar.com/avatar'
        else:
            url = 'http://www.gravatar.com/avatar'
        hash = self.avatar_hash or hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{url}/{hash}?s={size}&d={default}&r={rating}'.format(url=url, hash=hash, size=size, default=default, rating=rating)
    
    
    #生成模拟函数
    @staticmethod
    def generate_fake(count=1000):
        from sqlalchemy.exc import IntegrityError
        from random import seed
        import forgery_py
        
        seed()
        for i in range(count):
            u = User(
                    email=forgery_py.internet.email_address(),
                    username=forgery_py.internet.user_name(True),
                    password=forgery_py.lorem_ipsum.word(),
                    confirmed=True,
                    name=forgery_py.name.full_name(),
                    location=forgery_py.address.city(),
                    about_me=forgery_py.lorem_ipsum.sentence(),
                    member_since=forgery_py.date.date(True)
                )
            db.session.add(u)
            try:
                db.session.commit()
            except IntegrityError:  #判断提交的元素数据是否重复
                db.session.rollback()
    
    
    
    
    #连表查询，获取关注用户的文章   集合view中的
    @property
    def followed_posts(self):
        return Post.query.join(Follow, Follow.followed_id == Post.author_id).filter(Follow.follower_id == self.id)
    
    
    def __repr__(self):
        return '<User %r>' % self.usernam
    
    
class AnonymousUser(AnonymousUserMixin):
    def can(self, permissions):
        return False

    def is_administrator(self):
        return False

login_manager.anonymous_user = AnonymousUser
    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

#文章
class Post(db.Model):
    __tablename__= 'posts'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)     #文章内容
    body_html = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)  #创建时间
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))   #关联作者
    
    
    
    #生成模拟函数
    @staticmethod
    def generate_fake(count=100):
        from random import seed,randint
        import forgery_py
        
        seed()
        user_count = User.query.count()
        for i in range(count):
            u = User.query.offset(randint(0, user_count - 1)).first()
            p = Post(body=forgery_py.lorem_ipsum.sentences(randint(1, 3)),
                        timestamp=forgery_py.date.date(True),
                        author=u)
            db.session.add(p)
            db.session.commit()
            
    #将文字转换成网页存储
    @staticmethod
    def on_changed_body(target,value,oldvalue,initiator):
        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
                        'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
                        'h1', 'h2', 'h3', 'p','pre']
        target.body_html = bleach.linkify(bleach.clean(
                                            markdown(value, output_format='html'),
                                            tags=allowed_tags, strip=True))
        
    
    def __repr__(self):
        return '<id %r>' % self.id

#设置一个监听函数，当每次存入文章内容时候，函数会直接将其转换为网页格式的内容    
db.event.listen(Post.body, 'set', Post.on_changed_body)



        
    