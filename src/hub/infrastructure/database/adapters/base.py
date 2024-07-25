from sqlalchemy.ext.asyncio import AsyncSession

from hub.application.common.interfaces import Committer


class BaseDbGateway:
    def __init__(self, session: AsyncSession):
        self._session = session


class CommiterImpl(Committer):
    _session: AsyncSession

    async def commit(self) -> None:
        await self._session.commit()
