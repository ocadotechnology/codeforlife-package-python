import django
import pytest

django.setup()

from ..models import User


@pytest.mark.django_db
def test_user_import():
    """Basic test to ensure importing the package does not raise an error."""

    user_kwargs = {
        "username": "test teacher",
        "first_name": "Albert",
        "last_name": "Einstein",
        "email": "alberteinstein@codeforlife.com",
        "password": "Password1",
    }

    user = User.objects.create_user(**user_kwargs)
    assert user.username == user_kwargs["username"]
    assert user.first_name == user_kwargs["first_name"]
    assert user.last_name == user_kwargs["last_name"]
    assert user.email == user_kwargs["email"]
