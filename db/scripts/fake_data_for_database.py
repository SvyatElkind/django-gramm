import datetime
import io
import random
import requests
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.conf import settings
from faker import Faker
from users.models import User, Post, Image

fake = Faker()
Faker.seed(0)

# Get time frame when user was created
START_DATETIME = datetime.datetime.today() - datetime.timedelta(days=2)
END_DATETIME = datetime.datetime.now()


def get_image():
    """Generates images for user avatar and posts"""
    # Generate a fake image file name and URL
    file_name = fake.file_name(extension="jpg")
    image_url = fake.image_url(placeholder_url="https://loremflickr.com/800/600")

    # Download the image and save it to the media folder
    response = requests.get(image_url)
    with open(settings.BASE_DIR / f"media/posts/{file_name}", "wb") as f:
        f.write(response.content)
    # Read the image data from the file
    with open(settings.BASE_DIR / f"media/posts/{file_name}", "rb") as f:
        image_data = f.read()

    # Create and return the InMemoryUploadedFile object
    file_size = len(image_data)
    file_buffer = io.BytesIO(image_data)
    image_file = InMemoryUploadedFile(
        file_buffer, None, file_name, 'image/jpeg', file_size, None)

    return image_file


def generate_data():
    """
    Generate 20 users with up to 9 post where each post have up to
    5 tags and up to 3 images
    """
    for _ in range(20):

        # get image for avatar
        image_data = get_image()

        user = User(
            email=fake.ascii_email(),
            name=fake.first_name_nonbinary(),
            surname=fake.last_name_nonbinary(),
            bio=fake.text(max_nb_chars=150),
            avatar=image_data,
            created_at=fake.date_time_ad(
                tzinfo=datetime.timezone.utc,
                start_datetime=START_DATETIME,
                end_datetime=END_DATETIME),
            confirmed=True
        )
        user.set_password(fake.password())
        user.save()

        # Create up to 5 random tags
        tag_list = []
        for _ in range(random.randrange(5)):
            tag_list.append(fake.word())

        # Create up to 9 post for each user
        for _ in range(random.randrange(9)):
            post = Post.objects.create(
                user=user,
                content=fake.text(max_nb_chars=150),
                created_at=fake.date_time_ad(
                    tzinfo=datetime.timezone.utc,
                    start_datetime=user.created_at,
                    end_datetime=END_DATETIME),
                tags=tag_list
            )

            # Create up to 3 images for each post
            for _ in range(random.randrange(3)):

                image_data = get_image()

                # Create a new Image object and save it to the database
                Image.objects.create(post=post,
                                     image=image_data)


def generate_likes():
    """Generate likes for the post"""
    for post in Post.objects.all():
        # get random users to like the post
        users = User.objects.order_by("?")[:random.randrange(20)]
        for user in users:
            post.likes.add(user)


generate_data()
generate_likes()
