import tkinter as tk
from tkinter import ttk
from main import *
from dataclasses import asdict
from tkinter import messagebox, filedialog
import os


class Table:
    def __init__(self, frame, fields, datas):
        self.frame = frame

        self.fields = fields
        self.datas = datas

    def show(self, row=0, column=0):
        clear_frame(self.frame)

        tree_scroll = tk.Scrollbar(self.frame)
        tree = ttk.Treeview(
            self.frame,
            columns=self.fields,
            show='headings',
            yscrollcommand=tree_scroll.set
        )
        tree_scroll.config(command=tree.yview)

        for field in self.fields:
            tree.heading(field, text=field)
            tree.column(field, width=100, anchor='center')

        for data in self.datas:
            data = asdict(data)
            values = [data[field] for field in self.fields]
            tree.insert('', 'end', values=values)

        tree.grid(row=row, column=column, sticky='nsew')
        tree_scroll.grid(row=row, column=column + 1, sticky='ns')

        self.frame.grid_rowconfigure(row, weight=1)
        self.frame.grid_columnconfigure(column, weight=1)


class InputWithHint:
    def __init__(self, root, hint):
        self.hint = hint
        self.entry = tk.Entry(root)
        self.entry.insert(0, self.hint)
        self.entry.bind("<FocusIn>", self.on_focus_in)
        self.entry.bind("<FocusOut>", self.on_focus_out)

    def get(self):
        self.entry.get_val = lambda: self.entry.get() if self.entry.get() != self.hint else None
        return self.entry

    def on_focus_in(self, event):
        if self.entry.get() == self.hint:
            self.entry.delete(0, tk.END)

    def on_focus_out(self, event):
        if self.entry.get() == "":
            self.entry.insert(0, self.hint)


def clear_frame(frame):
    for widget in frame.winfo_children():
        widget.destroy()

def show_page(frame):
    global current_frame
    if current_frame is not None:
        current_frame.pack_forget()
    current_frame = frame
    current_frame.pack(fill='both', expand=True)


def add_io_buttons(frame, entity, refresh, row):
    def do_export(kind):
        ext = {'csv': '.csv', 'json': '.json', 'xlsx': '.xlsx'}[kind]
        full_path = filedialog.asksaveasfilename(
            initialfile=f'{entity}{ext}',
            defaultextension=ext,
            filetypes=[(kind.upper(), f'*{ext}'), ('All files', '*.*')]
        )
        if not full_path:
            return
        folder, file_name = os.path.split(full_path)
        try:
            result = export_entity(entity, folder, kind, file_name)
            messagebox.showinfo(result['status'], result['message'])
        except Exception as e:
            messagebox.showerror('error', str(e))

    def do_import(kind):
        ext = {'csv': '.csv', 'json': '.json', 'xlsx': '.xlsx'}[kind]
        full_path = filedialog.askopenfilename(
            filetypes=[(kind.upper(), f'*{ext}'), ('All files', '*.*')]
        )
        if not full_path:
            return
        folder, file_name = os.path.split(full_path)
        try:
            result = import_entity(entity, folder, kind, file_name)
            if result['status'] == 'success':
                messagebox.showinfo(result['status'], result['message'])
            else:
                messagebox.showerror(result['status'], result['message'])
            refresh()
        except Exception as e:
            messagebox.showerror('error', str(e))

    tk.Button(frame, text='Export CSV', command=lambda: do_export('csv')).grid(row=row, column=3, sticky='w')
    tk.Button(frame, text='Export Excel', command=lambda: do_export('xlsx')).grid(row=row, column=4, sticky='w')
    tk.Button(frame, text='Export JSON', command=lambda: do_export('json')).grid(row=row, column=5, sticky='w')
    tk.Button(frame, text='Import CSV', command=lambda: do_import('csv')).grid(row=row + 1, column=3, sticky='w')
    tk.Button(frame, text='Import Excel', command=lambda: do_import('xlsx')).grid(row=row + 1, column=4, sticky='w')
    tk.Button(frame, text='Import JSON', command=lambda: do_import('json')).grid(row=row + 1, column=5, sticky='w')


