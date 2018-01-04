#!/usr/bin/env python
# -*- coding:utf-8 -*-


from flask import render_template,url_for,redirect,session,current_app,abort,request,make_response,flash
from app import db
from app.models import Permission,User,Role,Post,Comment
from app.email import send_email
from . import main
from .forms import NameForm,EditProfileForm,EditProfileAdminForm,PostForm,CommentForm


#导入装饰器
from app.decorators import admin_required,permission_required
from flask_login import login_required,current_user
from flask_sqlalchemy import Pagination



@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    status = current_user.can(Permission.WRITE)
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        post = Post(body=form.body.data,
                    author=current_user._get_current_object()
                    )
        db.session.add(post)
        return redirect(url_for('main.index'))
    #分页处理
    page = request.args.get('page',1,type=int)
    show_followed=False
    if  current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination =  query.order_by(Post.timestamp.desc()).paginate(
        page,per_page=current_app.config['FLASKY_POSTS_PER_PAGE'],error_out=False
        )
    posts = pagination.items    
#     posts = Post.query.order_by(Post.timestamp.desc()).all()
    return render_template('index.html',form=form,posts=posts,status=status,show_followed=show_followed,pagination=pagination)
#     form = NameForm()
#     if form.validate_on_submit():
#         user = User.query.filter_by(username=form.name.data).first()
#         if user is None:
#             user = User(username=form.name.data)
#             db.session.add(user)
#             db.session.commit()
#             session['known'] = False
#             if current_app.config['FLASKY_ADMIN']:
#                 send_email(current_app.config['FLASKY_ADMIN'], 'New User',
#                            'mail/new_user', user=user)
#         else:
#             session['known'] = True
#         session['name'] = form.name.data
#         return redirect(url_for('.index'))
#     return render_template('index.html',
#                            form=form, name=session.get('name'),known=session.get('known', False))
#     

#用户资料展示页面    
@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    status = current_user.can(Permission.FOLLOW)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html',user=user,posts=posts,status=status)

#用户资料编辑页面
@main.route('/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        flash('Your profile has been updated!')
        return redirect(url_for('main.user',username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html',form=form) 


@main.route('/edit-profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data
        user.username = form.username.data
        user.confirmed = form.confirmed.data
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        db.session.add(user)
        flash('The profile has been updated.')
        return redirect(url_for('main.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    return render_template('edit_profile.html', form=form, user=user)


#文章单页显示
@main.route('/post/<int:id>',methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    status = current_user.can(Permission.COMMENT)
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author = current_user._get_current_object()
                        )
        db.session.add(comment)
        db.session.commit()
        flash('Your comment has been published.')  
        return redirect(url_for('.post', id=post.id, page=-1) )  
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / \
                current_app.config['FLASKY_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(Comment.timestamp.asc()).paginate(
                                        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],
                                        error_out=False)
    comments = pagination.items
    return render_template('post.html',posts=[post], form=form,comments=comments, pagination=pagination,status=status)


#页面编辑
@main.route('/edit/<int:id>',methods=['GET','POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user != post.author and not current_user.can(Permission.ADMIN):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        flash('The post has been updated','ok')
        return redirect(url_for('main.post',id=id))
    form.body.data=post.body
    return render_template('edit_post.html',form=form) 

#添加关注
@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash('You are already following this user.')
        return redirect(url_for('mian.user', username=username))
    current_user.follow(user)
    flash('You are now following %s.' % username)
    return redirect(url_for('main.user', username=username))

#我关注的人
@main.route('/followers/<username>')
def followers(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, 
                                         per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)

#关注我的人    
@main.route('/followed_by/<username>')
def followed_by(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, 
                                         per_page=current_app.config['FLASKY_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)

#取消关注
@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('You are not following this user.')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash('You are not following %s anymore.' % username)
    return redirect(url_for('.user', username=username))

@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp

@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp

#评论管理模块
@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['FLASKY_COMMENTS_PER_PAGE'],error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,pagination=pagination, page=page)

@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))
    
    
#装饰器函数测试用例
@main.route('/admin')
@login_required
@admin_required
def for_admin_only():
    return "For Administrators!"

@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE)
def for_moderators_only():
    return "For comment moderators!"
        
