#
# mypy: ignore-errors
#

from dataclasses import replace
from typing import TypeVar

from adaptix import CannotProvide, Dumper, Loader, Mediator
from adaptix._internal.morphing.provider_template import DumperProvider, LoaderProvider
from adaptix._internal.morphing.request_cls import DumperRequest, LoaderRequest
from adaptix._internal.provider.request_cls import LocatedRequest

LocatedRequestT = TypeVar("LocatedRequestT", bound=LocatedRequest)


class NewTypeUnwrappingProvider(LoaderProvider, DumperProvider):
    def _fetch_supertype(self, request: LocatedRequest):
        tp = request.last_loc.type
        supertype = getattr(tp, "__my_supertype__", None)
        if supertype is None:
            raise CannotProvide
        return tp, supertype

    def _provide_loader(self, mediator: Mediator, request: LoaderRequest) -> Loader:
        new_type, supertype = self._fetch_supertype(request)
        supertype_loader = mediator.mandatory_provide(
            replace(
                request,
                loc_stack=request.loc_stack.replace_last_type(supertype),
            ),
        )

        def my_new_type_loader(data):
            return new_type(supertype_loader(data))

        return my_new_type_loader

    def _provide_dumper(self, mediator: Mediator, request: DumperRequest) -> Dumper:
        new_type, supertype = self._fetch_supertype(request)
        return mediator.mandatory_provide(
            replace(
                request,
                loc_stack=request.loc_stack.replace_last_type(supertype),
            ),
        )


def new_type(name: str, cls: type):
    return type(name, (cls,), {"__my_supertype__": cls})
