from users.models import User, Post

TEST_PASSWORD = "123qwe!@#"


def create_test_user():
    user = User.objects.create_user(
        email="user1@email.com",
        password=TEST_PASSWORD,
        name="name",
        surname="surname",
        bio="bio",
        avatar="test.jpg",
        confirmed=True
    )
    return user

def create_test_user_without_data():
    user = User.objects.create_user(
        email="user9@email.com",
        password=TEST_PASSWORD,
        name="name",
        surname="surname",
        confirmed=True
    )
    return user

def create_unconfirmed_user():
    user = User.objects.create_user(
        email="user2@email.com",
        password=TEST_PASSWORD,
    )
    return user

def create_confirmed_user():
    user = User.objects.create_user(
        email="user3@email.com",
        password=TEST_PASSWORD,
        confirmed=True
    )
    return user

def create_test_users():
    user1 = User.objects.create_user(
        email="user4@email.com",
        password=TEST_PASSWORD,
        name="name",
        surname="surname",
        bio="bio",
        avatar="test.jpg",
        confirmed=True
    )
    user2 = User.objects.create_user(
        email="user5@email.com",
        password=TEST_PASSWORD,
        name="name",
        surname="surname",
        bio="bio",
        avatar="test.jpg",
        confirmed=True
    )
    return user1, user2


def create_posts(post_num, user):
    for post in range(post_num):
        Post.objects.create(user=user, content=f"Post number {post}")
