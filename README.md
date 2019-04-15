# argupdate

This package is used for updating values in the args/kwargs destined to
a function. This is particularly useful for decorators that want to
modify the values passed into the decorated function.

By introspecting the function the args/kwargs are destined for, it knows
the names of all arguments in your args (and of course your kwargs since
that is a dict). Because of this, you are able to provide updated values
by name of the argument.

By accepting a special callable, we also provide a way to dynamically
update the value of an argument at runtime.

## simple example

### The function we want to modify a value for

```python
from typing import Optional

def foo(arg_1: int, arg_2: bool, arg_3: Optional[str] = None) -> None:
    print(arg_1, arg_2, arg_3)
```

Let's say for some reason we always want `arg_2` to be `False`, no
matter what the caller passes in.

```python
import functools
from argupdate import update_parameter_value
from typing import Optional

def arg_2_always_false(func):
    # This is the new value for `arg_2`
    updated_values = {
        'arg_2': False
    }
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Here we update the value.
        updated_args, updated_kwargs = update_parameter_value(func, updated_values, args, kwargs)
        return func(*updated_args, **updated_kwargs)
    return wrapper

@arg_2_always_false
def foo(arg_1: int, arg_2: bool, arg_3: Optional[str] = None) -> None:
    print(arg_1, arg_2, arg_3)
```

Admittedly, this is a contrived example. You could've just set set the
second parameter in `args` to `False` without using this library. But,
even in this small, contrived example, you've gained some decoupling by
using `argupdate`. As long as the name of the parameter stays the same,
you do not have to count on it being the second parameter in the
argument list.

## more advanced example
You can also use a special callable as the new value. This allows you to
set the new value based upon the signature of the function and other
argument's values.

Here is an example taken from a real project. This project wrapped
multiple other backend libraries. These libraries all had methods that
took a `handle` argument as an `int`. Except one. This one library
required the `handle` argument as a string that looked like
`[HANDLE:0x0000001]`.

Instead of repeating code everywhere checking which type of handle we
should pass in, we created a decorator that did it for us.

```python
import functools
import inspect
from typing import Any, Mapping, Sequence

from argupdate import update_parameter_value, ValueUpdater
from utils import stringify_int


def handle_stringifier(func):
    class update_handle(ValueUpdater):
        def __call__(self,
                     original_value: Any,
                     signature: inspect.Signature,
                     orig_args: Sequence[Any],
                     orig_kwargs: Mapping[str, Any]) -> Any:
            if isinstance(original_value, int):
                return stringify_int(int)

            return original_value


    updated_values = {
        # update_handle will be used to create the value for the argument
        # called `handle`
        'handle': update_handle
    }

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        updated_args, updated_kwargs = update_parameter_value(func, updated_values, args, kwargs)
        return func(*updated_args, **updated_kwargs)

    return wrapper


@handle_stringifier
def weird_handle_taker(handle: int) -> None:
    ...
```
