class UserNotFoundException(Exception):
    pass


class EmailAlreadyRegisteredException(Exception):
    pass


class JobNotFoundException(Exception):
    pass


class InvalidJobStatusTransitionException(Exception):
    pass