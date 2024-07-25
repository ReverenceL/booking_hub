from collections.abc import Callable
from typing import Generic, TypeVar

InputDTO = TypeVar("InputDTO")
OutputDTO = TypeVar("OutputDTO")


class Interactor(Generic[InputDTO, OutputDTO]):
    async def __call__(self, data: InputDTO) -> OutputDTO:
        raise NotImplementedError


InteractorT = TypeVar("InteractorT")
InteractorFactory = Callable[[], InteractorT]
