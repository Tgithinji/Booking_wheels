#!/bin/usr/python3
"""routes"""
from app import app, db
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import UserSignupForm, LoginForm, NewCar, EditProfileForm
from app.models import User, Car


@app.route('/')
@app.route('/index')
def index():
    """Home page route"""
    return render_template('index.html', title='Home')


@app.route('/signup', methods=['GET', 'POST'])
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


@app.route('/login', methods=['GET', 'POST'])
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
        next_page = request.args.get('next')
        return redirect(next_page) if next_page else redirect(url_for('index'))
    return render_template('login_user.html', title='User Login', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/<username>')
@login_required
def profile(username):
    user = User.query.filter_by(id=current_user.id).first_or_404()
    return render_template('profile.html', user=user, title='Account')


@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form)


@app.route('/cars')
def view_cars():
    fleet = Car.query.all()
    return render_template('view_fleet.html', fleet=fleet, title='View Fleet')


@app.route('/cars/<int:user_id>')
@login_required
def manage_cars(user_id):
    user = User.query.filter_by(id=current_user.id).first_or_404()
    fleet = Car.query.filter_by(owner=user).all()
    return render_template('manage_fleet.html', fleet=fleet, title='Manage Fleet')


@app.route('/car/new', methods=['GET', 'POST'])
@login_required
def new_car():
    form = NewCar()
    if form.validate_on_submit():
        car = Car(make=form.make.data, model=form.model.data,
                  year=form.year.data, reg_num=form.reg_num.data,
                  owner=current_user)
        db.session.add(car)
        db.session.commit()
        flash('Car added successfully!', 'success')
        return redirect(url_for('view_cars'))
    return render_template('add_new.html', title='Add Car',
                           form=form, heading='Add Car')


@app.route('/car/<int:car_id>')
def view_car(car_id):
    car = Car.query.get_or_404(car_id)
    return render_template('view_car.html', car=car, title=car.make)


@app.route('/car/<int:car_id>/update', methods=['GET', 'POST'])
@login_required
def update_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner != current_user:
        abort(403)
    form = NewCar()
    if form.validate_on_submit():
        car.make = form.make.data
        car.model = form.model.data
        car.year = form.year.data
        car.reg_num = form.reg_num.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('manage_cars', id=current_user.id))
    elif request.method == 'GET':
        form.make.data = car.make
        form.model.data = car.model
        form.year.data = car.year
        form.reg_num.data = car.reg_num
    return render_template('add_new.html', title='UpdateCar',
                           form=form, heading='Update Car')


@app.route('/car/<int:car_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_car(car_id):
    car = Car.query.get_or_404(car_id)
    if car.owner != current_user:
        abort(403)
    db.session.delete(car)
    db.session.commit()
    flash('{} has been deleted successfully!'.format(car.make), 'success')
    return redirect(url_for('manage_cars', id=car.owner.id))
