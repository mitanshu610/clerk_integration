class UserDataException(Exception):
    """Custom exception for user data errors."""
    def __init__(self, message="An error occurred with user data"):
        self.message = message
        super().__init__(self.message)