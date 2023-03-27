import django
import pytest

django.setup()


@pytest.mark.django_db
def test_user_import():
    """Basic test to ensure importing the package does not raise an error."""

    from user.models import CFL_User


    from django.contrib.auth.hashers import make_password

    user = CFL_User.objects.create(
        username="test teacher",
        first_name="Albert",
        last_name="Einstein",
        email="alberteinstein@codeforlife.com",
        password=make_password("Password1"),
    )

    user.save()

    created_user = CFL_User.objects.get(username="test teacher")
    assert created_user.username == "test teacher"
    assert created_user.first_name == "Albert"
    assert created_user.last_name == "Einstein"
    assert created_user.email == "alberteinstein@codeforlife.com"

