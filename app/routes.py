#!/bin/usr/python3
"""routes"""
from app import app
from flask import render_template, flash, redirect
from app.forms import SignupForm, LoginForm


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html', title='Home')


@app.route('/admin_signup', methods=['GET', 'POST'])
def admin_signup():
    form = SignupForm()
    if form.validate_on_submit():
        flash('Account created successfully. Login to continue')
        return redirect('/admin_login')
    return render_template('signup_admin.html', title='Admin Signup', form=form)


@app.route('/user_signup', methods=['GET', 'POST'])
def user_signup():
    form = SignupForm()
    if form.validate_on_submit():
        flash('Account created successfully. Login to continue')
        return redirect('/user_login')
    return render_template('signup.html', title='Admin Signup', form=form)


@app.route('/admin_login', methods=['GET', 'POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login successful')
        return redirect('/index')
    return render_template('login_admin.html', title='Admin Login', form=form)


@app.route('/user_login', methods=['GET', 'POST'])
def user_login():
    form = LoginForm()
    if form.validate_on_submit():
        flash('Login successful')
        return redirect('/index')
    return render_template('login_user.html', title='User Login', form=form)
