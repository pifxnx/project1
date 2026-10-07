from ...core.exceptions import AppException, NotFoundException, AlreadyExistsException


class BatchNotFoundException(NotFoundException):
    def __init__(self, batch_id: int):
        super().__init__(f"Batch {batch_id} not found")


class BatchAlreadyExistsException(AlreadyExistsException):
    def __init__(self):
        super().__init__("Batch already exists")


class BatchInvalidShiftPeriodException(AppException):
    def __init__(self, batch_id: int):
        super().__init__(f"Batch {batch_id} has an invalid shift period", 409)
