from pydantic import BaseModel, ConfigDict
from datetime import datetime, date

class BatchModel(BaseModel):
    model_config = ConfigDict(from_attributes=True) 

class BatchCreate(BatchModel):
    is_closed: bool 
    task_description: str 
    #work_center
    shift: str
    team: str 
    ekn_code: str
    batch_number: int 
    batch_date: date
    nomenclature: str
    #work_center_id
    shift_start: datetime
    shift_end: datetime

class BatchResponse(BatchModel):
    id: int
    is_closed: bool
    batch_number: int 
    batch_date: date 
    #products сделать потом




# json
# [
# {
# "СтатусЗакрытия": false,
# "ПредставлениеЗаданияНаСмену": "Изготовить 1000 болтов М10",
# "РабочийЦентр": "Цех №1",
# "Смена": "1 смена",
# "Бригада": "Бригада Иванова",
# "НомерПартии": 22222,
# "ДатаПартии": "2024-01-30",
# "Номенклатура": "Болт М10х50",
# "КодЕКН": "EKN-12345",
# "ИдентификаторРЦ": "RC-001",
# "ДатаВремяНачалаСмены": "2024-01-30T08:00:00",
# "ДатаВремяОкончанияСмены": "2024-01-30T20:00:00"
# }
# ]