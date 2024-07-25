from dataclasses import dataclass


@dataclass
class DBConfig:
    host: str
    port: int
    database: str
    user: str
    password: str
    echo: bool = True

    @property
    def full_url(self) -> str:
        return f"postgresql+psycopg_async://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"
