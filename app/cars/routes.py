from app import db
from flask import render_template, flash, redirect, url_for, request, abort, current_app
from flask_login import current_user, login_required
from app.cars.forms import NewCar
from app.models import User, Car, CarStatus
import sqlalchemy as sa
from app.cars import bp


@bp.route('/cars')
def view_cars():
    page = request.args.get('page', 1, type=int)
    query = sa.select(Car).where(
        Car.status == CarStatus.AVAILABLE.value
    ).order_by(Car.timestamp.desc())
    fleet = db.paginate(
        query, page=page, per_page=current_app.config['POSTS_PER_PAGE'],
        error_out=False
    )
    next_url = url_for('cars.view_cars', page=fleet.next_num) if fleet.has_next else None
    prev_url = url_for('cars.view_cars', page=fleet.prev_num) if fleet.has_prev else None

    return render_template(
        'cars/view_fleet.html',
        title='Fleet',
        fleet=fleet.items,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/cars/<int:user_id>')
@login_required
def manage_cars(user_id):
    if not current_user.is_admin():
        abort(403)
    user = db.first_or_404(
        sa.select(User).where(User.id == user_id)
    )
    page = request.args.get('page', 1, type=int)
    query = user.cars.select().order_by(Car.timestamp.desc())
    fleet = db.paginate(
        query, page=page,
        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    next_url = url_for('cars.manage_cars', user_id=current_user.id , page=fleet.next_num) if fleet.has_next else None
    prev_url = url_for('cars.manage_cars', user_id=current_user.id, page=fleet.prev_num) if fleet.has_prev else None

    return render_template('cars/manage_fleet.html',
                           fleet=fleet.items,
                           title='Manage Fleet',
                           next_url=next_url,
                           prev_url=prev_url)


@bp.route('/car/new', methods=['GET', 'POST'])
@login_required
def new_car():
    if not current_user.is_admin():
        abort(403)
    form = NewCar()
    if form.validate_on_submit():
        car = Car(make=form.make.data, model=form.model.data,
                  year=form.year.data, reg_num=form.reg_num.data,
                  owner=current_user, fuel_type=form.fuel_type.data,
                  seats=form.seats.data, mileage = form.mileage.data)
        db.session.add(car)
        db.session.commit()
        flash('Car added successfully!', 'success')
        return redirect(url_for('cars.view_cars'))
    return render_template('cars/add_new.html', title='Add Car',
                           form=form, heading='Add Car', section='section')


@bp.route('/car/<int:car_id>')
def view_car(car_id):
    car = db.first_or_404(
        sa.select(Car).where(Car.id == car_id)
    )
    return render_template('cars/view_car.html', car=car, title=car.make)


@bp.route('/car/<int:car_id>/update', methods=['GET', 'POST'])
@login_required
def update_car(car_id):
    if not current_user.is_admin():
        abort(403)
    car = db.first_or_404(
        sa.select(Car).where(Car.id == car_id)
    )
    if car.owner != current_user:
        abort(403)
    form = NewCar()
    if form.validate_on_submit():
        car.make = form.make.data
        car.model = form.model.data
        car.year = form.year.data
        car.reg_num = form.reg_num.data
        car.fuel_type = form.fuel_type.data
        car.seats = form.seats.data
        car.mileage = form.mileage.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('cars.view_car', car_id=car_id))
    elif request.method == 'GET':
        form.make.data = car.make
        form.model.data = car.model
        form.year.data = car.year
        form.reg_num.data = car.reg_num
        form.fuel_type.data = car.fuel_type
        form.seats.data = car.seats
        form.mileage.data = car.mileage
    return render_template('cars/add_new.html', title='UpdateCar',
                           form=form, heading='Update Car', section='section')


@bp.route('/car/<int:car_id>/delete', methods=['GET', 'POST'])
@login_required
def delete_car(car_id):
    if not current_user.is_admin():
        abort(403)
    car = db.first_or_404(
        sa.select(Car).where(Car.id == car_id)
    )
    if car.owner != current_user:
        abort(403)
    db.session.delete(car)
    db.session.commit()
    flash('{} has been deleted successfully!'.format(car.make), 'success')
    return redirect(url_for('cars.manage_cars', user_id=current_user.id))
