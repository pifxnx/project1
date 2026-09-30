from ...core.exceptions import NotFoundException


class WorkCenterNotFoundException(NotFoundException):
    def __init__(self, work_center_id: int):
        super().__init__(f"Work center {work_center_id} not found")
