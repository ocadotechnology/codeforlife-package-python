"""
© Ocado Group
Created on 19/01/2024 at 17:06:45(+00:00).

Base test case for all model view sets.
"""

import typing as t
from datetime import datetime

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Model
from django.db.models.query import QuerySet
from django.urls import reverse
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.response import Response

from ..permissions import Permission
from ..serializers import BaseSerializer
from ..types import DataDict, JsonDict, KwArgs
from ..user.models import AnyUser as RequestUser
from ..user.models import Class, Student, User
from ..views import ModelViewSet
from .api import APIClient, APITestCase

AnyModel = t.TypeVar("AnyModel", bound=Model)

# pylint: disable=no-member,too-many-arguments


class ModelViewSetClient(
    APIClient[RequestUser], t.Generic[RequestUser, AnyModel]
):
    """
    An API client that helps make requests to a model view set and assert their
    responses.
    """

    _test_case: "ModelViewSetTestCase[RequestUser, AnyModel]"

    @property
    def _model_class(self):
        """Shortcut to get model class."""
        return self._test_case.get_model_class()

    @property
    def _model_view_set_class(self):
        """Shortcut to get model view set class."""
        return self._test_case.model_view_set_class

    # --------------------------------------------------------------------------
    # Create (HTTP POST)
    # --------------------------------------------------------------------------

    def _assert_create(self, json_model: JsonDict, action: str):
        model = self._model_class.objects.get(
            **{self._model_view_set_class.lookup_field: json_model["id"]}
        )
        self._test_case.assert_serialized_model_equals_json_model(
            model, json_model, action, request_method="post"
        )

    def create(
        self,
        data: DataDict,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_201_CREATED
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Create a model.

        Args:
            data: The values for each field.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.post(
            self._test_case.reverse_action("list", kwargs=reverse_kwargs),
            data=data,
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(
                response,
                lambda json_model: self._assert_create(
                    json_model, action="create"
                ),
            )

        return response

    def bulk_create(
        self,
        data: t.List[DataDict],
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_201_CREATED
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk create many instances of a model.

        Args:
            data: The values for each field, for each model.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.post(
            self._test_case.reverse_action("bulk", kwargs=reverse_kwargs),
            data=data,
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(json_models: t.List[JsonDict]):
                for json_model in json_models:
                    self._assert_create(json_model, action="bulk")

            self._assert_response_json_bulk(response, _make_assertions, data)

        return response

    # --------------------------------------------------------------------------
    # Retrieve (HTTP GET)
    # --------------------------------------------------------------------------

    def retrieve(
        self,
        model: AnyModel,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Retrieve a model.

        Args:
            model: The model to retrieve.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.get(
            self._test_case.reverse_action(
                "detail",
                model,
                kwargs=reverse_kwargs,
            ),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(
                response,
                make_assertions=lambda json_model: (
                    self._test_case.assert_serialized_model_equals_json_model(
                        model,
                        json_model,
                        action="retrieve",
                        request_method="get",
                    )
                ),
            )

        return response

    def list(
        self,
        models: t.Iterable[AnyModel],
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        filters: t.Optional[t.Dict[str, str]] = None,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Retrieve a list of models.

        Args:
            models: The model list to retrieve.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            filters: The filters to apply to the list.
            reverse_kwargs: The kwargs for the reverse URL.

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
                self._test_case.reverse_action("list", kwargs=reverse_kwargs)
                + f"?{urlencode(filters or {})}"
            ),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(response_json: JsonDict):
                json_models = t.cast(t.List[JsonDict], response_json["data"])
                for model, json_model in zip(models, json_models):
                    self._test_case.assert_serialized_model_equals_json_model(
                        model, json_model, action="list", request_method="get"
                    )

            self._assert_response_json(response, _make_assertions)

        return response

    # --------------------------------------------------------------------------
    # Partial Update (HTTP PATCH)
    # --------------------------------------------------------------------------

    def _assert_update(
        self,
        model: AnyModel,
        json_model: JsonDict,
        action: str,
        request_method: str,
        partial: bool,
    ):
        model.refresh_from_db()
        self._test_case.assert_serialized_model_equals_json_model(
            model, json_model, action, request_method, contains_subset=partial
        )

    def partial_update(
        self,
        model: AnyModel,
        data: DataDict,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Partially update a model.

        Args:
            model: The model to partially update.
            data: The values for each field.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long
        response: Response = self.patch(
            self._test_case.reverse_action(
                "detail",
                model,
                kwargs=reverse_kwargs,
            ),
            data=data,
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(
                response,
                make_assertions=lambda json_model: self._assert_update(
                    model,
                    json_model,
                    action="partial_update",
                    request_method="patch",
                    partial=True,
                ),
            )

        return response

    def bulk_partial_update(
        self,
        models: t.Union[t.List[AnyModel], QuerySet[AnyModel]],
        data: t.List[DataDict],
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk partially update many instances of a model.

        Args:
            models: The models to partially update.
            data: The values for each field, for each model.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long
        if not isinstance(models, list):
            models = list(models)

        response: Response = self.patch(
            self._test_case.reverse_action("bulk", kwargs=reverse_kwargs),
            data=data,
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(json_models: t.List[JsonDict]):
                models.sort(
                    key=lambda model: getattr(
                        model, self._model_view_set_class.lookup_field
                    )
                )
                for model, json_model in zip(models, json_models):
                    self._assert_update(
                        model,
                        json_model,
                        action="bulk",
                        request_method="patch",
                        partial=True,
                    )

            self._assert_response_json_bulk(response, _make_assertions, data)

        return response

    # --------------------------------------------------------------------------
    # Update (HTTP PUT)
    # --------------------------------------------------------------------------

    def update(
        self,
        model: AnyModel,
        action: str,
        data: t.Optional[DataDict] = None,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Update a model.

        Args:
            model: The model to update.
            data: The values for each field.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long
        response = self.put(
            path=self._test_case.reverse_action(
                action, model, kwargs=reverse_kwargs
            ),
            data=data,
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response_json(
                response,
                make_assertions=lambda json_model: self._assert_update(
                    model,
                    json_model,
                    action,
                    request_method="put",
                    partial=False,
                ),
            )

        return response

    def bulk_update(
        self,
        models: t.Union[t.List[AnyModel], QuerySet[AnyModel]],
        data: t.List[DataDict],
        action: str,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk update many instances of a model.

        Args:
            models: The models to update.
            data: The values for each field, for each model.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long
        if not isinstance(models, list):
            models = list(models)

        assert models
        assert len(models) == len(data)

        response = self.put(
            self._test_case.reverse_action(action, kwargs=reverse_kwargs),
            data={
                getattr(model, self._model_view_set_class.lookup_field): _data
                for model, _data in zip(models, data)
            },
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(json_models: t.List[JsonDict]):
                models.sort(
                    key=lambda model: getattr(
                        model, self._model_view_set_class.lookup_field
                    )
                )
                for model, json_model in zip(models, json_models):
                    self._assert_update(
                        model,
                        json_model,
                        action,
                        request_method="put",
                        partial=False,
                    )

            self._assert_response_json_bulk(response, _make_assertions, data)

        return response

    # --------------------------------------------------------------------------
    # Destroy (HTTP DELETE)
    # --------------------------------------------------------------------------

    def _assert_destroy(self, lookup_values: t.List):
        assert not self._model_class.objects.filter(
            **{f"{self._model_view_set_class.lookup_field}__in": lookup_values}
        ).exists()

    def destroy(
        self,
        model: AnyModel,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_204_NO_CONTENT
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Destroy a model.

        Args:
            model: The model to destroy.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.delete(
            self._test_case.reverse_action(
                "detail",
                model,
                kwargs=reverse_kwargs,
            ),
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
        data: t.List,
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_204_NO_CONTENT
        ),
        make_assertions: bool = True,
        reverse_kwargs: t.Optional[KwArgs] = None,
        **kwargs,
    ):
        # pylint: disable=line-too-long
        """Bulk destroy many instances of a model.

        Args:
            data: The primary keys of the models to lookup and destroy.
            status_code_assertion: The expected status code.
            make_assertions: A flag designating whether to make the default assertions.
            reverse_kwargs: The kwargs for the reverse URL.

        Returns:
            The HTTP response.
        """
        # pylint: enable=line-too-long

        response: Response = self.delete(
            self._test_case.reverse_action("bulk", kwargs=reverse_kwargs),
            data=data,
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:
            self._assert_response(
                response, make_assertions=lambda: self._assert_destroy(data)
            )

        return response


# pylint: enable=no-member


class ModelViewSetTestCase(
    APITestCase[RequestUser], t.Generic[RequestUser, AnyModel]
):
    """Base for all model view set test cases."""

    basename: str
    model_view_set_class: t.Type[ModelViewSet[RequestUser, AnyModel]]
    client: ModelViewSetClient[RequestUser, AnyModel]
    client_class: t.Type[
        ModelViewSetClient[RequestUser, AnyModel]
    ] = ModelViewSetClient

    @classmethod
    def get_model_class(cls) -> t.Type[AnyModel]:
        """Get the model view set's class.

        Returns:
            The model view set's class.
        """
        # pylint: disable-next=no-member
        return t.get_args(cls.__orig_bases__[0])[  # type: ignore[attr-defined]
            1
        ]

    @classmethod
    def setUpClass(cls):
        for attr in ["model_view_set_class", "basename"]:
            assert hasattr(cls, attr), f'Attribute "{attr}" must be set.'

        return super().setUpClass()

    def _get_client_class(self):
        # TODO: unpack type args in index after moving to python 3.11
        # pylint: disable-next=too-few-public-methods
        class _Client(
            self.client_class[  # type: ignore[misc]
                self.get_request_user_class(),
                self.get_model_class(),
            ]
        ):
            _test_case = self

        return _Client

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

        reverse_kwargs = t.cast(t.Optional[KwArgs], kwargs.pop("kwargs", None))
        reverse_kwargs = reverse_kwargs or {}

        if model is not None:
            lookup_field = self.model_view_set_class.lookup_field
            reverse_kwargs[lookup_field] = getattr(model, lookup_field)

        name = name.replace("_", "-")
        return reverse(
            viewname=kwargs.pop("viewname", f"{self.basename}-{name}"),
            kwargs=reverse_kwargs,
            **kwargs,
        )

    # --------------------------------------------------------------------------
    # Assertion Helpers
    # --------------------------------------------------------------------------

    def assert_serialized_model_equals_json_model(
        self,
        model: AnyModel,
        json_model: JsonDict,
        action: str,
        request_method: str,
        contains_subset: bool = False,
    ):
        """Assert the serialized representation of a model matches its JSON
        representation.

        Args:
            model: The model to serialize.
            json_model: The JSON representation of the model.
            action: The model view set's action.
            request_method: The request's HTTP method.
            contains_subset: Whether the JSON representation is a subset of the
                serialized representation. If set to False, the representations
                must be an exact match.
        """
        # Get the logged-in user.
        try:
            user = t.cast(
                RequestUser,
                self.get_request_user_class().objects.get(
                    session=self.client.session.session_key
                ),
            )
        except ObjectDoesNotExist:
            user = None  # NOTE: no user has logged in.

        # Create an instance of the model view set and serializer.
        model_view_set = self.model_view_set_class(
            action=action.replace("-", "_"),
            request=self.client.request_factory.generic(
                request_method, user=user
            ),
            format_kwarg=None,  # NOTE: required by get_serializer_context()
        )
        model_serializer = model_view_set.get_serializer(model)

        # Serialize the model.
        serialized_model = model_serializer.data

        # Recursively convert all datetimes to strings.
        def datetime_values_to_representation(data: DataDict):
            for key, value in data.copy().items():
                if isinstance(value, dict):
                    datetime_values_to_representation(value)
                elif isinstance(value, datetime):
                    data[key] = value.strftime("%Y-%m-%dT%H:%M:%S.%fZ")

        datetime_values_to_representation(serialized_model)

        # Assert the JSON model provided in the response is an exact match or
        # subset of the serialized model.
        (
            self.assertDictContainsSubset
            if contains_subset
            else self.assertDictEqual
        )(json_model, serialized_model)

    def assert_get_serializer_class(
        self,
        serializer_class: t.Type[BaseSerializer],
        action: str,
        *args,
        **kwargs,
    ):
        """Assert that the expected serializer class is returned.

        Args:
            serializer_class: The expected serializer class.
            action: The model view set's action.
        """
        model_view_set = self.model_view_set_class(
            *args, **kwargs, action=action
        )
        actual_serializer_class = model_view_set.get_serializer_class()
        self.assertEqual(serializer_class, actual_serializer_class)

    def assert_get_permissions(
        self, permissions: t.List[Permission], *args, **kwargs
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
        if ordered and not queryset.ordered:
            queryset = queryset.order_by("pk")
        self.assertQuerysetEqual(queryset, values, ordered=ordered)

    def assert_get_serializer_context(
        self,
        serializer_context: t.Dict[str, t.Any],
        action: str,
        *args,
        **kwargs,
    ):
        """Assert that the serializer's context contains a subset of values.

        Args:
            serializer_context: The serializer's context.
            action: The model view set's action.
        """
        kwargs.setdefault("request", self.client.request_factory.get())
        kwargs.setdefault("format_kwarg", None)
        model_view_set = self.model_view_set_class(
            *args, **kwargs, action=action
        )
        actual_serializer_context = model_view_set.get_serializer_context()
        self.assertDictContainsSubset(
            serializer_context, actual_serializer_context
        )

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
            else t.cast(
                Class, t.cast(Student, user.student).class_field
            ).teacher.school
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
                    klass = t.cast(
                        Class, t.cast(Student, user.student).class_field
                    )

                    assert (
                        klass == other_user.student.class_field
                        if same_class
                        else klass != other_user.student.class_field
                    )
        else:
            assert school != other_school

        return other_user
