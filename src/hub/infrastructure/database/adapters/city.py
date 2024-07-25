from sqlalchemy import delete, select, update

from hub.application.city.exceptions import CityIdNotExistsError
from hub.application.common.interfaces import CityReader, CitySaver
from hub.domain.models.branch import Branch
from hub.domain.models.city import City, CityId, CityName
from hub.domain.models.timezone import TimeZone
from hub.infrastructure.database.adapters.base import BaseDbGateway, CommiterImpl
from hub.infrastructure.database.converters import branch_converter, city_converter
from hub.infrastructure.database.models import BranchModel, CityModel


class CityDbGateway(BaseDbGateway, CommiterImpl, CityReader, CitySaver):
    async def save_city(self, city: City) -> CityId:
        city_model = CityModel()
        city_model.name = city.name
        city_model.timezone = city.timezone
        city_model.bot_id = city.bot_id

        self._session.add(city_model)
        await self._session.flush()
        return city_model.id

    async def get_city(self, city_id: CityId) -> City:
        city = await self._session.get(CityModel, city_id)
        if city is None:
            raise CityIdNotExistsError
        return city_converter(city)

    async def get_branches(self, city_id: CityId) -> list[Branch]:
        branches = await self._session.scalars(
            select(BranchModel).where(BranchModel.city_id == city_id),
        )
        return [branch_converter(branch) for branch in branches]

    async def delete_city(self, city_id: CityId) -> None:
        await self._session.execute(delete(CityModel).where(CityModel.id == city_id))

    async def update_city_name(self, city_id: CityId, name: CityName) -> None:
        await self._session.execute(update(CityModel).where(CityModel.id == city_id).values(name=name))

    async def update_city_timezone(self, city_id: CityId, timezone: TimeZone) -> None:
        await self._session.execute(update(CityModel).where(CityModel.id == city_id).values(timezone=timezone))
