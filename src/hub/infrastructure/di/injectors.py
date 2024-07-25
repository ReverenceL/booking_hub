from collections.abc import Callable, Sequence
from inspect import Parameter
from typing import Any, Final, ParamSpec, TypeVar, cast

from aiogram_dialog import ChatEvent, DialogManager
from dishka import AsyncContainer
from dishka.integrations.base import DependencyParser, default_parse_dependency, wrap_injection

CONTAINER_KEY: Final[str] = "dishka_container"
RT = TypeVar("RT")
ManagedWidget = TypeVar("ManagedWidget")
Params = ParamSpec("Params")


def create_inject(
    *,
    func: Callable[Params, RT],
    container_getter: Callable[[tuple[Any, ...], dict[Any, Any]], AsyncContainer],
    is_async: bool = True,
    remove_depends: bool = True,
    additional_params: Sequence[Parameter] = (),
    parse_dependency: DependencyParser = default_parse_dependency,
) -> Callable[Params, RT]:
    return cast(
        Callable[Params, RT],
        wrap_injection(  # type: ignore[call-overload]
            func=func,
            container_getter=container_getter,
            is_async=is_async,
            remove_depends=remove_depends,
            additional_params=additional_params,
            parse_dependency=parse_dependency,
        ),
    )


def inject_getter(func: Callable[Params, RT]) -> Callable[Params, RT]:
    return create_inject(
        func=func,
        container_getter=lambda _, p: p[CONTAINER_KEY],
    )


def inject_handler(func: Callable) -> Any:
    return create_inject(
        func=func,
        container_getter=lambda p, _: p[2].middleware_data[CONTAINER_KEY],
    )


def inject_trigger(func: Callable[Params, RT]) -> Callable[[Any, DialogManager], RT]:
    return cast(
        Callable[[Any, DialogManager], RT],
        create_inject(
            func=func,
            container_getter=lambda p, _: p[1].middleware_data[CONTAINER_KEY],
        ),
    )
