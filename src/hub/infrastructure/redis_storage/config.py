from dataclasses import dataclass


@dataclass
class RedisConfig:
    host: str
    port: int
    db: int

    @property
    def full_url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"
