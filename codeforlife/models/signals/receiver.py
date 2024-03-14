"""
© Ocado Group
Created on 14/03/2024 at 12:49:34(+00:00).
"""

import typing as t

from django.db.models.signals import ModelSignal
from django.dispatch import receiver as _receiver

from .general import AnyModel


def model_receiver(base: t.Type[AnyModel]):
    """Generates a receiver for a model and all of its inheritances.

    All signals sent by the base model will be received. In addition, all
    signals sent by the base model's inheritances are received. You can specify
    which inheritances to receive signals for by setting the sender argument.

    For example:

    user_receiver = model_receiver(User)

    # Receives all pre-save signals sent by User and all of its inheritances.
    @user_receiver(pre_save)
    def handle_pre_save(): ...

    # Receives all pre-save signals sent by User and its inheritance: SuperUser.
    @user_receiver(pre_save, sender={SuperUser})
    def handle_pre_save(): ...

    Args:
        base: The base model to receive signals for.
    """

    def receiver(
        signal: ModelSignal,
        sender: t.Optional[t.Set[t.Type[AnyModel]]] = None,
        **kwargs,
    ):
        senders = sender

        def decorator(handler: t.Callable):
            def handler_wrapper(
                sender: t.Type[AnyModel], instance, *args, **kwargs
            ):
                def handle_signal():
                    handler(sender, instance, *args, **kwargs)

                if sender is base:
                    handle_signal()
                elif senders is None:
                    if issubclass(sender, base):
                        handle_signal()
                elif sender in senders:
                    handle_signal()

            return _receiver(signal, **kwargs)(handler_wrapper)

        return decorator

    return receiver
