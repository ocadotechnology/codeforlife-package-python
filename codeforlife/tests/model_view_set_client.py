"""
© Ocado Group
Created on 06/11/2024 at 14:13:31(+00:00).

Base test case for all model view clients.
"""

import typing as t

from django.db.models import Model
from django.db.models.query import QuerySet
from django.utils.http import urlencode
from rest_framework import status
from rest_framework.response import Response

from ..types import DataDict, JsonDict, KwArgs
from .api import APIClient, BaseAPIClient
from .api_request_factory import APIRequestFactory, BaseAPIRequestFactory

# pylint: disable=duplicate-code
if t.TYPE_CHECKING:
    from ..user.models import User
    from .model_view_set import BaseModelViewSetTestCase, ModelViewSetTestCase

    RequestUser = t.TypeVar("RequestUser", bound=User)
    AnyBaseModelViewSetTestCase = t.TypeVar(
        "AnyBaseModelViewSetTestCase", bound=BaseModelViewSetTestCase
    )
else:
    RequestUser = t.TypeVar("RequestUser")
    AnyBaseModelViewSetTestCase = t.TypeVar("AnyBaseModelViewSetTestCase")

AnyModel = t.TypeVar("AnyModel", bound=Model)
AnyBaseAPIRequestFactory = t.TypeVar(
    "AnyBaseAPIRequestFactory", bound=BaseAPIRequestFactory
)
# pylint: enable=duplicate-code

# pylint: disable=no-member


# pylint: disable-next=too-many-ancestors
class BaseModelViewSetClient(
    BaseAPIClient[AnyBaseModelViewSetTestCase, AnyBaseAPIRequestFactory],
    t.Generic[AnyBaseModelViewSetTestCase, AnyBaseAPIRequestFactory],
):
    """
    An API client that helps make requests to a model view set and assert their
    responses.
    """

    @property
    def _model_class(self):
        """Shortcut to get model class."""
        return self._test_case.model_class

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

    # pylint: disable-next=too-many-arguments
    def list(
        self,
        models: t.Collection[AnyModel],
        status_code_assertion: APIClient.StatusCodeAssertion = (
            status.HTTP_200_OK
        ),
        make_assertions: bool = True,
        filters: t.Optional[t.Dict[str, t.Union[str, t.Iterable[str]]]] = None,
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

        query: t.List[t.Tuple[str, str]] = []
        for key, values in (filters or {}).items():
            if isinstance(values, str):
                query.append((key, values))
            else:
                for value in values:
                    query.append((key, value))

        response: Response = self.get(
            (
                self._test_case.reverse_action("list", kwargs=reverse_kwargs)
                + f"?{urlencode(query)}"
            ),
            status_code_assertion=status_code_assertion,
            **kwargs,
        )

        if make_assertions:

            def _make_assertions(response_json: JsonDict):
                json_models = t.cast(t.List[JsonDict], response_json["data"])
                assert len(models) == len(json_models)
                for model, json_model in zip(models, json_models):
                    self._test_case.assert_serialized_model_equals_json_model(
                        model, json_model, action="list", request_method="get"
                    )

            self._assert_response_json(response, _make_assertions)

        return response

    # --------------------------------------------------------------------------
    # Partial Update (HTTP PATCH)
    # --------------------------------------------------------------------------

    # pylint: disable-next=too-many-arguments
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

    # pylint: disable-next=too-many-arguments
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

    # pylint: disable-next=too-many-arguments
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

    # pylint: disable-next=too-many-arguments
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
            action: The name of the action.
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

    # pylint: disable-next=too-many-arguments
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
            action: The name of the action.
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


# pylint: disable-next=too-many-ancestors
class ModelViewSetClient(  # type: ignore[misc]
    BaseModelViewSetClient[
        "ModelViewSetTestCase[RequestUser, AnyModel]",
        APIRequestFactory[RequestUser],
    ],
    APIClient[RequestUser],
    t.Generic[RequestUser, AnyModel],
):
    """
    An API client that helps make requests to a model view set and assert their
    responses.
    """
