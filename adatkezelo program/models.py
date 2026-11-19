import datetime
from dataclasses import dataclass, field

@dataclass
class Car:
    id: int = field()
    type: str = field()
    model: str = field()
    year: int = field()
    plate: str = field()
    cost_category_id: int = field()

@dataclass
class Customer:
    id: int = field()
    first_name: str = field()
    last_name: str = field()
    date_of_birth: datetime.datetime = field()
    is_male: int = field()

@dataclass
class Rental:
    id: int = field()
    car_id: int = field()
    customer_id: int = field()
    rental_start: datetime.datetime = field()
    rental_end: datetime.datetime = field()

@dataclass
class CostCategory:
    id: int
    name: str
    price_per_day: float
    cost_per_km: float
    penalty_per_day_late: float


def parse_data(datas, Obj):
    result = []
    for data in datas:
        result.append(
            Obj(
                *data
            )
        )
    return result

