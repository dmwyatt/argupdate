import abc
import inspect
from typing import (
    Any,
    Callable,
    Iterable,
    Mapping,
    MutableMapping,
    Optional,
    Sequence,
    Tuple,
    Union,
)


class ValueUpdater(abc.ABC):
    """Base class for functions that update the value of another functions arguments.

    For usage with :func:`update_parameter_value`.
    """

    @abc.abstractmethod
    def __call__(self, original_value: Any, signature: inspect.Signature,
                 orig_args: Sequence[Any], orig_kwargs: Mapping[str, Any]) -> Any:
        ...

    @staticmethod
    def is_value_updater(value: Any) -> bool:
        try:
            return issubclass(value, ValueUpdater)
        except TypeError:
            return False


ArgKwarg = Tuple[Sequence[Any], Mapping[str, Any]]
UpdateValue = Union[ValueUpdater, Any]

AnyCallable = Callable[..., Any]


def iter_args(func: AnyCallable,
              args: Sequence[Any],
              kwargs: Mapping[str, Any],
              use_default_values_if_needed: Optional[bool] = True,
              signature: Optional[inspect.Signature] = None
              ) -> Iterable[Tuple[str, Any]]:
    sig = signature or inspect.signature(func)
    bound_args: inspect.BoundArguments = sig.bind(*args, **kwargs)
    if use_default_values_if_needed:
        bound_args.apply_defaults()

    bound_args.arguments: MutableMapping[str, Any]
    for name, value in bound_args.arguments.items():
        yield name, value


def update_parameter_value(func: Callable[..., Any],
                           updated_values: Mapping[str, UpdateValue],
                           orig_args: Sequence[Any] = None,
                           orig_kwargs: Mapping[str, Any] = None) -> ArgKwarg:
    """Updates the values in an arg list and kwarg dict to new values.

    :param func: The function that we're going to give the args and kwargs to once we update
        them.
    :param updated_values: A key-value mapping of parameter names to new values. If the new
        value is an instance of :class:`ValueUpdater`, it gets called and its return value used as
        the new value.
    :param orig_args: The original arguments that we want to update.  It's ok to provide None if
        you're only passing kwargs to `func`.
    :param orig_kwargs: The original kwargs that we want to update. It's ok to provide None if
        you're only passing args to `func`.
    :return: Returns the updated args and kwargs.
    """

    sig = inspect.signature(func)

    def updater(key: str, current_value: Any) -> Any:
        if key not in updated_values:
            return current_value
        elif ValueUpdater.is_value_updater(updated_values[key]):
            value_updater = updated_values[key]()
            return value_updater(current_value, sig, orig_args, orig_kwargs)
        else:
            return updated_values[key]

    if orig_args is None:
        orig_args = []
    if orig_kwargs is None:
        orig_kwargs = {}

    args = list(orig_args)
    kwargs = dict(orig_kwargs)

    index = 0
    for name, value in iter_args(func, orig_args, orig_kwargs, signature=sig):
        if name in updated_values:
            # Since iter_args returns arguments ordered as they are in the function signature,
            # we'll first see all the positional args.
            if index < len(orig_args):
                args[index] = updater(name, value)
            # after we've exhausted the positional args, we'll start iterating through the
            # keyword arguments.
            else:
                kwargs[name] = updater(name, value)
                # we don't need to update our index anymore since we go through the positional
                # arguments first.
                continue
        index += 1

    return args, kwargs


if __name__ == '__main__':
    def hi(arg1, arg2, arg3=3, arg4=4) -> None:
        print(arg1, arg2, arg3, arg4)


    args = ('one', 'two')
    a, k = update_parameter_value(hi, {'arg2': 2, 'arg4': 'nope'}, args)
    print(a, k)
    hi(*a, **k)