def show_cars():
    def add_car_command():
        result = add_car(
            car_type.get_val(),
            model.get_val(),
            year.get_val(),
            plate.get_val(),
            cost_category_id.get_val(),
        )
        if result['status'] == 'success':
            messagebox.showinfo(result['status'], result['message'])
            show_cars()
        else:
            messagebox.showerror(result['status'], result['message'])

    show_page(cars_frame)
    table = Table(cars_frame, ['id', 'type', 'model', 'year', 'plate', 'cost_category_id'], get_cars())
    table.show()

    tk.Label(cars_frame, text='Add new car').grid(row=1, column=0, sticky='w')

    car_type = InputWithHint(cars_frame, 'Type').get()
    car_type.grid(row=2, column=0, sticky='ew')

    model = InputWithHint(cars_frame, 'Model').get()
    model.grid(row=3, column=0, sticky='ew')

    year = InputWithHint(cars_frame, 'Year').get()
    year.grid(row=4, column=0, sticky='ew')

    plate = InputWithHint(cars_frame, 'Plate').get()
    plate.grid(row=5, column=0, sticky='ew')

    cost_category_id = InputWithHint(cars_frame, 'Cost category id').get()
    cost_category_id.grid(row=6, column=0, sticky='ew')

    tk.Button(cars_frame, text='Submit', command=add_car_command).grid(row=7, column=0, sticky='w')
    add_io_buttons(cars_frame, 'cars', show_cars, row=8)

def show_customers():
    def add_customer_command():
        result = add_customer(
            first_name.get_val(),
            last_name.get_val(),
            date_of_birth.get_val(),
            is_male.get_val(),
        )
        if result['status'] == 'success':
            messagebox.showinfo(result['status'], result['message'])
            show_customers()
        else:
            messagebox.showerror(result['status'], result['message'])

    show_page(customers_frame)
    table = Table(customers_frame, ['id', 'first_name', 'last_name', 'date_of_birth', 'is_male'], get_customers())
    table.show()

    tk.Label(customers_frame, text='Add new customer').grid(row=1, column=0, sticky='w')

    first_name = InputWithHint(customers_frame, 'First name').get()
    first_name.grid(row=2, column=0, sticky='ew')

    last_name = InputWithHint(customers_frame, 'Last name').get()
    last_name.grid(row=3, column=0, sticky='ew')

    date_of_birth = InputWithHint(customers_frame, 'Date of birth (YYYY.MM.DD)').get()
    date_of_birth.grid(row=4, column=0, sticky='ew')

    is_male = InputWithHint(customers_frame, 'Is male (1/0)').get()
    is_male.grid(row=5, column=0, sticky='ew')

    tk.Button(customers_frame, text='Submit', command=add_customer_command).grid(row=6, column=0, sticky='w')
    add_io_buttons(customers_frame, 'customers', show_customers, row=7)


def show_costcategories():
    def update():
        update_cost_category(cat_id.get_val(), new_name.get_val(), new_price_per_day.get_val(),
                             new_cost_per_km.get_val(), new_penalty_per_day.get_val())
        show_costcategories()

    show_page(costcategories_frame)
    table = Table(costcategories_frame, ['id', 'name', 'price_per_day', 'cost_per_km', 'penalty_per_day_late'], get_costcategories())
    table.show(row=0, column=0)

    cat_id = InputWithHint(costcategories_frame, 'Category id').get()
    cat_id.grid(row=1, column=0, sticky='ew')

    new_name = InputWithHint(costcategories_frame, 'Name').get()
    new_name.grid(row=2, column=0, sticky='ew')

    new_price_per_day = InputWithHint(costcategories_frame, 'Price per day').get()
    new_price_per_day.grid(row=3, column=0, sticky='ew')

    new_cost_per_km = InputWithHint(costcategories_frame, 'Cost per km').get()
    new_cost_per_km.grid(row=4, column=0, sticky='ew')

    new_penalty_per_day = InputWithHint(costcategories_frame, 'Penalty per day late').get()
    new_penalty_per_day.grid(row=5, column=0, sticky='ew')

    tk.Button(costcategories_frame, text='Submit', command=update).grid(row=6, column=0, sticky='w', columnspan=5)


