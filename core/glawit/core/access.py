import enum


class RepositoryAccess(enum.Enum):
    ADMIN = 5
    MAINTAIN = 4
    READ = 1
    TRIAGE = 2
    WRITE = 3

    def __ge__(self, other):
        assert self.__class__ is other.__class__
        return self.value >= other.value

    def __gt__(self, other):
        assert self.__class__ is other.__class__
        return self.value > other.value

    def __le__(self, other):
        assert self.__class__ is other.__class__
        return self.value <= other.value

    def __lt__(self, other):
        assert self.__class__ is other.__class__
        return self.value < other.value
