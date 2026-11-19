
from faker import Faker
from faker_vehicle import VehicleProvider
from models import Car, Customer, Rental, CostCategory
import random
from datetime import datetime, timedelta
import math


def generate_cars(n: int, category_distribution):
    if n is None:
        n = 1000
    if category_distribution is None:
        category_distribution = [50, 10, 5, 35]

    assert n >= 0
    assert sum(category_distribution) == 100

    fake_plate = Faker('hu_HU')
    fake_plate.add_provider(VehicleProvider)
    fake_plate = fake_plate.unique

    fake = Faker()
    fake.add_provider(VehicleProvider)

    cars = []

    for i in range(n):
        curr = fake.vehicle_year_make_model().split(' ')
        while len(curr) != 3:
            curr = fake.vehicle_year_make_model().split(' ')

        year, make, model = curr

        num = int(random.random() * 100)
        s = 0
        cost_category_id = None
        for k, val in enumerate(category_distribution):
            s += val
            if num <= s:
                cost_category_id = k
                break

        cars.append(Car(
            id=i,
            type=make,
            model=model,
            year=year,
            plate=fake_plate.license_plate(),
            cost_category_id=cost_category_id
        ))

    return cars


def generate_customers(n: int, male_ratio: float, customers_locale: str):
    n = n if n else 1000
    male_ratio = male_ratio if male_ratio else 0.5
    customers_locale = customers_locale if customers_locale else 'hu_HU'

    assert n >= 0
    assert 0 <= male_ratio <= 1

    fake = Faker(customers_locale)
    customers = []

    for i in range(n):
        start_date = datetime.strptime('1950.01.01', '%Y.%m.%d')
        end_date = datetime.strptime('2025.12.31', '%Y.%m.%d')

        is_male = random.random() < male_ratio

        customers.append(
            Customer(
                id = i,
                first_name = fake.first_name_male() if is_male else fake.first_name_female(),
                last_name = fake.last_name(),
                date_of_birth = start_date + timedelta(days=random.randrange((end_date - start_date).days)),
                is_male = is_male
            )
        )

    return customers

def generate_costcategories():
    categories = []
    categories.append(
        CostCategory(
            id=0,
            name='olcso',
            price_per_day=30_000,
            cost_per_km=300,
            penalty_per_day_late=20000
        )
    )
    categories.append(
        CostCategory(
            id=1,
            name='alap',
            price_per_day=50_000,
            cost_per_km=400,
            penalty_per_day_late=30000
        )
    )
    categories.append(
        CostCategory(
            id=2,
            name='draga',
            price_per_day=100_000,
            cost_per_km=500,
            penalty_per_day_late=50000
        )
    )
    categories.append(
        CostCategory(
            id=3,
            name='luxus',
            price_per_day=200_000,
            cost_per_km=600,
            penalty_per_day_late=100000
        )
    )
    return categories

