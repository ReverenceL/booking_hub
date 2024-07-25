from dataclasses import dataclass

from hub.infrastructure.database.config import DBConfig
from hub.infrastructure.redis_storage.config import RedisConfig


@dataclass
class BotConfig:
    token: str


@dataclass
class WebhookConfig:
    host: str
    path: str
    port: int
    secret: str | None = None


@dataclass
class FSMConfig(RedisConfig):
    db: int = 0


@dataclass
class EventIsolationConfig(RedisConfig):
    db: int = 1


@dataclass
class Config:
    webhook: WebhookConfig
    db: DBConfig
    fsm: FSMConfig
    event_isolation: EventIsolationConfig
    bot: BotConfig | None = None
