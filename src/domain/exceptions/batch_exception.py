from ...core.exceptions import (
    NotFoundException,
    AlreadyExistsException
)

class BatchNotFoundException(NotFoundException):
    def __init__(self, batch_id: int):
        super().__init__(f"Batch {batch_id} not found")

class BatchAlreadyExistsException(AlreadyExistsException):
    def __init__(self):
        super().__init__(f"Batch already exists")
