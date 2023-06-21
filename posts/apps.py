from django.apps import AppConfig

from posts.constants import POSTS_PER_PAGE


class PostsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'posts'

    def ready(self):
        """Overrides post per page value"""
        from django.conf import settings
        settings.PAGINATE_BY = POSTS_PER_PAGE

        import posts.signals
