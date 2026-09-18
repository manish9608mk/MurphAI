# ============================================================
# MurphAI Custom Exceptions
# ============================================================


# -----------------------------
# User Exceptions
# -----------------------------

class UserNotFoundException(Exception):
    pass


class EmailAlreadyRegisteredException(Exception):
    pass


# -----------------------------
# Job Exceptions
# -----------------------------

class JobNotFoundException(Exception):
    pass


class InvalidJobStatusTransitionException(Exception):
    pass


# -----------------------------
# Worker Exceptions
# -----------------------------

class WorkerNotFoundException(Exception):
    pass


class WorkerAlreadyExistsException(Exception):
    pass


# -----------------------------
# Worker Skill Exceptions
# -----------------------------

class WorkerSkillAlreadyExistsException(Exception):
    pass


class WorkerSkillNotFoundException(Exception):
    pass


# -----------------------------
# Assignment Exceptions
# -----------------------------

class AssignmentNotFoundException(Exception):
    pass


class AssignmentAlreadyExistsException(Exception):
    pass


class InvalidAssignmentTransitionException(Exception):
    pass


class WorkerUnavailableException(Exception):
    pass


# -----------------------------
# Job Interest Exceptions
# -----------------------------

class JobInterestNotFoundException(Exception):
    pass


class JobInterestAlreadyExistsException(Exception):
    pass


class InvalidJobInterestTransitionException(Exception):
    pass


# -----------------------------
# Authorization Exception
# -----------------------------
# Used when a logged-in user
# tries to access something
# they are not allowed to access.

class PermissionDeniedException(Exception):
    pass