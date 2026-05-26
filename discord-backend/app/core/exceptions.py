# app/core/exceptions.py
from typing import Optional, Any


class DiscordException(Exception):
    """Base exception for the Discord-like application"""
    
    def __init__(self, message: str = "An error occurred", status_code: int = 500, details: Optional[Any] = None):
        self.message = message
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class PermissionDenied(DiscordException):
    """Raised when a user doesn't have permission to perform an action"""
    
    def __init__(self, message: str = "Permission denied", details: Optional[Any] = None):
        super().__init__(message, status_code=403, details=details)


class NotFoundError(DiscordException):
    """Raised when a resource is not found"""
    
    def __init__(self, resource: str, identifier: Optional[str] = None, details: Optional[Any] = None):
        message = f"{resource} not found"
        if identifier:
            message += f": {identifier}"
        super().__init__(message, status_code=404, details=details)


class ValidationError(DiscordException):
    """Raised when validation fails"""
    
    def __init__(self, message: str = "Validation error", details: Optional[Any] = None):
        super().__init__(message, status_code=400, details=details)


class ConflictError(DiscordException):
    """Raised when a resource already exists"""
    
    def __init__(self, message: str = "Resource already exists", details: Optional[Any] = None):
        super().__init__(message, status_code=409, details=details)


class AuthenticationError(DiscordException):
    """Raised when authentication fails"""
    
    def __init__(self, message: str = "Authentication failed", details: Optional[Any] = None):
        super().__init__(message, status_code=401, details=details)


class RateLimitExceeded(DiscordException):
    """Raised when rate limit is exceeded"""
    
    def __init__(self, message: str = "Rate limit exceeded", retry_after: int = 60, details: Optional[Any] = None):
        self.retry_after = retry_after
        super().__init__(message, status_code=429, details=details)