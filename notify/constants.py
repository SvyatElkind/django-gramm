"""Module for constants used in notify app"""

# Templates
ALL_NOTIFICATIONS_TEMPLATE = "notify/notifications.html"

# Constants for url name (<app>:<url_name>)
NOTIFICATIONS_URL = "notify:all"
NOTIFICATIONS_READ_URL = "notify:read"
NOTIFICATIONS_DELETE_URL = "notify:delete"

# Notification messages
NOTIFY_NEW_POST = "created new post"
NOTIFY_IS_FOLLOWING = "is now following you"
NOTIFY_LIKE_POST = "liked your post"
NOTIFY_LIKE_IMAGE = "liked your image"

# Error messages
NOTIFICATION_DOES_NOT_EXIST = "Notifications does not exist"
ERROR_WHILE_CREATING_POST_NOTIFICATIONS = "Could not create notifications when post with id {} was created"
ERROR_WHILE_CREATING_LIKE_OBJECT_NOTIFICATION = "Could not create notification when {} with id {} was liked"
ERROR_WHILE_DELETING_NOTIFICATION = "Could not delete notifications when related {} with id {} was deleted"

# Notification model constants
TARGET_CONTENT_TYPE = "target_content_type"
TARGET_OBJECT_ID = "target_object_id"
VERB_MAX_LENGTH = 255

# Number of a notifications displayed on the page
NOTIFICATIONS_PER_PAGE = 20
