import datetime
import os
from sql import SqlHandler
from models import Car, Customer, Rental, CostCategory, parse_data
from generator import generate_cars, generate_customers, generate_costcategories
from file_io import (
    write_cars, read_cars, write_customers, read_customers, write_rentals, read_rentals,
    write_cars_json, read_cars_json, write_customers_json, read_customers_json,
    write_rentals_json, read_rentals_json,
    write_cars_excel, read_cars_excel, write_customers_excel, read_customers_excel,
    write_rentals_excel, read_rentals_excel,
)


def generate_cars_and_customers_and_categories(num_of_cars, num_of_customers, male_ratio, category_distribution, customers_locale):
    num_of_cars = int(num_of_cars) if num_of_cars else None
    num_of_customers = int(num_of_customers) if num_of_customers else None
    male_ratio = float(male_ratio) if male_ratio else None
    cost_category_dist = [int(x) for x in category_distribution.split(',')] if category_distribution else None
    customers_locale = customers_locale if customers_locale else None

    sqlhandler.drop_all()
    sqlhandler.ensure_tables()

    cars = generate_cars(num_of_cars, cost_category_dist)
    sqlhandler.fill_cars(cars)

    customers = generate_customers(num_of_customers, male_ratio, customers_locale)
    sqlhandler.fill_customers(customers)

    categories = generate_costcategories()
    sqlhandler.fill_costcategories(categories)



def get_cars():
    return parse_data(sqlhandler.read_table('cars'), Car)

def get_customers():
    return parse_data(sqlhandler.read_table('customers'), Customer)

def get_costcategories():
    return parse_data(sqlhandler.read_table('costcategories'), CostCategory)

def get_rentals():
    return parse_data(sqlhandler.read_table('rentals'), Rental)


def export_entity(entity, path, kind='csv', file_name=None):
    writers = {
        ('cars', 'csv'): write_cars,
        ('customers', 'csv'): write_customers,
        ('rentals', 'csv'): write_rentals,
        ('cars', 'json'): write_cars_json,
        ('customers', 'json'): write_customers_json,
        ('rentals', 'json'): write_rentals_json,
        ('cars', 'xlsx'): write_cars_excel,
        ('customers', 'xlsx'): write_customers_excel,
        ('rentals', 'xlsx'): write_rentals_excel,
    }
    getters = {
        'cars': get_cars,
        'customers': get_customers,
        'rentals': get_rentals,
    }
    writers[(entity, kind)](getters[entity](), path, file_name)
    saved = os.path.join(path, file_name) if file_name else path
    return {'status': 'success', 'message': f'Exported {entity} to {saved}'}


def import_entity(entity, path, kind='csv', file_name=None):
    readers = {
        ('cars', 'csv'): read_cars,
        ('customers', 'csv'): read_customers,
        ('rentals', 'csv'): read_rentals,
        ('cars', 'json'): read_cars_json,
        ('customers', 'json'): read_customers_json,
        ('rentals', 'json'): read_rentals_json,
        ('cars', 'xlsx'): read_cars_excel,
        ('customers', 'xlsx'): read_customers_excel,
        ('rentals', 'xlsx'): read_rentals_excel,
    }
    fillers = {
        'cars': sqlhandler.fill_cars,
        'customers': sqlhandler.fill_customers,
        'rentals': sqlhandler.fill_rentals,
    }
    objects = readers[(entity, kind)](path, file_name) if file_name else readers[(entity, kind)](path)
    try:
        sqlhandler.clear_table(entity)
        if objects:
            fillers[entity](objects)
        else:
            sqlhandler.connection.commit()
    except Exception as e:
        sqlhandler.connection.rollback()
        return {'status': 'error', 'message': str(e)}
    return {'status': 'success', 'message': f'Replaced {entity} with {len(objects)} rows'}

def _next_id(table):
    max_id = sqlhandler.get_max_id(table)
    if max_id is None:
        max_id = -1
    return max_id + 1


def add_car(car_type, model, year, plate, cost_category_id):
    if not all([car_type, model, year, plate, cost_category_id]):
        return {'status': 'error', 'message': 'Fill in every car field!'}

    year = int(year)
    cost_category_id = int(cost_category_id)

    if not sqlhandler.does_id_exist_in_table('costcategories', cost_category_id):
        return {'status': 'error', 'message': 'Cost category does not exist!'}

    car = Car(
        id=_next_id('cars'),
        type=car_type,
        model=model,
        year=year,
        plate=plate,
        cost_category_id=cost_category_id,
    )
    sqlhandler.add_car(car)
    return {'status': 'success', 'message': f'Car({car.id}) has been added!'}


