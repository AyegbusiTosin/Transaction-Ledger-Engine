#categorizing error exceptions

#class 'errorname'(Exception)- this means create a new class called 'errorname', based on Exception (inheritance)

class SenderNotFoundError(Exception):
    pass

class ReceiverNotFoundError(Exception):
    pass

class InsufficientFundsError(Exception):
    pass

class IdempotencyConflictError(Exception):
    pass