def show_rentals():
    def add_rental_command():
        result = add_rental(car_id.get_val(), customer_id.get_val(), rental_start.get_val(), rental_end.get_val())
        if result['status'] == 'success':
            messagebox.showinfo(result['status'], result['message'])
            show_rentals()
        else:
            messagebox.showerror(result['status'], result['message'])

    def end_rental_command():
        result = end_rental(rental_id.get_val(), kms.get_val())
        if result['status'] == 'success':
            messagebox.showinfo(result['status'], result['message'])
            show_rentals()
        else:
            messagebox.showerror(result['status'], result['message'])

    show_page(rentals_frame)
    table = Table(rentals_frame, ['id', 'car_id', 'customer_id', 'rental_start', 'rental_end'], get_rentals())
    table.show(row=0, column=0)

    tk.Label(rentals_frame, text='Add new rental').grid(row=1, column=0, sticky='w')

    car_id = InputWithHint(rentals_frame, 'Car id').get()
    car_id.grid(row=2, column=0, sticky='ew')

    customer_id = InputWithHint(rentals_frame, 'Customer id').get()
    customer_id.grid(row=3, column=0, sticky='ew')

    rental_start = InputWithHint(rentals_frame, 'Start date (YYYY.MM.DD)').get()
    rental_start.grid(row=4, column=0, sticky='ew')

    rental_end = InputWithHint(rentals_frame, 'End date (YYYY.MM.DD)').get()
    rental_end.grid(row=5, column=0, sticky='ew')

    tk.Button(rentals_frame, text='Submit', command=add_rental_command).grid(row=6, column=0, sticky='w')


    tk.Label(rentals_frame, text='End rental').grid(row=1, column=2)

    rental_id = InputWithHint(rentals_frame, 'Rental id').get()
    rental_id.grid(row=2, column=2)

    kms = InputWithHint(rentals_frame, 'Km change').get()
    kms.grid(row=3, column=2)

    tk.Button(rentals_frame, text='Submit', command=end_rental_command).grid(row=4, column=2)

    add_io_buttons(rentals_frame, 'rentals', show_rentals, row=7)


def show_initialize():
    show_page(initialize_frame)

    n_cars = InputWithHint(initialize_frame, 'Num of cars {1000}').get()
    n_cars.grid(row=0, column=0, sticky='ew')

    category_distribution = InputWithHint(initialize_frame, 'Cost dist {25,25,25,25}').get()
    category_distribution.grid(row=1, column=0, sticky='ew')

    n_customers = InputWithHint(initialize_frame, 'Num of customers {1000}').get()
    n_customers.grid(row=0, column=1, sticky='ew')

    male_ratio = InputWithHint(initialize_frame, 'Male ratio {0.5}').get()
    male_ratio.grid(row=1, column=1, sticky='ew')

    customers_locale = InputWithHint(initialize_frame, 'Customers locale {hu_HU}').get()
    customers_locale.grid(row=2, column=1, sticky='ew')

    tk.Button(initialize_frame, text='Submit', command=lambda: generate_cars_and_customers_and_categories(n_cars.get_val(), n_customers.get_val(), male_ratio.get_val(), category_distribution.get_val(), customers_locale.get_val())).grid(row=7, column=0, columnspan=2)



window = tk.Tk()
window.geometry('1000x600')
window.resizable(False, False)

home = tk.Frame(master=window)
home.pack(fill='x')

tk.Button(master=home, text='Cars', command=show_cars).grid(row=0, column=0)
tk.Button(master=home, text='Customers', command=show_customers).grid(row=0, column=1)
tk.Button(master=home, text='Rentals', command=show_rentals).grid(row=0, column=2)
tk.Button(master=home, text='Cost Categories', command=show_costcategories).grid(row=0, column=3)
tk.Button(master=home, text='Initialize tables', command=show_initialize).grid(row=0, column=4)

cars_frame = tk.Frame(master=window)
customers_frame = tk.Frame(master=window)
costcategories_frame = tk.Frame(master=window)
rentals_frame = tk.Frame(master=window)
initialize_frame = tk.Frame(master=window)

current_frame = None

window.mainloop()