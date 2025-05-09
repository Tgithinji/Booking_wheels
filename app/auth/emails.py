from flask_mail import Message
from app import mail
from flask import current_app, render_template

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


def send_reset_password(user):
    token = user.get_reset_token()
    send_email('[Booking Wheels] Reset your Password',
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('auth/reset_email.txt',
                                         user=user, token=token),
               html_body=render_template('auth/reset_email.html',
                                         user=user, token=token))
