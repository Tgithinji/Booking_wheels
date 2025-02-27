from app import db
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_required
from app.users.forms import EditProfileForm
from app.models import User
import sqlalchemy as sa
from app.users import bp


@bp.route('/profile/<username>')
@login_required
def profile(username):
    user = db.first_or_404(
        sa.select(User).where(User.username == username)
    )
    return render_template('users/profile.html', user=user, title='Profile')


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your changes have been saved.', 'success')
        return redirect(url_for('users.profile', username=current_user.username))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    return render_template('users/edit_profile.html', title='Edit Profile',
                           form=form)
