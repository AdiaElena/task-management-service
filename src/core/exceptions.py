class NotFoundError(Exception):
    """
    Domain exception raised when a requested entity is not found in the repository.
    This exception is caught and translated to HTTP 404 in the API layer.
    """
    pass