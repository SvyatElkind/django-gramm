"""Module for utilities"""

from django.contrib import messages
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.sites.shortcuts import get_current_site
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
import logging
from smtplib import SMTPException

from authenticator.constants import (
    FURTHER_REGISTRATION_MSG,
    CAN_NOT_SEND_EMAIL_MSG,
    ACTIVATE_ACCOUNT
)
from users.models import User

# Get an instance of a logger
logger = logging.getLogger(__name__)

def send_confirmation_email(user: User, request):
    """Generates and sends confirmation email

    Args:
        user: User instance
        request: request object
    """
    # Prepare data for email
    subject = ACTIVATE_ACCOUNT
    message = render_to_string("authenticator/activate_account.html", {
        "domain": get_current_site(request).domain,
        "uid": urlsafe_base64_encode(force_bytes(user.id)),
        "token": PasswordResetTokenGenerator().make_token(user),
        "protocol": "https" if request.is_secure() else "http"
    })

    try:
        # Initialize email
        email = EmailMessage(subject, message, to=[user.email])
        email.send()
        # If email was sent successfully
        messages.success(request, FURTHER_REGISTRATION_MSG)
    except SMTPException:
        logger.exception(CAN_NOT_SEND_EMAIL_MSG.format(user.email))
        # If email was not sent
        messages.error(request, CAN_NOT_SEND_EMAIL_MSG.format(user.email))

