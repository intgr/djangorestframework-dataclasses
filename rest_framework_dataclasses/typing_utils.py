"""
We want to handle at least the more common, slightly complicated type hints, such as Iterable[int] and the likes.
Unfortunately, there's no real API for type introspection at runtime in Python.

So, instead of using a proper API, we'll just apply some heuristics for the common type hints and give up on everything
else. This probably only works on Python 3.7+ and might break at any moment.

Note that there's some promising development in the `typing_inspect` module, but at the time of writing it is still
experimental. Maybe for the future.
"""
import collections
import typing


def is_iterable_type(tp: type) -> bool:
    """
    Test if the given type is iterable.

    Some examples of iterable type hints are:

        Iterable[str]
        Collection[str]
        Mapping[str, int]
        Sequence[str]
        List[str]
        Set[str]
        Dict[str, int]
        Generator[str, int, int]

    """
    # All type hints for iterables satisfy:
    # * Being an instance of the typing._GenericAlias class
    # * Having an __origin__ that extends collections.abc.Iterable
    # * The element type is the first item in __args__
    return (
        isinstance(tp, typing._GenericAlias) and
        isinstance(tp.__origin__, type) and
        issubclass(tp.__origin__, collections.abc.Iterable) and
        len(tp.__args__) >= 1
    )


def get_iterable_element_type(tp: type) -> type:
    """
    Get the type of elements in an iterable.
    """
    if not is_iterable_type(tp):
        raise ValueError('get_iterable_element_type() called with non-iterable type.')

    return tp.__args__[0]


def is_mapping_type(tp: type) -> bool:
    """
    Test if the given type is a mapping.

    Some examples of mapping type hints are:

        Mapping[str, int]
        Dict[str, int]

    """
    # All type hints for mappings satisfy:
    # * Being an instance of the typing._GenericAlias class
    # * Having an __origin__ that extends collections.abc.Mapping
    # * The value type is the second (of two) item in __args__
    return (
        isinstance(tp, typing._GenericAlias) and
        isinstance(tp.__origin__, type) and
        issubclass(tp.__origin__, collections.abc.Mapping) and
        len(tp.__args__) == 2
    )


def get_mapping_value_type(tp: type) -> type:
    """
    Get the type of values in a mapping.
    """
    if not is_mapping_type(tp):
        raise ValueError('get_mapping_value_type() called with non-mapping type.')

    return tp.__args__[1]


def is_optional_type(tp: type) -> bool:
    """
    Test if the given type is optional.

    Some examples of optional type hints are:

        Optional[int]
        Union[int, None]

    """
    # All optional type hints satisfy:
    # * Being an instance of the typing._GenericAlias class
    # * Having an __origin__ that is typing.Union
    # * There is exactly one item in __args__ that is not NoneType
    none_type = type(None)
    return (
        isinstance(tp, typing._GenericAlias) and
        tp.__origin__ is typing.Union and
        any(argument_type is none_type for argument_type in tp.__args__) and
        len([argument_type for argument_type in tp.__args__ if argument_type is not none_type]) == 1
    )


def get_optional_type(tp: type) -> type:
    """
    Get the type that is made optional.
    """
    if not is_optional_type(tp):
        raise ValueError('get_optional_type() called with non-optional type.')

    return next(argument_type for argument_type in tp.__args__ if argument_type is not type(None))
