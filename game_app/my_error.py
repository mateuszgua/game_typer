class MyError(Exception):
    """Base class for other exceptions"""
    pass


class UserNotExist(MyError):
    """Raised when user is not exist in db """
    def __str__(self):
        return "User not exist in database."