import logging
from collections.abc import Awaitable, Callable
from pathlib import Path

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.enums import ParseMode
from aiogram.types import LinkPreviewOptions
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, TokenBasedRequestHandler, setup_application
from aiogram_dialog import setup_dialogs as setup_aiogram_dialog
from aiogram_dialog.widgets.text import setup_jinja
from aiohttp import web
from dishka import AsyncContainer
from dishka.integrations.aiogram import setup_dishka

from hub.infrastructure.config_loader import load_config
from hub.infrastructure.di.main import get_main_bot_ioc_container, get_multibot_ioc_container
from hub.infrastructure.jinja_filters import jinja_filters
from hub.infrastructure.redis_storage.factories import create_redis_event_isolation, create_redis_fsm_storage
from hub.infrastructure.webhook_url import MultibotWebhookUrl
from hub.main.config import Config
from hub.presentation.admin_bot.setup import setup as setup_main_bot
from hub.presentation.client_bot.setup import setup as setup_multibot

CONFIG_PATH = Path() / "config"
MAIN_BOT_CONFIG_PATH = CONFIG_PATH / "main_bot_config.toml"
MULTIBOT_CONFIG_PATH = CONFIG_PATH / "multibot_config.toml"


def get_dispatcher(config: Config, ioc_container: AsyncContainer) -> Dispatcher:
    fsm_storage = create_redis_fsm_storage(config.fsm)
    event_isolation = create_redis_event_isolation(config.event_isolation)
    dispatcher = Dispatcher(
        storage=fsm_storage,
        events_isolation=event_isolation,
    )

    setup_jinja(dispatcher, filters=jinja_filters)
    setup_dishka(ioc_container, dispatcher, auto_inject=True)
    setup_aiogram_dialog(dispatcher)

    return dispatcher


def get_on_startup(config: Config) -> Callable[[Bot], Awaitable[None]]:
    url = config.webhook.host + config.webhook.path

    async def on_startup(bot: Bot) -> None:
        await bot.set_webhook(url=url, secret_token=config.webhook.secret)

    return on_startup


# use async func because gunicorn needs an Application instance
# or async func returning an Application instance
async def create_app() -> web.Application:
    logging.basicConfig(level="INFO")
    main_bot_config = load_config(Config, path=MAIN_BOT_CONFIG_PATH)
    if main_bot_config.bot is None:
        raise ValueError("The [bot] section in the main bot configuration file is missed")
    multibot_config = load_config(Config, path=MULTIBOT_CONFIG_PATH)
    bot_settings = {
        "session": AiohttpSession(),
        "default": DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview=LinkPreviewOptions(is_disabled=True),
        ),
    }
    bot = Bot(
        token=main_bot_config.bot.token,
        session=AiohttpSession(),
        default=DefaultBotProperties(
            parse_mode=ParseMode.HTML,
            link_preview=LinkPreviewOptions(is_disabled=True),
        ),
    )
    main_bot_dispatcher = setup_main_bot(
        get_dispatcher(
            config=main_bot_config,
            ioc_container=get_main_bot_ioc_container(
                context={
                    MultibotWebhookUrl: f"{multibot_config.webhook.host}{multibot_config.webhook.path}",
                    Config: main_bot_config,
                },
            ),
        ),
    )
    main_bot_dispatcher.startup.register(get_on_startup(main_bot_config))
    multibot_dispatcher = setup_multibot(
        get_dispatcher(
            config=multibot_config,
            ioc_container=get_multibot_ioc_container(context={Config: multibot_config}),
        ),
    )
    app = web.Application()
    SimpleRequestHandler(
        dispatcher=main_bot_dispatcher,
        bot=bot,
        secret_token=main_bot_config.webhook.secret,
    ).register(app, path=main_bot_config.webhook.path)
    TokenBasedRequestHandler(
        dispatcher=multibot_dispatcher,
        bot_settings=bot_settings,
    ).register(app, path=multibot_config.webhook.path)

    setup_application(app, main_bot_dispatcher, bot=bot)
    setup_application(app, multibot_dispatcher)

    return app
