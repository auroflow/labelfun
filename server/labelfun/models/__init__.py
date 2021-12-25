import enum

from labelfun.extensions import db


class UserType(enum.IntEnum):
    USER = 0
    ADMIN = 1


class TaskType(enum.IntEnum):
    IMAGE_CLS = 0
    IMAGE_SEG = 1
    VIDEO_SEG = 2


class JobStatus(enum.IntEnum):
    UNLABELED = 0
    UNREVIEWED = 1
    DONE = 2
    REVIEWED = 3


class IntEnum(db.TypeDecorator):
    """
    Enables passing in a Python enum and storing the enum's *value* in the db.
    The default would have stored the enum's *name* (ie the string).
    """
    impl = db.Integer

    def __init__(self, enumtype, *args, **kwargs):
        super(IntEnum, self).__init__(*args, **kwargs)
        self._enumtype = enumtype

    def process_bind_param(self, value, dialect):
        if isinstance(value, int):
            return value

        return value.value

    def process_result_value(self, value, dialect):
        return self._enumtype(value)
