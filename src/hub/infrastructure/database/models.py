from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, MetaData, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, registry, relationship

from hub.domain.models.appointment import AppointmentDateTime, AppointmentId
from hub.domain.models.bot import BotId, BotName, BotTelegramId, BotToken
from hub.domain.models.branch import BranchAddress, BranchId, BranchName
from hub.domain.models.city import CityId, CityName
from hub.domain.models.client import ClientId, ClientName, ClientTelegramId
from hub.domain.models.manager import ManagerId, ManagerTelegramId
from hub.domain.models.master import MasterId, MasterName
from hub.domain.models.service import ServiceDescription, ServiceId, ServiceName
from hub.domain.models.service_master import BreakTime, WorkTime
from hub.domain.models.timezone import TimeZone

convention = {
    "ix": "ix_%(column_0_label)s",  # INDEX
    "uq": "uq_%(table_name)s_%(column_0_N_name)s",  # UNIQUE
    "ck": "ck_%(table_name)s_%(constraint_name)s",  # CHECK
    "fk": "fk_%(table_name)s_%(column_0_N_name)s_%(referred_table_name)s",  # FOREIGN KEY
    "pk": "pk_%(table_name)s",  # PRIMARY KEY
}

mapper_registry = registry(metadata=MetaData(naming_convention=convention))


class BaseModel(DeclarativeBase):
    registry = mapper_registry
    metadata = mapper_registry.metadata


class ManagerModel(BaseModel):
    __tablename__ = "managers"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[ManagerId] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[ManagerTelegramId] = mapped_column(BigInteger, unique=True, nullable=False)

    bots: Mapped[list["BotModel"]] = relationship(back_populates="manager")


class BotModel(BaseModel):
    __tablename__ = "bots"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[BotId] = mapped_column(BigInteger, primary_key=True)
    token: Mapped[BotToken] = mapped_column(String, unique=True, nullable=False)
    telegram_id: Mapped[BotTelegramId] = mapped_column(BigInteger, unique=True, nullable=False)
    name: Mapped[BotName] = mapped_column(String, nullable=False)

    manager_id: Mapped[ManagerId] = mapped_column(BigInteger, ForeignKey("managers.id", ondelete="cascade"))
    manager: Mapped["ManagerModel"] = relationship(back_populates="bots")

    cities: Mapped[list["CityModel"]] = relationship(back_populates="bot")
    services: Mapped[list["ServiceModel"]] = relationship(back_populates="bot")
    masters: Mapped[list["MasterModel"]] = relationship(back_populates="bot")


class CityModel(BaseModel):
    __tablename__ = "cities"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[CityId] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[CityName] = mapped_column(String, nullable=False)
    timezone: Mapped[TimeZone] = mapped_column(String, nullable=False)

    bot_id: Mapped[BotId] = mapped_column(BigInteger, ForeignKey("bots.id", ondelete="cascade"))
    bot: Mapped["BotModel"] = relationship(back_populates="cities")

    branches: Mapped[list["BranchModel"]] = relationship(back_populates="city")
    masters: Mapped[list["MasterModel"]] = relationship(back_populates="city")


class BranchMasterAssociationModel(BaseModel):
    __tablename__ = "branch_master_association"
    __mapper_args__ = {"eager_defaults": True}

    branch_id: Mapped[BranchId] = mapped_column(
        BigInteger, ForeignKey("branches.id", ondelete="cascade"), primary_key=True
    )
    master_id: Mapped[MasterId] = mapped_column(
        BigInteger, ForeignKey("masters.id", ondelete="cascade"), primary_key=True
    )


class BranchModel(BaseModel):
    __tablename__ = "branches"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[BranchId] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[BranchName] = mapped_column(String, nullable=False)
    address: Mapped[BranchAddress] = mapped_column(String, nullable=False)

    city_id: Mapped[CityId] = mapped_column(BigInteger, ForeignKey("cities.id", ondelete="cascade"))
    city: Mapped["CityModel"] = relationship(back_populates="branches")
    masters: Mapped[list["MasterModel"]] = relationship(
        secondary="branch_master_association",
        back_populates="branches",
    )


class ServiceMasterAssociationModel(BaseModel):
    __tablename__ = "service_master_association"
    __mapper_args__ = {"eager_defaults": True}

    service_id: Mapped[BranchId] = mapped_column(
        BigInteger, ForeignKey("services.id", ondelete="cascade"), primary_key=True
    )
    master_id: Mapped[MasterId] = mapped_column(
        BigInteger, ForeignKey("masters.id", ondelete="cascade"), primary_key=True
    )

    work_time: Mapped[WorkTime] = mapped_column(Integer, nullable=False)
    break_time: Mapped[BreakTime] = mapped_column(Integer, nullable=False)


class ServiceModel(BaseModel):
    __tablename__ = "services"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[ServiceId] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[ServiceName] = mapped_column(String, nullable=False)
    description: Mapped[ServiceDescription] = mapped_column(String, nullable=True)

    bot_id: Mapped[BotId] = mapped_column(BigInteger, ForeignKey("bots.id", ondelete="cascade"))
    bot: Mapped["BotModel"] = relationship(back_populates="services")

    masters: Mapped[list["MasterModel"]] = relationship(
        secondary="service_master_association",
        back_populates="services",
    )


class MasterModel(BaseModel):
    __tablename__ = "masters"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[MasterId] = mapped_column(BigInteger, primary_key=True)
    name: Mapped[MasterName] = mapped_column(String, nullable=False)

    bot_id: Mapped[BotId] = mapped_column(BigInteger, ForeignKey("bots.id", ondelete="cascade"))
    bot: Mapped["BotModel"] = relationship(back_populates="masters")

    city_id: Mapped[CityId] = mapped_column(BigInteger, ForeignKey("cities.id", ondelete="SET NULL"))
    city: Mapped["CityModel"] = relationship(back_populates="masters")

    branches: Mapped[list["BranchModel"]] = relationship(
        secondary="branch_master_association",
        back_populates="masters",
    )
    services: Mapped[list["ServiceModel"]] = relationship(
        secondary="service_master_association",
        back_populates="masters",
    )


class AppointmentModel(BaseModel):
    __tablename__ = "appointments"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[AppointmentId] = mapped_column(BigInteger, primary_key=True)
    date: Mapped[AppointmentDateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    master_id: Mapped[MasterId] = mapped_column(BigInteger, ForeignKey("masters.id", ondelete="cascade"))
    client_id: Mapped[ClientId] = mapped_column(BigInteger, ForeignKey("clients.id", ondelete="cascade"))


class ClientModel(BaseModel):
    __tablename__ = "clients"
    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[ClientId] = mapped_column(BigInteger, primary_key=True)
    telegram_id: Mapped[ClientTelegramId] = mapped_column(BigInteger, nullable=False)
    name: Mapped[ClientName] = mapped_column(String, nullable=True)
    bot_id: Mapped[BotId] = mapped_column(BigInteger, ForeignKey("bots.id", ondelete="cascade"))
    city_id: Mapped[CityId] = mapped_column(BigInteger, ForeignKey("cities.id", ondelete="SET NULL"))
