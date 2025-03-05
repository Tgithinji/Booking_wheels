from app import db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user
from app.auth.forms import UserSignupForm, LoginForm
from app.models import User
import sqlalchemy as sa
from urllib.parse import urlsplit
from app.auth import bp


@bp.route('/signup', methods=['GET', 'POST'])
def user_signup():
    """user registration view function"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = UserSignupForm()
    if form.validate_on_submit():
        role = 'admin' if form.is_admin.data else 'user'
        user = User(username=form.username.data, email=form.email.data, role=role)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Login to continue', 'success')
        return redirect(url_for('auth.user_login'))
    return render_template('auth/signup.html', title='Admin Signup', form=form, section='section')


@bp.route('/login', methods=['GET', 'POST'])
def user_login():
    """user login view function"""
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'failed')
            return redirect(url_for('auth.user_login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
        #return redirect(next_page) if next_page else redirect(url_for('index'))
    return render_template('auth/login_user.html', title='User Login', form=form, section='section')


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))

