from hub.application.common.exceptions import ApplicationError


class BotIdNotExistsError(ApplicationError):
    """Raised when trying to get a bot, but the specified BotId does not exist"""


class BotTokenNotExistsError(ApplicationError):
    """Raised when trying to get a bot, but the specified BotToken does not exist"""


class BotTelegramIdNotExistsError(ApplicationError):
    """Raised when trying to get a bot, but the specified BotTelegramId does not exist"""


class BotAlreadyExistsError(ApplicationError):
    """Raised when trying to add a bot, but bot already exist"""


class InvalidBotTokenError(ApplicationError):
    """Raised when trying to add a bot, but bot token is invalid"""
