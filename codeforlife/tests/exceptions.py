"""
© Ocado Group
Created on 22/01/2026 at 11:19:31(+00:00).
"""

import typing as t
from unittest.mock import patch

if t.TYPE_CHECKING:
    from ..types import Args, KwArgs
    from .test import TestCase


class InterruptPipelineError(Exception):
    """Custom exception to support the Interruption Pattern in tests.

    The Interruption Pattern is a testing technique used to verify that a
    specific step in a complex pipeline is reached and executed correctly,
    without allowing the pipeline to finish. It is useful when the final steps
    have side effects you want to avoid (like writing to a database, sending an
    email, or charging a credit card).
    """

    @classmethod
    # pylint: disable-next=too-many-arguments,too-many-positional-argument
    def run(
        cls,
        test_case: "TestCase",
        step_target,
        step_attribute: str,
        assert_step: t.Callable[[t.Any], None],
        pipeline: t.Callable[..., t.Any],
        pipeline_args: t.Optional["Args"] = None,
        pipeline_kwargs: t.Optional["KwArgs"] = None,
    ):
        """Run a pipeline, interrupting at a specified step.

        Args:
            test_case: The test case instance to use for assertions.
            step_target: The object containing the step method to patch.
            step_attribute: The name of the step method to patch.
            assert_step: A callable that asserts the step was reached correctly.
            pipeline: The pipeline function to run.
            pipeline_args: Positional arguments to pass to the pipeline.
            pipeline_kwargs: Keyword arguments to pass to the pipeline.
        """

        # Get the original step method.
        step = getattr(step_target, step_attribute)
        assert callable(step)

        def side_effect(*step_args, **step_kwargs):
            result = step(*step_args, **step_kwargs)  # Call the original step.
            assert_step(result)  # Assert the step was reached correctly.
            raise cls()  # Interrupt the pipeline.

        # Patch the step method to include the side effect.
        with patch.object(step_target, step_attribute, side_effect=side_effect):
            # Run the pipeline and expect the interruption.
            with test_case.assertRaises(cls):
                pipeline(*(pipeline_args or ()), **(pipeline_kwargs or {}))
