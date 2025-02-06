class BaseAPIException(Exception):
    """Base exception for API-related errors"""

    def __init__(self, detail: str):
        self.detail = detail
        super().__init__(self.detail)


class DuplicateEntityException(BaseAPIException):
    """Raised when trying to create an entity that already exists"""

    pass


class RegistrationException(BaseAPIException):
    """Raised when there's an error during user registration"""

    pass


class AuthenticationException(BaseAPIException):
    """Raised when authentication fails"""

    pass