def add_customer(first_name, last_name, date_of_birth, is_male):
    if not all([first_name, last_name, date_of_birth, is_male is not None]):
        return {'status': 'error', 'message': 'Fill in every customer field!'}

    date_of_birth = datetime.datetime.strptime(date_of_birth, '%Y.%m.%d')
    is_male_text = str(is_male).strip().lower()
    if is_male_text in ('1', 'true', 'male', 'm'):
        is_male = 1
    elif is_male_text in ('0', 'false', 'female', 'f'):
        is_male = 0
    else:
        return {'status': 'error', 'message': 'is_male must be 1 or 0'}

    customer = Customer(
        id=_next_id('customers'),
        first_name=first_name,
        last_name=last_name,
        date_of_birth=date_of_birth,
        is_male=is_male,
    )
    sqlhandler.add_customer(customer)
    return {'status': 'success', 'message': f'Customer({customer.id}) has been added!'}


def add_rental(car_id, customer_id, rental_start, rental_end):
    car_id = int(car_id)
    customer_id = int(customer_id)
    rental_start = datetime.datetime.strptime(rental_start, '%Y.%m.%d')
    rental_end = datetime.datetime.strptime(rental_end, '%Y.%m.%d')

    if not sqlhandler.does_id_exist_in_table('cars', car_id):
        return {'status': 'error', 'message': 'Car does not exist!'}

    if not sqlhandler.does_id_exist_in_table('customers', customer_id):
        return {'status': 'error', 'message': 'Customer does not exist!'}

    if sqlhandler.is_car_rented(car_id):
        return {'status': 'error', 'message': 'Car already rented out!'}

    max_id = sqlhandler.get_max_id('rentals')
    if max_id is None:
        max_id = -1

    rental = Rental(
        id=max_id + 1,
        car_id=car_id,
        customer_id=customer_id,
        rental_start=rental_start,
        rental_end=rental_end
    )

    sqlhandler.add_rental(rental)

    return {'status': 'success', 'message': f'Car({car_id}) has been rented out for customer({customer_id})!'}


def format_amount(amount):
    amount = str(amount)
    new_amount = ''
    i = 1
    for char in amount[::-1]:
        new_amount += char
        if i % 3 == 0 and i != len(amount):
            new_amount += ','
        i += 1

    return new_amount[::-1] + 'HUF'


def end_rental(rental_id, km):
    rental_id = int(rental_id)
    km = int(km)

    if not sqlhandler.does_id_exist_in_table('rentals', rental_id):
        return {'status': 'error', 'message': 'Rental does not exist!'}

    rental = parse_data(sqlhandler.get_row_by_id('rentals', rental_id), Rental)[0]
    car = parse_data(sqlhandler.get_row_by_id('cars', rental.car_id), Car)[0]
    customer = parse_data(sqlhandler.get_row_by_id('customers', rental.customer_id), Customer)[0]
    costcategory = parse_data(sqlhandler.get_row_by_id('costcategories', car.cost_category_id), CostCategory)[0]

    sqlhandler.remove_row_by_id('rentals', rental_id)

    days_late = max(0, (datetime.datetime.now() - rental.rental_end).days)

    days_between = (rental.rental_end - rental.rental_start).days

    message = f'''
        Rental of car({car.id}) with customer({customer.id}) has ended with {km}km and {days_late} days late.
        The total cost is {days_between}days * {format_amount(costcategory.price_per_day)} + {km}km * {format_amount(costcategory.cost_per_km)} + {days_late}days late * {format_amount(costcategory.penalty_per_day_late)} = {format_amount(int(costcategory.price_per_day * days_between + km * costcategory.cost_per_km + days_late * costcategory.penalty_per_day_late))}
    '''

    return {'status': 'success', 'message': message}

def update_cost_category(id, name, price_per_day, cost_per_km, penalty_per_day):
    id = int(id)
    price_per_day = int(price_per_day) if price_per_day else None
    cost_per_km = int(cost_per_km) if cost_per_km else None
    penalty_per_day = int(penalty_per_day) if penalty_per_day else None

    assert 0 <= id <= 3

    fields = []
    vals = []
    if name:
        fields.append('name')
        vals.append(name)

    if price_per_day:
        fields.append('price_per_day')
        vals.append(price_per_day)

    if cost_per_km:
        fields.append('cost_per_km')
        vals.append(cost_per_km)

    if penalty_per_day:
        fields.append('penalty_per_day_late')
        vals.append(penalty_per_day)

    sqlhandler.update_row('costcategories', id, fields, vals)

    return {'status': 'success', 'message': 'Success'}


sqlhandler = SqlHandler()
sqlhandler.ensure_tables()