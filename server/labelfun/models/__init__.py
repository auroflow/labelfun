from enum import IntEnum


class UserType(IntEnum):
    USER = 0
    ADMIN = 1


class TaskType(IntEnum):
    IMAGE_CLS = 0
    IMAGE_SEG = 1
    VIDEO_SEG = 2


class JobStatus(IntEnum):
    UNLABELED = 0
    UNREVIEWED = 1
    DONE = 2
    EMPTY = 3
