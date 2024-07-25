from hub.application.common.exceptions import ApplicationError


class ClientIdNotExistsError(ApplicationError):
    pass


class ClientTelegramIdNotExistsError(ApplicationError):
    pass


class ClientAlreadyExistsError(ApplicationError):
    pass
