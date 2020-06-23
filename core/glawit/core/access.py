import enum


class RepositoryAccess(enum.Enum):
    ADMIN = 5
    MAINTAIN = 4
    READ = 1
    TRIAGE = 2
    WRITE = 3
