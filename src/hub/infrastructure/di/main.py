from typing import Any

from dishka import AsyncContainer, Scope, make_async_container

from ..webhook_url import MultibotWebhookUrl
from .providers import (
    ClientBotGatewayProvider,
    ClientBotInteractorProvider,
    ContextDataProvider,
    DatabaseProvider,
    MainBotGatewayProvider,
    MainBotInteractorProvider,
)


def get_main_bot_ioc_container(context: dict[type[Any], Any] | None = None) -> AsyncContainer:
    context_provider = ContextDataProvider()
    context_provider.from_context(provides=MultibotWebhookUrl, scope=Scope.APP)

    return make_async_container(
        context_provider,
        DatabaseProvider(),
        MainBotGatewayProvider(),
        MainBotInteractorProvider(),
        context=context,
    )


def get_multibot_ioc_container(context: dict[type[Any], Any] | None = None) -> AsyncContainer:
    return make_async_container(
        ContextDataProvider(),
        DatabaseProvider(),
        ClientBotGatewayProvider(),
        ClientBotInteractorProvider(),
        context=context,
    )
