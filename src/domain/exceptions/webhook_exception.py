from ...core.exceptions import (
    NotFoundException,
    AlreadyExistsException
)

class WebhookSubscriptionNotFoundException(
    NotFoundException
):
    def __init__(self, sub_id: int):
        super().__init__(f"Webhook subscription {sub_id} not found")


class WebhookSubscriptionAlreadyExistsException(
    AlreadyExistsException
):
    def __init__(self):
        super().__init__("Webhook subscription already exists")



class WebhookDeliveryNotFoundException(
    NotFoundException
):
    def __init__(self, del_id: int):
        super().__init__(f"Webhook delivery {del_id} not found")


class WebhookDeliveryAlreadyExistsException(
    AlreadyExistsException
):
    def __init__(self):
        super().__init__("Webhook delivery already exists")