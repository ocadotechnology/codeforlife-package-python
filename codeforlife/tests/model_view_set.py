"""
© Ocado Group
Created on 19/01/2024 at 17:06:45(+00:00).

Base test case for all model view sets.
"""

import json
import typing as t
from datetime import datetime
from unittest.mock import patch

from django.db.models import Model
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils import timezone
from django.utils.http import urlencode
from pyotp import TOTP
from rest_framework import status
from rest_framework.response import Response
from rest_framework.serializers import DateTimeField
from rest_framework.test import APIClient, APIRequestFactory, APITestCase

from ..permissions import Permission
from ..serializers import ModelSerializer
from ..types import JsonDict
from ..user.models import (
    AuthFactor,
    NonSchoolTeacherUser,
    SchoolTeacherUser,
    StudentUser,
    TeacherUser,
    User,
)
from ..views import ModelViewSet

AnyModel = t.TypeVar("AnyModel", bound=Model)


class ModelViewSetClient(APIClient, t.Generic[AnyModel]):
    """
    An API client that helps make requests to a model view set and assert their
    responses.
    """

    def __init__(self, enforce_csrf_checks: bool = False, **defaults):
        super().__init__(enforce_csrf_checks, **defaults)
        self.request_factory = APIRequestFactory(
            enforce_csrf_checks,
            **defaults,
        )

    _test_case: "ModelViewSetTestCase[AnyModel]"

    @property
    def _model_class(self):
        """Shortcut to get model class."""

        # pylint: disable-next=no-member
        return self._test_case.get_model_class()

    @property
    def _model_view_set_class(self):
        """Shortcut to get model view set class."""

        # pylint: disable-next=no-member
        return self._test_case.model_view_set_class

    @property
    def _lookup_field(self):
        """Resolves the field to lookup the model."""

        lookup_field = self._model_view_set_class.lookup_field
        return (
            self._model_class._meta.pk.attname
            if lookup_field == "pk"
            else lookup_field
        )

    Data = t.Dict[str, t.Any]
    StatusCodeAssertion = t.Optional[t.Union[int, t.Callable[[int], bool]]]
    ListFilters = t.Optional[t.Dict[str, str]]

    def _assert_response(self, response: Response, make_assertions: t.Callable):
        if self.status_code_is_ok(response.status_code):
            make_assertions()

    def _assert_response_json(
        self,
        response: Response,
        make_assertions: t.Callable[[JsonDict], None],
    ):
        self._assert_response(
            response,
            make_assertions=lambda: make_assertions(
                response.json(),  # type: ignore[attr-defined]
            ),
        )

    def _assert_response_json_bulk(
        self,
        response: Response,
        make_assertions: t.Callable[[t.List[JsonDict]], None],
        data: t.List[Data],
    ):
        def _make_assertions():
            response_json = response.json()  # type: ignore[attr-defined]
            assert isinstance(response_json, list)
            assert len(response_json) == len(data)
            make_assertions(response_json)

        self._assert_response(response, _make_assertions)

    @staticmethod
    def status_code_is_ok(status_code: int):
        """Check if the status code is greater than or equal to 200 and less
        than 300.

        Args:
            status_code: The status code to check.

        Returns:
            A flag designating if the status code is OK.
        """

        return 200 <= status_code < 300

    def _assert_serialized_model_equals_json_model(
        self,
        model: AnyModel,
        json_model: JsonDict,
        contains_subset: bool = False,
    ):
        model_view_set = self._model_view_set_class()
        model_serializer_class = model_view_set.get_serializer_class()
        serialized_model = model_serializer_class(model).data

        datetime_to_representation = DateTimeField().to_representation

        def datetime_values_to_representation(data: ModelViewSetClient.Data):
            for key, value in data.copy().items():
                if isinstance(value, dict):
                    datetime_values_to_representation(value)
                elif isinstance(value, datetime):
                    data[key] = datetime_to_representation(value)

        datetime_values_to_representation(serialized_model)

        (
            # pylint: disable=no-member
            self._test_case.assertDictContainsSubset
            if contains_subset
            else self._test_case.assertDictEqual
            # pylint: enable=no-member
        )(json_model, serialized_model)

    # pylint: disable-next=too-many-arguments
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
        response = t.cast(
            Response,
            super().generic(
                method,
                path,
                data,
                content_type,
                secure,
                **extra,
            ),
        )

        # Use a custom kwarg to handle the common case of checking the
        # response's status code.
        if status_code_assertion is None:
            status_code_assertion = self.status_code_is_ok
        elif isinstance(status_code_assertion, int):
            expected_status_code = status_code_assertion
            status_code_assertion = (
                # pylint: disable-next=unnecessary-lambda-assignment
                lambda status_code: status_code
                == expected_status_code
            )

        # pylint: disable-next=no-member
        status_code = response.status_code
        assert status_code_assertion(
            status_code
        ), f"Unexpected status code: {status_code}."

        return response

    def _assert_create(self, json_model: JsonDict):
        model = self._model_class.objects.get(
            **{self._lookup_field: json_model[self._lookup_field]}
        )
        self._assert_serialized_model_equals_json_model(model, json_model)

    def create(
        self,
        data: Data,
        status_code_assertion: StatusCodeAssertion = status.HTTP_201_CREATED,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Create a model.

        Args:
            data: The values for each field.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.post(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("list"),
            data=json.dumps(data, default=str),
            content_type="application/json",
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(response, self._assert_create)

        return response

    def bulk_create(
        self,
        data: t.List[Data],
        status_code_assertion: StatusCodeAssertion = status.HTTP_201_CREATED,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk create many instances of a model.

        Args:
            data: The values for each field, for each model.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.post(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("bulk"),
            data=json.dumps(data, default=str),
            content_type="application/json",
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(json_models: t.List[JsonDict]):
                for json_model in json_models:
                    self._assert_create(json_model)

            self._assert_response_json_bulk(response, _make_assertions, data)

        return response

    def retrieve(
        self,
        model: AnyModel,
        status_code_assertion: StatusCodeAssertion = status.HTTP_200_OK,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Retrieve a model.

        Args:
            model: The model to retrieve.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.get(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("detail", model),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(
                response,
                make_assertions=lambda json_model: (
                    self._assert_serialized_model_equals_json_model(
                        model, json_model
                    )
                ),
            )

        return response

    def list(
        self,
        models: t.Iterable[AnyModel],
        status_code_assertion: StatusCodeAssertion = status.HTTP_200_OK,
        make_assertions: bool = True,
        filters: ListFilters = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Retrieve a list of models.

        Args:
            models: The model list to retrieve.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            filters: The filters to apply to the list.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        assert self._model_class.objects.difference(
            self._model_class.objects.filter(
                pk__in=[model.pk for model in models]
            )
        ).exists(), "List must exclude some models for a valid test."

        response: Response = self.get(
            (
                # pylint: disable-next=no-member
                self._test_case.reverse_action("list")
                + f"?{urlencode(filters or {})}"
            ),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(response_json: JsonDict):
                json_models = t.cast(t.List[JsonDict], response_json["data"])
                for model, json_model in zip(models, json_models):
                    self._assert_serialized_model_equals_json_model(
                        model, json_model
                    )

            self._assert_response_json(response, _make_assertions)

        return response

    def _assert_partial_update(self, model: AnyModel, json_model: JsonDict):
        model.refresh_from_db()
        self._assert_serialized_model_equals_json_model(
            model, json_model, contains_subset=True
        )

    def partial_update(
        self,
        model: AnyModel,
        data: Data,
        status_code_assertion: StatusCodeAssertion = status.HTTP_200_OK,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Partially update a model.

        Args:
            model: The model to partially update.
            data: The values for each field.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.patch(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("detail", model),
            data=json.dumps(data, default=str),
            content_type="application/json",
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(
                response,
                make_assertions=lambda json_model: (
                    self._assert_partial_update(model, json_model)
                ),
            )

        return response

    def bulk_partial_update(
        self,
        models: t.List[AnyModel],
        data: t.List[Data],
        status_code_assertion: StatusCodeAssertion = status.HTTP_200_OK,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk partially update many instances of a model.

        Args:
            models: The models to partially update.
            data: The values for each field, for each model.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.patch(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("bulk"),
            data=json.dumps(data, default=str),
            content_type="application/json",
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(json_models: t.List[JsonDict]):
                models.sort(
                    key=lambda model: getattr(model, self._lookup_field)
                )
                for model, json_model in zip(models, json_models):
                    self._assert_partial_update(model, json_model)

            self._assert_response_json_bulk(response, _make_assertions, data)

        return response

    def _assert_destroy(self, lookup_values: t.List):
        assert not self._model_class.objects.filter(
            **{f"{self._lookup_field}__in": lookup_values}
        ).exists()

    def destroy(
        self,
        model: AnyModel,
        status_code_assertion: StatusCodeAssertion = status.HTTP_204_NO_CONTENT,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Destroy a model.

        Args:
            model: The model to destroy.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.delete(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("detail", model),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response(
                response,
                make_assertions=lambda: self._assert_destroy([model.pk]),
            )

        return response

    def bulk_destroy(
        self,
        lookup_values: t.List,
        status_code_assertion: StatusCodeAssertion = status.HTTP_204_NO_CONTENT,
        make_assertions: bool = True,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk destroy many instances of a model.

        Args:
            lookup_values: The models to lookup and destroy.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.delete(
            # pylint: disable-next=no-member
            self._test_case.reverse_action("bulk"),
            data=json.dumps(lookup_values, default=str),
            content_type="application/json",
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response(
                response,
                make_assertions=lambda: self._assert_destroy(lookup_values),
            )

        return response

    def login(self, **credentials):
        assert super().login(
            **credentials
        ), f"Failed to login with credentials: {credentials}."

        user = User.objects.get(session=self.session.session_key)

        if user.session.session_auth_factors.filter(
            auth_factor__type=AuthFactor.Type.OTP
        ).exists():
            request = self.request_factory.request()
            request.user = user

            now = timezone.now()
            otp = TOTP(user.otp_secret).at(now)
            with patch.object(timezone, "now", return_value=now):
                assert super().login(
                    request=request,
                    otp=otp,
                ), f'Failed to login with OTP "{otp}" at {now}.'

        assert user.is_authenticated, "Failed to authenticate user."

        return user

    def login_teacher(
        self,
        is_admin: t.Optional[bool] = None,
        **credentials,
    ) -> TeacherUser:
        # pylint: disable=line-too-long
        """Log in a user and assert they are a teacher.

        Args:
            is_admin: Whether or not the teacher is an admin. Set to None if the teacher can be either or.

        Returns:
            The teacher-user.
        """
        # pylint: enable=line-too-long

        user = self.login(**credentials)
        assert user.teacher
        if is_admin is not None:
            assert is_admin == user.teacher.is_admin

        return user

    def login_school_teacher(
        self,
        is_admin: t.Optional[bool] = None,
        **credentials,
    ):
        # pylint: disable=line-too-long
        """Log in a user and assert they are a school-teacher.

        Args:
            is_admin: Whether or not the teacher is an admin. Set to None if the teacher can be either or.

        Returns:
            The school-teacher-user.
        """
        # pylint: enable=line-too-long

        user = self.login_teacher(is_admin, **credentials)
        assert user.teacher.school
        return t.cast(SchoolTeacherUser, user)

    def login_non_school_teacher(self, **credentials):
        """Log in a user and assert they are a non-school-teacher.

        Returns:
            The non-school-teacher-user.
        """

        user = self.login_teacher(is_admin=None, **credentials)
        assert not user.teacher.school
        return t.cast(NonSchoolTeacherUser, user)

    def login_student(self, **credentials) -> StudentUser:
        """Log in a user and assert they are a student.

        Returns:
            The student-user.
        """

        user = self.login(**credentials)
        assert user.student
        assert user.student.class_field.teacher.school
        return user

    # TODO: set return type to IndependentUser when we use the new data models.
    def login_indy(self, **credentials) -> StudentUser:
        """Log in an independent and assert they are a student.

        Returns:
            The independent-user.
        """

        user = self.login(**credentials)
        assert user.student
        assert not user.student.class_field
        return user


class ModelViewSetTestCase(APITestCase, t.Generic[AnyModel]):
    """Base for all model view set test cases."""

    basename: str
    model_view_set_class: t.Type[ModelViewSet[AnyModel]]
    model_serializer_class: t.Optional[t.Type[ModelSerializer[AnyModel]]] = None
    client: ModelViewSetClient[AnyModel]
    client_class = ModelViewSetClient  # type: ignore[assignment]

    def _pre_setup(self):
        super()._pre_setup()  # type: ignore[misc]
        # pylint: disable-next=protected-access
        self.client._test_case = self

    @classmethod
    def get_model_class(cls) -> t.Type[AnyModel]:
        """Get the model view set's class.

        Returns:
            The model view set's class.
        """

        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            0
        ]

    @classmethod
    def setUpClass(cls):
        attr_name = "model_view_set_class"
        assert hasattr(cls, attr_name), f'Attribute "{attr_name}" must be set.'

        return super().setUpClass()

    def reverse_action(
        self,
        name: str,
        model: t.Optional[AnyModel] = None,
        **kwargs,
    ):
        """Get the reverse URL for the model view set's action.

        Args:
            name: The name of the action.
            model: The model to look up.

        Returns:
            The reversed URL for the model view set's action.
        """

        reverse_kwargs = kwargs.pop("kwargs", {})
        if model is not None:
            lookup_field = self.model_view_set_class.lookup_field
            reverse_kwargs[lookup_field] = getattr(model, lookup_field)

        return reverse(
            viewname=kwargs.pop("viewname", f"{self.basename}-{name}"),
            kwargs=reverse_kwargs,
            **kwargs,
        )

    def assert_get_permissions(
        self,
        permissions: t.List[Permission],
        *args,
        **kwargs,
    ):
        """Assert that the expected permissions are returned.

        Args:
            permissions: The expected permissions.
        """

        model_view_set = self.model_view_set_class(*args, **kwargs)
        actual_permissions = model_view_set.get_permissions()
        self.assertListEqual(permissions, actual_permissions)

    def assert_get_queryset(
        self,
        values: t.Collection[AnyModel],
        *args,
        ordered: bool = True,
        **kwargs,
    ):
        """Assert that the expected queryset is returned.

        Args:
            values: The values we expect the queryset to contain.
            ordered: Whether the queryset provides an implicit ordering.
        """

        model_view_set = self.model_view_set_class(*args, **kwargs)
        queryset = model_view_set.get_queryset()
        # pylint: disable-next=no-member
        self.assertQuerySetEqual(queryset, values, ordered=ordered)

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
        same_class: t.Optional[bool] = None,
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
            else user.student.class_field.teacher.school  # type: ignore[union-attr]
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
            if not (user.teacher and other_user.teacher):
                # At this point, same_class needs to be set.
                assert same_class is not None, "same_class must be set."

                # If one of the users is a teacher.
                if user.teacher or is_teacher:
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
                        user.student.class_field  # type: ignore[union-attr]
                        == other_user.student.class_field
                        if same_class
                        else user.student.class_field  # type: ignore[union-attr]
                        != other_user.student.class_field
                    )
        else:
            assert school != other_school

        return other_user
