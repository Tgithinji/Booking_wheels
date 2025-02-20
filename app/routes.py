#!/bin/usr/python3
"""routes"""
from app import app, db
from flask import render_template, flash, redirect, url_for, request, abort
from flask_login import current_user, login_user, logout_user, login_required
from app.forms import UserSignupForm, LoginForm, NewCar, EditProfileForm, BookingForm
from app.models import User, Car, Booking, BookingStatus, CarStatus
import sqlalchemy as sa
from urllib.parse import urlsplit


@app.route('/')
@app.route('/index')
def index():
    """Home page route"""
    return render_template('index.html', title='Home', section='home')


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
    return render_template('signup.html', title='Admin Signup', form=form, section='section')


@app.route('/login', methods=['GET', 'POST'])
def user_login():
    """user login view function"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = db.session.scalar(
            sa.select(User).where(User.username == form.username.data)
        )
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password', 'failed')
            return redirect(url_for('user_login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or urlsplit(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
        #return redirect(next_page) if next_page else redirect(url_for('index'))
    return render_template('login_user.html', title='User Login', form=form, section='section')


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


@app.route('/profile/<username>')
@login_required
def profile(username):
    user = db.first_or_404(
        sa.select(User).where(User.username == username)
    )
    return render_template('profile.html', user=user, title='Profile')


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
    page = request.args.get('page', 1, type=int)
    fleet = Car.query.paginate(page=page, per_page=app.config['POSTS_PER_PAGE'])
    next_url = url_for('view_cars', page=fleet.next_num) \
        if fleet.has_next else None
    prev_url = url_for('view_cars', page=fleet.prev_num) \
        if fleet.has_prev else None
    return render_template('view_fleet.html',
                           fleet=fleet.items,
                           title='View Fleet',
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/cars/<int:user_id>')
@login_required
def manage_cars(user_id):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(id=current_user.id).first_or_404()
    fleet = Car.query.filter_by(owner=user).paginate(page=page, per_page=app.config['POSTS_PER_PAGE'])
    next_url = url_for('manage_cars', page=fleet.next_num) \
        if fleet.has_next else None
    prev_url = url_for('manage_cars', page=fleet.prev_num) \
        if fleet.has_prev else None

    return render_template('manage_fleet.html',
                           fleet=fleet.items,
                           title='Manage Fleet',
                           next_url=next_url,
                           prev_url=prev_url)


@app.route('/car/new', methods=['GET', 'POST'])
@login_required
def new_car():
    form = NewCar()
    if form.validate_on_submit():
        car = Car(make=form.make.data, model=form.model.data,
                  year=form.year.data, reg_num=form.reg_num.data,
                  owner=current_user, fuel_type=form.fuel_type.data,
                  seats=form.seats.data, mileage = form.mileage.data)
        db.session.add(car)
        db.session.commit()
        flash('Car added successfully!', 'success')
        return redirect(url_for('view_cars'))
    return render_template('add_new.html', title='Add Car',
                           form=form, heading='Add Car', section='section')


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
        car.fuel_type = form.fuel_type
        car.seats = form.seats
        car.mileage = form.mileage
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('manage_cars', id=current_user.id))
    elif request.method == 'GET':
        form.make.data = car.make
        form.model.data = car.model
        form.year.data = car.year
        form.reg_num.data = car.reg_num
        form.fuel_type = car.fuel_type
        form.seats = car.seats
        form.mileage = car.mileage
    return render_template('add_new.html', title='UpdateCar',
                           form=form, heading='Update Car', section='section')


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


@app.route('/book/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book_car(car_id):
    car = Car.query.get_or_404(car_id)
    form = BookingForm()

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        # Check car availability (you need to implement this logic)
        if car.is_available(start_date, end_date):
            booking = Booking(
                client=current_user,
                car=car,
                start_date=start_date,
                end_date=end_date,
                status=BookingStatus.PENDING.value
            )
            car.status = CarStatus.PENDING.value
            db.session.add(booking)
            db.session.commit()
            flash('Booking request!', 'success')
            return redirect(url_for('my_bookings', user_id=current_user.id))
        else:
            flash('Car is not available for the selected dates.', 'failed')

    return render_template('book_car.html', car=car, form=form)


@app.route('/bookings/<int:user_id>')
@login_required
def my_bookings(user_id):
    bookings = current_user.bookings
    return render_template('my_bookings.html', bookings=bookings)


@app.route('/requests/<int:user_id>')
@login_required
def pending_requests(user_id):
    """
    Retrieve booking requests for cars owned by the current user (car owner)
    """
    car_owner_bookings = Booking.query.join(Car).\
        filter(Car.owner == current_user,\
               Booking.status == BookingStatus.PENDING.value).\
        all()

    return render_template('pending_requests.html', bookings=car_owner_bookings)


@app.route('/accept_booking/<int:booking_id>')
@login_required
def accept_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if the logged-in user is the owner of the car
    if current_user == booking.car.owner:
        booking.status = BookingStatus.ACCEPTED.value
        booking.car.status = CarStatus.BOOKED.value
        db.session.commit()
        flash('Booking request accepted!', 'success')
        return redirect(url_for('pending_requests', user_id=current_user.id))
    else:
        abort(403)


@app.route('/reject_booking/<int:booking_id>')
@login_required
def reject_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    # Check if the logged-in user is the owner of the car
    if current_user == booking.car.owner:
        booking.status = BookingStatus.REJECTED.value
        booking.car.status = CarStatus.AVAILABLE.value
        db.session.commit()
        flash('Booking request accepted!', 'success')
        return redirect(url_for('pending_requests', user_id=current_user.id))
    else:
        abort(403)
