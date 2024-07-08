from enum import Enum


class NotificationsTypes(Enum):
    WARN = "warn-message"
    ERROR = "error-message"
    SUCCESS = "success-message"
