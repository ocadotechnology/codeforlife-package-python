import typing as t
from unittest.mock import patch

from django.db.models import Model
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from pyotp import TOTP
from rest_framework.response import Response
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APIClient as _APIClient
from rest_framework.test import APITestCase as _APITestCase

from ..user.models import AuthFactor, User

AnyModelSerializer = t.TypeVar("AnyModelSerializer", bound=ModelSerializer)
AnyModel = t.TypeVar("AnyModel", bound=Model)


class APIClient(_APIClient):
    StatusCodeAssertion = t.Optional[t.Union[int, t.Callable[[int], bool]]]
    ListFilters = t.Optional[t.Dict[str, str]]

    @staticmethod
    def status_code_is_ok(status_code: int):
        return 200 <= status_code < 300

    def generic(
        self,
        method,
        path,
        data="",
        content_type="application/octet-stream",
        secure=False,
        status_code_assertion: StatusCodeAssertion = None,
        **extra,
    ):
        wsgi_response = super().generic(
            method, path, data, content_type, secure, **extra
        )

        # Use a custom kwarg to handle the common case of checking the
        # response's status code.
        if status_code_assertion is None:
            status_code_assertion = self.status_code_is_ok
        elif isinstance(status_code_assertion, int):
            expected_status_code = status_code_assertion
            status_code_assertion = (
                lambda status_code: status_code == expected_status_code
            )
        assert status_code_assertion(
            wsgi_response.status_code
        ), f"Unexpected status code: {wsgi_response.status_code}."

        return wsgi_response

    def login(self, **credentials):
        assert super().login(
            **credentials
        ), f"Failed to login with credentials: {credentials}."

        user = User.objects.get(session=self.session.session_key)

        if user.session.session_auth_factors.filter(
            auth_factor__type=AuthFactor.Type.OTP
        ).exists():
            now = timezone.now()
            otp = TOTP(user.otp_secret).at(now)
            with patch.object(timezone, "now", return_value=now):
                assert super().login(
                    otp=otp
                ), f'Failed to login with OTP "{otp}" at {now}.'

        assert user.is_authenticated, "Failed to authenticate user."

        return user

    def login_teacher(self, is_admin: bool, **credentials):
        user = self.login(**credentials)
        assert user.teacher
        assert user.teacher.school
        assert is_admin == user.teacher.is_admin
        return user

    def login_student(self, **credentials):
        user = self.login(**credentials)
        assert user.student
        assert user.student.class_field.teacher.school
        return user

    def login_indy_student(self, **credentials):
        user = self.login(**credentials)
        assert user.student
        assert not user.student.class_field
        return user

    @staticmethod
    def assert_data_equals_model(
        data: t.Dict[str, t.Any],
        model: AnyModel,
        model_serializer_class: t.Type[AnyModelSerializer],
    ):
        assert (
            data == model_serializer_class(model).data
        ), "Data does not equal serialized model."

    def retrieve(
        self,
        basename: str,
        model: AnyModel,
        model_serializer_class: t.Type[AnyModelSerializer],
        status_code_assertion: StatusCodeAssertion = None,
        **kwargs,
    ):
        response: Response = self.get(
            reverse(f"{basename}-detail", kwargs={"pk": model.pk}),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if self.status_code_is_ok(response.status_code):
            self.assert_data_equals_model(
                response.json(),
                model,
                model_serializer_class,
            )

        return response

    def list(
        self,
        basename: str,
        models: t.Iterable[AnyModel],
        model_serializer_class: t.Type[AnyModelSerializer],
        status_code_assertion: StatusCodeAssertion = None,
        filters: ListFilters = None,
        **kwargs,
    ):
        model_class: t.Type[AnyModel] = model_serializer_class.Meta.model
        assert model_class.objects.difference(
            model_class.objects.filter(pk__in=[model.pk for model in models])
        ).exists(), "List must exclude some models for a valid test."

        response: Response = self.get(
            f"{reverse(f'{basename}-list')}?{urlencode(filters or {})}",
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if self.status_code_is_ok(response.status_code):
            for data, model in zip(response.json()["data"], models):
                self.assert_data_equals_model(
                    data,
                    model,
                    model_serializer_class,
                )

        return response


class APITestCase(_APITestCase):
    client: APIClient
    client_class = APIClient

    def get_other_user(
        self,
        user: User,
        other_users: QuerySet[User],
        is_teacher: bool,
    ):
        """
        Get a different user.
        """

        other_user = other_users.first()
        assert other_user
        assert user != other_user
        assert other_user.teacher if is_teacher else other_user.student
        return other_user

    def get_other_school_user(
        self,
        user: User,
        other_users: QuerySet[User],
        is_teacher: bool,
    ):
        """
        Get a different user that is in a school.
        - the provided user does not have to be in a school.
        - the other user has to be in a school.
        """

        other_user = self.get_other_user(user, other_users, is_teacher)
        assert (
            other_user.teacher.school
            if is_teacher
            else other_user.student.class_field.teacher.school
        )
        return other_user

    def get_another_school_user(
        self,
        user: User,
        other_users: QuerySet[User],
        is_teacher: bool,
        same_school: bool,
        same_class: bool = None,
    ):
        """
        Get a different user that is also in a school.
         - the provided user has to be in a school.
         - the other user has to be in a school.
        """

        other_user = self.get_other_school_user(user, other_users, is_teacher)

        school = (
            user.teacher.school
            if user.teacher
            else user.student.class_field.teacher.school
        )
        assert school

        other_school = (
            other_user.teacher.school
            if is_teacher
            else other_user.student.class_field.teacher.school
        )
        assert other_school

        if same_school:
            assert school == other_school

            # Cannot assert that 2 teachers are in the same class since a class
            # can only have 1 teacher.
            if not (user.teacher is not None and is_teacher):
                # At this point, same_class needs to be set.
                assert same_class is not None, "same_class must be set."

                # If one of the users is a teacher.
                if user.teacher is not None or is_teacher:
                    # Get the teacher.
                    teacher = other_user if is_teacher else user

                    # Get the student's class' teacher.
                    class_teacher = (
                        user if is_teacher else other_user
                    ).student.class_field.teacher.new_user

                    # Assert the teacher is the class' teacher.
                    assert (
                        teacher == class_teacher
                        if same_class
                        else teacher != class_teacher
                    )
                # Else, both users are students.
                else:
                    assert (
                        user.student.class_field
                        == other_user.student.class_field
                        if same_class
                        else user.student.class_field
                        != other_user.student.class_field
                    )
        else:
            assert school != other_school

        return other_user
