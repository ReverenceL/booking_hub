from hub.application.common.exceptions import ApplicationError


class ManagerIdNotExistsError(ApplicationError):
    pass


class ManagerTelegramIdNotExistsError(ApplicationError):
    pass
