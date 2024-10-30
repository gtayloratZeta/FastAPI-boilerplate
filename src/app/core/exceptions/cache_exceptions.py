class CacheIdentificationInferenceError(Exception):
    """
    Defines a custom exception for errors that occur when inferring a cache
    identifier, providing a specific error message and inheriting from the base
    `Exception` class for error handling.

    Attributes:
        message (str): Initialized with a default value of "Could not infer id for
            resource being cached."

    """
    def __init__(self, message: str = "Could not infer id for resource being cached.") -> None:
        """
        Initializes an instance of the CacheIdentificationInferenceError class
        with a custom error message and passes it to the superclass (Exception)
        for further processing.

        Args:
            message (str): Optional, with a default value of "Could not infer id
                for resource being cached."

        """
        self.message = message
        super().__init__(self.message)


class InvalidRequestError(Exception):
    """
    Inherits from the built-in Python `Exception` class, allowing it to be raised
    when an invalid request occurs. It has a custom `__init__` method that accepts
    an optional message, which is used to set the error message and passed to the
    parent class.

    Attributes:
        message (str): Initialized with a default value of "Type of request not supported."

    """
    def __init__(self, message: str = "Type of request not supported.") -> None:
        """
        Initializes an instance of InvalidRequestError with a custom error message,
        which is then passed to the superclass (Exception) to construct the error
        object.

        Args:
            message (str): Optional. It defaults to the string "Type of request
                not supported." if not provided.

        """
        self.message = message
        super().__init__(self.message)


class MissingClientError(Exception):
    """
    Inherits from the built-in `Exception` class and creates a custom exception
    for cases where a client is missing or `None`. It allows for a custom error
    message when raising the exception.

    Attributes:
        message (str): Assigned the value of a default message when the class is
            instantiated without a custom message.

    """
    def __init__(self, message: str = "Client is None.") -> None:
        """
        Initializes the MissingClientError instance with a custom error message.
        It sets the instance variable `message` to the provided string and passes
        this message to the parent Exception class's `__init__` method.

        Args:
            message (str): Optional. It defaults to the string "Client is None."
                if not provided.

        """
        self.message = message
        super().__init__(self.message)
