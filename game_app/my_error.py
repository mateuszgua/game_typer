class MyError(Exception):
    """Base class for other exceptions"""
    pass


class UserNotExist(MyError):
    """Raised when user is not exist in db """
    def __str__(self):
        return "User not exist in database."


class DatabaseProblem(MyError):
    """Raised when user is not exist in db """
    def __str__(self):
        return "Problem to load data from database."