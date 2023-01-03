class MyError(Exception):
    """Base class for other exceptions"""
    pass


class UserNotExist(MyError):
    """Raised when user is not exist in db """

    def __str__(self):
        return "User not exist in database."


class DatabaseProblem(MyError):
    """Raised when is problem to load data from database """

    def __str__(self):
        return "Problem to load data from database."


class TeamsDatabaseEmpty(MyError):
    """Raised when database with teams is empty """

    def __str__(self):
        return "Database with teams is empty."


class ImagesNotExist(MyError):
    """Raised when any image not exist in static folder """

    def __str__(self):
        return "There is a problem to load images of flags."


class GameNotExist(MyError):
    """Raised when any game in database not exist """

    def __str__(self):
        return "There is a problem to load game grom database."
