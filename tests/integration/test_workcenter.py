from src.data.models.work_center import WorkCenter 

async def test_create_work_center(create_work_center):
    assert create_work_center.id is not None
    assert create_work_center.identifier == "wc_test"
    assert create_work_center.name == "test_work_center"