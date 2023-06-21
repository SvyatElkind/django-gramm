"""Module for constants used in users app"""

# Constants for url name (<app>:<url_name>)
GET_USER_PROFILE_URL = "users:profile"
UPDATE_USER_PROFILE_URL = "users:update"
USER_PAGE_URL = "users:userpage"

# Constants in Views
FOLLOWS = "follows"
FOLLOWING = "following"
FOLLOWERS = "followers"
TARGET_USER = "target_user"
FOLLOW = "follow"
UNFOLLOW = "unfollow"

# Messages in views
USER_DELETED_MSG = "User is successfully deleted."
USER_UPDATED_MSG = "User information is successfully updated."
CANT_CREATE_NOTIFICATION = "Can't create follow notification: user_id {} is following user_id {}"
NO_SUCH_USER = "User with id {} not found"

# Messages in middleware
FILL_IN_ALL_FIELDS = "Please fill in all fields"

# URL parameter
USER_ID = "user_id"

# URLs
USER_CONFIRM_DELETE_TEMPLATE = "users/user_confirm_delete.html"
PROFILE_TEMPLATE = "users/profile.html"
PROFILE_EDIT_TEMPLATE = "users/edit.html"
USER_PAGE_TEMPLATE = "users/user_page.html"

# Models filed names
CONTENT_FIELD = "content"
TAGS_FIELD = "tags"
IMAGES_FIELD = "images"

# DB retry parameters
TRIES = 3
DELAY = 1

# Create user constants
DEFAULT_EMAIL_PREFIX = "random_email"
STRING_LENGTH = 32
DEFAULT_EMAIL_POSTFIX = "random_email.com"

