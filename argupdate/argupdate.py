import abc
import inspect
from collections import OrderedDict
from typing import Any, Sequence, Mapping, Tuple, Union, Callable, MutableMapping


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


def update_parameter_value(func: Callable[..., Any],
                           updated_values: MutableMapping[str, UpdateValue],
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
    if not orig_args and not orig_kwargs:
        # nothing to update, so short-circuit here
        return orig_args, orig_kwargs

    signature = inspect.signature(func)
    parameters = signature.parameters

    if not parameters:
        # function doesn't take any parameters, so this is going to be an error.
        # Return the data and let python raise when the args get passed to the function.
        return orig_args, orig_kwargs

    # separate the positional args from the default-having args
    positional_parameters = OrderedDict()
    default_parameters = OrderedDict()
    for name, param in parameters.items():
        if param.default is inspect.Parameter.empty:
            positional_parameters[name] = param
        else:
            default_parameters[name] = param

    if len(orig_args) != len(positional_parameters):
        # wrong number of positional arguments so this is going to be an error.
        # Return the arguments and let python raise when wrong number of args gets passed to the
        # function.
        return orig_args, orig_kwargs

    # Updating positional args if necessary.


    updated_args = []
    if orig_args:
        args_count = 0
        # The parameters are an ordered dict.  The order is determined by the order the arguments
        # are specified in the original function signature.  Since function signatures must have
        # args before kwargs, we can just loop through the parameters until we've reached the
        # first parameter with a default value...aka a kwarg.
        for index, key in enumerate(positional_parameters):
            if key in updated_values:
                update = updated_values.pop(key)
                # This parameter is in our updated_values, so we need to update it.
                if ValueUpdater.is_value_updater(update):
                    # this is a value-updating function so run it
                    value_creator = update()
                    value = value_creator(orig_args[index], signature, orig_args, orig_kwargs)
                else:
                    # just a plain value, so update it
                    value = update
                updated_args.append(value)
            else:
                # We have no updates for this argument, so just use original value
                updated_args.append(orig_args[index])
            args_count += 1

        # sanity check.  We should have checked all arguments without default values and the
        # number of such arguments should equal the length of the original args
        assert args_count == len(orig_args), ("Consistency error.  "
                                              "Un-equal number of positional args.")

    # Updating default-having args if necessary
    kwarg_updates = {}
    for k, v in updated_values.items():
        if k in default_parameters:
            if ValueUpdater.is_value_updater(v):
                value_creator = v()
                value: ValueUpdater = value_creator(orig_kwargs[k], signature, orig_args,
                                                    orig_kwargs)
            else:
                value = v
            kwarg_updates[k] = value

    updated_kwargs = {**orig_kwargs, **kwarg_updates}

    return updated_args or orig_args, updated_kwargs
