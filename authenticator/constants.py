"""Module for constants used in users app"""

# Constants for url name (<app>:<url_name>)
APP_NAME = "authenticator"

REGISTER = f"{APP_NAME}:register"
LOGIN = f"{APP_NAME}:login"
ACTIVATION = f"{APP_NAME}:activate"
INDEX = f"{APP_NAME}:index"
LOGOUT = f"{APP_NAME}:logout"


# Messages in views
EMAIL_CONFIRMATION_MSG = "Please confirm your email first"
INVALID_EMAIL_OR_PASSWORD_MSG = "Invalid Email/Password"
SUCCESSFUL_EMAIL_CONFIRMATION_MSG = "Congratulations, you have confirmed your email." \
                                    " Now you can log in to your account. "
INVALID_ACTIVATION_LINK_MSG = "Activation link is invalid."
BAD_LOGIN = "Bad login"

# Messages in utils
FURTHER_REGISTRATION_MSG = "Please check your email for further registration"
CAN_NOT_SEND_EMAIL_MSG = "Problem with sending confirmation email to {email}, " \
                         "chick if you typed it correctly."

PASSWORD = "password1"
CONFIRM_PASSWORD = "password2"

# Email subjects
ACTIVATE_ACCOUNT = "Activate your account"

# Templates
LOGIN_TEMPLATE = "authenticator/login.html"
REGISTER_TEMPLATE = "authenticator/register.html"
