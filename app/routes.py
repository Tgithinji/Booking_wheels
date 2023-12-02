#!/bin/usr/python3
"""routes"""
from app import app, db
from flask import render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
from app.forms import AdminSignupForm, UserSignupForm, LoginForm
from app.models import User, Admin


@app.route('/')
@app.route('/index')
def index():
    """Home page route"""
    return render_template('index.html', title='Home')


@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    """Admin registration view function"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = AdminSignupForm()
    if form.validate_on_submit():
        admin = Admin(username=form.username.data, email=form.email.data)
        admin.set_password(form.password.data)
        db.session.add(admin)
        db.session.commit()
        flash('Account created successfully. Login to continue', 'success')
        return redirect(url_for('admin_login'))
    return render_template('signup_admin.html', title='Admin Signup', form=form)


@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    """user registration view function"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = UserSignupForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created successfully. Login to continue', 'success')
        return redirect(url_for('user_login'))
    return render_template('signup.html', title='Admin Signup', form=form)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    """Admin login view function"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash('Invalid username or password', 'failed')
            return redirect(url_for('admin_login'))
        login_user(admin, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login_admin.html', title='Admin Login', form=form)


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    """user login view function"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'failed')
            return redirect(url_for('user_login'))
        login_user(user, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login_user.html', title='User Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))
