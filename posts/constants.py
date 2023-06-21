"""Module for constants used in posts app"""

# Constants for url name (<app>:<url_name>)
POSTS_FEED_URL = "posts:posts"
SINGLE_POST_FEED_URL = "posts:feed_post"

# Messages in views
POST_CREATED_MSG = "Post created successfully!"
POST_UPDATED_MSG = "Post updated successfully!"
POST_DELETED_MSG = "Post deleted successfully!"

# URL parameter
POST_ID = "post_id"

# URLs
POST_CONFIRM_DELETE_TEMPLATE = "posts/post_confirm_delete.html"
POST_LIST_TEMPLATE = "posts/post_list.html"
SINGLE_POST_TEMPLATE = "posts/single_post.html"
CREATE_POST_TEMPLATE = "posts/create_post.html"
UPDATE_POST_TEMPLATE = "posts/update_post.html"
FEED_POST_TEMPLATE = "posts/feed_post.html"
FEED_POST_PREVIEW_TEMPLATE = "posts/feed_post_preview.html"

# Number of a posts displayed on the page
POSTS_PER_PAGE = 10
