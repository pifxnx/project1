from ...core.exceptions import (
    NotFoundException,
    AlreadyExistsException
)

class ProductNotFoundException(NotFoundException):
    def __init__(self, product_id: int):
        super().__init__(f"Product {product_id} not found")


class ProductAlreadyExistsException(AlreadyExistsException):
    def __init__(self):
        super().__init__(f"Product already exists")