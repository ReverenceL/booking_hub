from abc import abstractmethod
from typing import Protocol

from hub.domain.models.bot import Bot, BotId, BotTelegramId, BotToken
from hub.domain.models.branch import AvailableBranch, Branch, BranchId
from hub.domain.models.city import City, CityId, CityName
from hub.domain.models.client import Client, ClientId, ClientTelegramId
from hub.domain.models.manager import Manager, ManagerId, ManagerTelegramId
from hub.domain.models.master import Master, MasterId
from hub.domain.models.service import AvailableService, Service, ServiceId
from hub.domain.models.timezone import TimeZone


class Committer(Protocol):
    @abstractmethod
    async def commit(self) -> None:
        raise NotImplementedError


class BotReader(Protocol):
    @abstractmethod
    async def get_bot(self, bot_id: BotId) -> Bot:
        raise NotImplementedError

    @abstractmethod
    async def get_bot_by_token(self, bot_token: BotToken) -> Bot:
        raise NotImplementedError

    @abstractmethod
    async def get_bot_by_telegram_id(self, telegram_id: BotTelegramId) -> Bot:
        raise NotImplementedError

    @abstractmethod
    async def get_bots_by_manager_id(self, manager_id: ManagerId) -> list[Bot]:
        raise NotImplementedError

    @abstractmethod
    async def get_bot_cities(self, bot_id: BotId) -> list[City]:
        raise NotImplementedError

    @abstractmethod
    async def get_bot_services(self, bot_id: BotId) -> list[Service]:
        raise NotImplementedError

    @abstractmethod
    async def get_bot_branches(self, bot_id: BotId) -> list[Branch]:
        raise NotImplementedError

    @abstractmethod
    async def get_bot_masters(self, bot_id: BotId) -> list[Master]:
        raise NotImplementedError


class BotSaver(Protocol):
    @abstractmethod
    async def save_bot(self, bot: Bot) -> BotId:
        raise NotImplementedError


class ManagerReader(Protocol):
    @abstractmethod
    async def get_manager(self, manager_id: ManagerId) -> Manager:
        raise NotImplementedError

    @abstractmethod
    async def get_manager_by_telegram_id(self, telegram_id: ManagerTelegramId) -> Manager:
        raise NotImplementedError

    @abstractmethod
    async def get_manager_bots(self, manager_id: ManagerId) -> list[Bot]:
        raise NotImplementedError


class ManagerSaver(Protocol):
    @abstractmethod
    async def save_manager(self, manager: Manager) -> ManagerId:
        raise NotImplementedError


class CityReader(Protocol):
    @abstractmethod
    async def get_city(self, city_id: CityId) -> City:
        raise NotImplementedError

    @abstractmethod
    async def get_branches(self, city_id: CityId) -> list[Branch]:
        raise NotImplementedError


class CitySaver(Protocol):
    @abstractmethod
    async def save_city(self, city: City) -> CityId:
        raise NotImplementedError

    @abstractmethod
    async def update_city_name(self, city_id: CityId, name: CityName) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_city_timezone(self, city_id: CityId, timezone: TimeZone) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_city(self, city_id: CityId) -> None:
        raise NotImplementedError


class BranchReader(Protocol):
    @abstractmethod
    async def get_branch(self, branch_id: BranchId) -> Branch:
        raise NotImplementedError


class BranchSaver(Protocol):
    @abstractmethod
    async def save_branch(self, branch: Branch) -> BranchId:
        raise NotImplementedError

    @abstractmethod
    async def update_branch_name(self, branch_id: BranchId, name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_branch_address(self, branch_id: BranchId, address: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_branch(self, branch_id: BranchId) -> None:
        raise NotImplementedError


class MasterReader(Protocol):
    @abstractmethod
    async def get_master(self, master_id: MasterId) -> Master:
        raise NotImplementedError

    @abstractmethod
    async def get_available_branches(self, bot_id: BotId, master_id: MasterId) -> list[AvailableBranch]:
        raise NotImplementedError

    @abstractmethod
    async def get_available_services(self, bot_id: BotId, master_id: MasterId) -> list[AvailableService]:
        raise NotImplementedError

    @abstractmethod
    async def check_master_attached_to_branch(self, master_id: MasterId, branch_id: BranchId) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def check_master_provides_service(self, master_id: MasterId, service_id: ServiceId) -> bool:
        raise NotImplementedError


class MasterSaver(Protocol):
    @abstractmethod
    async def save_master(self, master: Master) -> MasterId:
        raise NotImplementedError

    @abstractmethod
    async def update_master_name(self, master_id: MasterId, name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def attach_master_to_branch(self, master_id: MasterId, branch_id: BranchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def detach_master_from_branch(self, master_id: MasterId, branch_id: BranchId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def master_provide_service(self, master_id: MasterId, service_id: ServiceId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def master_withhold_service(self, master_id: MasterId, service_id: ServiceId) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_master_work_time(self, master_id: MasterId, service_id: ServiceId, work_time: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_master_break_time(self, master_id: MasterId, service_id: ServiceId, break_time: int) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_master(self, master_id: MasterId) -> None:
        raise NotImplementedError


class ServiceReader(Protocol):
    @abstractmethod
    async def get_service(self, service_id: ServiceId) -> Service:
        raise NotImplementedError


class ServiceSaver(Protocol):
    @abstractmethod
    async def save_service(self, bot_id: BotId, service: Service) -> ServiceId:
        raise NotImplementedError

    @abstractmethod
    async def update_service_name(self, service_id: ServiceId, name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def update_service_description(self, service_id: ServiceId, description: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def delete_service(self, service_id: ServiceId) -> None:
        raise NotImplementedError


class ClientReader(Protocol):
    @abstractmethod
    async def get_client(self, client_id: ClientId) -> Client:
        raise NotImplementedError

    @abstractmethod
    async def get_client_by_telegram_id(self, bot_id: BotId, telegram_id: ClientTelegramId) -> Client:
        raise NotImplementedError


class ClientSaver(Protocol):
    @abstractmethod
    async def save_client(self, client: Client) -> ClientId:
        raise NotImplementedError
