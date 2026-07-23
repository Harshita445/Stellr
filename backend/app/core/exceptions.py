"""Domain exception hierarchy.

Every business error is a typed exception with an HTTP status code and
a machine-readable code string. Global exception handlers catch these and
return consistent JSON error responses.

Usage:
    raise UserNotFoundError()
    raise FriendAlreadyExistsError()
"""


class ConstellationError(Exception):
    """Base exception for all domain errors."""

    def __init__(self, message: str, code: str, status_code: int = 400):
        self.message = message
        self.code = code
        self.status_code = status_code
        super().__init__(message)


# ── Auth Module ──────────────────────────────────────────────────────────

class AuthenticationError(ConstellationError):
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, "AUTHENTICATION_FAILED", 401)


class TokenExpiredError(AuthenticationError):
    def __init__(self):
        super().__init__("Token has expired")


class TokenInvalidError(AuthenticationError):
    def __init__(self):
        super().__init__("Token is invalid")


class DeviceNotFoundError(AuthenticationError):
    def __init__(self):
        super().__init__("Device not recognized")


class DeviceLockedError(AuthenticationError):
    def __init__(self, retry_after: int):
        super().__init__(f"Device locked. Retry after {retry_after}s")
        self.retry_after = retry_after


class DeviceLimitExceededError(ConstellationError):
    def __init__(self):
        super().__init__("Maximum devices reached", "DEVICE_LIMIT", 403)


# ── User Module ──────────────────────────────────────────────────────────

class UserNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("User not found", "USER_NOT_FOUND", 404)


class UserAlreadyExistsError(ConstellationError):
    def __init__(self):
        super().__init__("User already registered", "USER_EXISTS", 409)


class SectionNotSelectedError(ConstellationError):
    def __init__(self):
        super().__init__("Section not selected", "SECTION_REQUIRED", 400)


# ── Friend Module ────────────────────────────────────────────────────────

class FriendNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("Friend not found", "FRIEND_NOT_FOUND", 404)


class FriendAlreadyExistsError(ConstellationError):
    def __init__(self):
        super().__init__("Already friends", "FRIEND_EXISTS", 409)


class CannotFriendSelfError(ConstellationError):
    def __init__(self):
        super().__init__("Cannot add yourself", "SELF_FRIEND", 400)


# ── Group Module ─────────────────────────────────────────────────────────

class GroupNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("Group not found", "GROUP_NOT_FOUND", 404)


class NotGroupMemberError(ConstellationError):
    def __init__(self):
        super().__init__("Not a group member", "NOT_MEMBER", 403)


class NotGroupCreatorError(ConstellationError):
    def __init__(self):
        super().__init__("Only the creator can perform this action", "NOT_CREATOR", 403)


class GroupNameTooLongError(ConstellationError):
    def __init__(self):
        super().__init__("Group name exceeds 100 characters", "NAME_TOO_LONG", 400)


# ── Timetable Module ─────────────────────────────────────────────────────

class ImportInProgressError(ConstellationError):
    def __init__(self):
        super().__init__("Import already in progress", "IMPORT_IN_PROGRESS", 409)


class ImportParseError(ConstellationError):
    def __init__(self, details: list[str]):
        super().__init__("Failed to parse workbook", "IMPORT_PARSE_ERROR", 422)
        self.details = details


class ImportValidationError(ConstellationError):
    def __init__(self, details: list[str]):
        super().__init__("Timetable validation failed", "IMPORT_VALIDATION_ERROR", 422)
        self.details = details


# ── Availability Module ──────────────────────────────────────────────────

class SectionNotFoundError(ConstellationError):
    def __init__(self):
        super().__init__("Section not found", "SECTION_NOT_FOUND", 404)


class NoTimetableError(ConstellationError):
    def __init__(self):
        super().__init__("No timetable available", "NO_TIMETABLE", 404)
