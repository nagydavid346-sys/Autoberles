

import datetime
import oracledb
from models import Car, Customer, Rental, CostCategory
import pwinput

class SqlHandler:
    def __init__(self):
        pw = pwinput.pwinput(prompt="Enter password: ", mask="#")

        self.connection = oracledb.connect(
            user="U_A9AM11",
            password=pw,
            dsn="codd.inf.unideb.hu:1521/ora21cp.inf.unideb.hu")

        self.cursor = self.connection.cursor()

        self.tables = ['cars', 'customers', 'rentals', 'costcategories']


    def ensure_tables(self):
        try:
            self.cursor.execute("""
            create table cars (
                id number primary key,
                type varchar2(30),
                model varchar2(30),
                year number,
                plate varchar2(10),
                cost_category_id varchar2(30)
            )
            """)
            print('Cars table created!')
        except oracledb.DatabaseError as e:
            print('Cars table already exists!')

        try:
            self.cursor.execute("""
                create table customers (
                    id number primary key,
                    first_name varchar2(30),
                    last_name varchar2(30),
                    date_of_birth date,
                    is_male number(1))
            """)
            print('Customers table created!')
        except oracledb.DatabaseError as e:
            print('Customers table already exists!')

        try:
            self.cursor.execute("""
                create table rentals (
                    id number primary key,
                    car_id number,
                    customer_id number,
                    rental_start date,
                    rental_end date)
            """)
            print('Rentals table created!')
        except oracledb.DatabaseError as e:
            print('Rentals table already exists!')

        try:
            self.cursor.execute("""
                create table costcategories (
                    id number primary key,
                    name varchar2(20),
                    price_per_day number,
                    cost_per_km number,
                    penalty_per_day_late number)
            """)
            print('Costcategories table created!')
        except oracledb.DatabaseError as e:
            print('Costcategories table already exists!')

        self.connection.commit()

    def drop_all(self):
        for table in self.tables:
            table = table.capitalize()
            try:
                self.cursor.execute(f"""
                    drop table {table}
                """)
                print(table, 'dropped')
            except Exception as e:
                print(table, 'does not exist')

        self.connection.commit()

    def add_car(self, car: Car):
        self.cursor.execute(f'''
            insert into cars (id, type, model, year, plate, cost_category_id) values (:id, :type, :model, :year, :plate, :cost_category_id)
        ''', id = car.id, type = car.type, model = car.model, year = car.year, plate = car.plate, cost_category_id = car.cost_category_id)

        self.connection.commit()

    def add_customer(self, customer: Customer):
        self.cursor.execute('''
            insert into customers (id, first_name, last_name, date_of_birth, is_male) values (:id, :first_name, :last_name, :date_of_birth, :is_male)
        ''', id=customer.id, first_name=customer.first_name, last_name=customer.last_name, date_of_birth=customer.date_of_birth, is_male=customer.is_male)

        self.connection.commit()

    def add_rental(self, rental: Rental):
        self.cursor.execute(f'''
            insert into rentals (id, car_id, customer_id, rental_start, rental_end) values (:id, :car_id, :customer_id, :rental_start, :rental_end)
        ''', id=rental.id, car_id=rental.car_id, customer_id=rental.customer_id, rental_start=rental.rental_start, rental_end=rental.rental_end)

        self.connection.commit()

    def add_costcategory(self, costcategory: CostCategory):
        self.cursor.execute(f'''
            insert into costcategories (id, name, price_per_day, cost_per_km, penalty_per_day_late) values (:id, :name, :price_per_day, :cost_per_km, :penalty_per_day_late)
        ''', id=costcategory.id, name=costcategory.name, price_per_day=costcategory.price_per_day, cost_per_km=costcategory.cost_per_km, penalty_per_day_late=costcategory.penalty_per_day_late)

        self.connection.commit()

    def fill_cars(self, cars):
        self.cursor.executemany("insert into cars (id, type, model, year, plate, cost_category_id) values(:id, :type, :model, :year, :plate, :cost_category_id)",
                                [[car.id, car.type, car.model, car.year, car.plate, car.cost_category_id] for car in cars])
        self.connection.commit()

    def fill_customers(self, customers):
        self.cursor.executemany("insert into customers (id, first_name, last_name, date_of_birth, is_male) values (:id, :first_name, :last_name, :date_of_birth, :is_male)",
                                [[customer.id, customer.first_name, customer.last_name, customer.date_of_birth, customer.is_male] for customer in customers])
        self.connection.commit()

    def fill_costcategories(self, categories):
        self.cursor.executemany("insert into costcategories (id, name, price_per_day, cost_per_km, penalty_per_day_late) values (:id, :name, :price_per_day, :cost_per_km, :penalty_per_day_late)",
                                [[category.id, category.name, category.price_per_day, category.cost_per_km, category.penalty_per_day_late] for category in categories])
        self.connection.commit()

    def fill_rentals(self, rentals):
        self.cursor.executemany(
            "insert into rentals (id, car_id, customer_id, rental_start, rental_end) values (:id, :car_id, :customer_id, :rental_start, :rental_end)",
            [[rental.id, rental.car_id, rental.customer_id, rental.rental_start, rental.rental_end] for rental in rentals]
        )
        self.connection.commit()

    def clear_table(self, table: str):
        if table not in self.tables:
            raise ValueError(f'Unknown table: {table}')
        self.cursor.execute(f'delete from {table}')

    def read_table(self, table: str):
        self.cursor.execute(f'''
            select * from {table} order by id
        ''')
        return self.cursor.fetchall()

    def get_max_id(self, table: str):
        self.cursor.execute(f'''
            select max(id) from {table}
        ''')
        return self.cursor.fetchall()[0][0]

    def is_car_rented(self, car_id: int):
        self.cursor.execute(f'''
            select * from rentals where car_id = {car_id}
        ''')
        return len(self.cursor.fetchall()) != 0

    def does_id_exist_in_table(self, table: str, id: int):
        self.cursor.execute(f'''
            select * from {table} where id = {id}
        ''')
        return len(self.cursor.fetchall()) != 0

    def get_row_by_id(self, table: str, id: int):
        self.cursor.execute(f'''
            select * from {table} where id = {id}
        ''')
        return self.cursor.fetchall()

    def remove_row_by_id(self, table: str, id: int):
        self.cursor.execute(f'''
            delete from {table} where id = {id}
        ''')

    def update_row(self, table: str, id: int, fields: list[str], new_vals: list):
        set = ''
        i = 0
        for field, val in zip(fields, new_vals):
            if isinstance(field, str):
                set = set + f"{field} = '{val}'" + (',' if i != len(fields) - 1 else '')
            elif isinstance(field, int):
                set = set + f'{field} = {val}' + (',' if i != len(fields) - 1 else '')
            i += 1
        print(f'update {table} set {set} where id = {id}')
        self.cursor.execute(f'''
            update {table} set {set} where id = {id}
        ''')





