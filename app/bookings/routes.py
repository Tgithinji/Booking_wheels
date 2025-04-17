from app import db
from flask import render_template, flash, redirect, url_for, abort, request, current_app
from flask_login import current_user, login_required
from app.bookings.forms import BookingForm
from app.models import User, Car, CarStatus, Booking, BookingStatus
import sqlalchemy as sa
from sqlalchemy.orm import joinedload
from datetime import date, datetime, timezone, timedelta
from app.bookings import bp
from app.jobs import schedule_car_booking


@bp.app_context_processor
def inject_pending_count():
    if current_user.is_authenticated and current_user.is_admin():
        pending_count = (
            db.session.query(Booking)
            .join(Car)
            .filter(
                Car.user_id == current_user.id,
                Booking.status == BookingStatus.PENDING.value
            )
            .count()
        )
        return dict(pending_count=pending_count)
    return dict(pending_count=0)


@bp.route('/book/<int:car_id>', methods=['GET', 'POST'])
@login_required
def book_car(car_id):
    if current_user.is_admin():
        abort(403)
    car = db.first_or_404(
        sa.select(Car).where(Car.id == car_id)
    )
    form = BookingForm()

    if form.validate_on_submit():
        start_date = form.start_date.data
        end_date = form.end_date.data

        now = date.today()
        if start_date > end_date or start_date < now:
            flash('Choose relevant booking dates', 'failed')
            return redirect(url_for('bookings.book_car', car_id=car.id))
        
        # Check car availability (you need to implement this logic)
        if not Booking.is_available(car_id, start_date, end_date):
            flash('This car is already booked for the following dates', 'failed')
            return redirect(url_for('bookings.book_car', car_id=car_id))
        
        # create booking
        booking = Booking(
            car_id=car_id,
            renter_id=current_user.id,
            start_date=start_date,
            end_date=end_date,
            status=BookingStatus.PENDING.value,
            renter=current_user
        )
        
        db.session.add(booking)
        db.session.commit()
        flash('Booking request!', 'success')
        return redirect(url_for('bookings.view_booking', booking_id=booking.id))
    return render_template('bookings/book_car.html', form=form, title='Book Car', car=car, section='section')

@bp.route('/bookings/<int:user_id>')
@login_required
def my_bookings(user_id):
    if current_user.is_admin():
        abort(403)
    page = request.args.get('page', 1, type=int)
    user = db.first_or_404(
        sa.select(User).where(User.id == user_id)
    )
    query = user.bookings.select().order_by(Booking.timestamp.desc())
    bookings = db.paginate(
        query, page=page,
        per_page=current_app.config['POSTS_PER_PAGE'], error_out=False
    )
    next_url = url_for('bookings.my_bookings', user_id=user_id, page=bookings.next_num) if bookings.has_next else None
    prev_url = url_for('bookings.my_bookings', user_id=user_id, page=bookings.prev_num) if bookings.has_prev else None

    return render_template(
        'bookings/my_bookings.html',
        title='My Bookings',
        bookings=bookings,
        next_url=next_url,
        prev_url=prev_url
    )


@bp.route('/booking/<int:booking_id>')
@login_required
def view_booking(booking_id):
    booking = db.first_or_404(
        sa.select(Booking).where(Booking.id == booking_id)
    )
    return render_template('bookings/view_booking.html', booking=booking, title='Bookings')



@bp.route('/requests/<int:user_id>')
@login_required
def pending_requests(user_id):
    """
    Retrieve booking requests for cars owned by the current user (car owner)
    """
    if not current_user.is_admin():
        abort(403)
    pending_requests = (
        db.session.query(Booking)
        .join(Car)
        .filter(
            Car.user_id == current_user.id,
            Booking.status == BookingStatus.PENDING.value
        )
        .options(joinedload(Booking.renter)).all()
    )
    return render_template('bookings/pending_requests.html', bookings=pending_requests)


@bp.route('/accept_booking/<int:booking_id>')
@login_required
def accept_booking(booking_id):
    if not current_user.is_admin():
        abort(403)
    booking = db.first_or_404(
        sa.select(Booking).where(Booking.id == booking_id)
    )

    # Check if the logged-in user is the owner of the car
    if current_user == booking.car.owner:
        booking.status = BookingStatus.ACCEPTED.value
        db.session.commit()

        # check when booking starts and reserve for a day before
        today = datetime.now()
        tomorrow = today + timedelta(days=1)
        if booking.start_date > tomorrow:
            update_date = booking.start_date - timedelta(days=1)
            schedule_car_booking(booking.car_id, update_date)
        else:
            booking.car.status = CarStatus.BOOKED.value
            db.session.commit()

        flash('Booking request accepted!', 'success')
        return redirect(url_for('bookings.pending_requests', user_id=current_user.id))
    else:
        abort(403)


@bp.route('/reject_booking/<int:booking_id>')
@login_required
def reject_booking(booking_id):
    if not current_user.is_admin():
        abort(403)
    booking = db.first_or_404(
        sa.select(Booking).where(
            Booking.id == booking_id,
            Booking.status == BookingStatus.PENDING.value
    ))

    # Check if the logged-in user is the owner of the car
    if current_user == booking.car.owner:
        booking.status = BookingStatus.REJECTED.value
        booking.car.status = CarStatus.AVAILABLE.value
        db.session.commit()
        flash('Booking request rejected!', 'failed')
        return redirect(url_for('bookings.pending_requests', user_id=current_user.id))
    else:
        abort(403)


@bp.route('/cancel_request/<int:booking_id>')
@login_required
def cancel_request(booking_id):
    booking = db.first_or_404(
        sa.select(Booking).where(
            Booking.id == booking_id,
            Booking.status == BookingStatus.PENDING.value
        )
    )
    if current_user == booking.renter:
        booking.car.status = CarStatus.AVAILABLE.value
        db.session.delete(booking)
        db.session.commit()
        flash('Booking request cancelled', 'failed')
        return redirect(url_for('bookings.my_bookings', user_id=booking.renter_id))
    else:
        abort(403)
