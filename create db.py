import sqlite3

def initialize_database():
    # Connect to SQLite database (or create it if it doesn't exist)
    conn = sqlite3.connect("canine_haircut_service.db")
    cursor = conn.cursor()

    # Create Clients table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clients (
        client_id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT UNIQUE NOT NULL
    );
    ''')

    # Create Dogs table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Dogs (
        dog_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        name TEXT NOT NULL,
        breed TEXT,
        notes TEXT,
        FOREIGN KEY (client_id) REFERENCES Clients(client_id) ON DELETE CASCADE
    );
    ''')

    # Create Services table to store types of services (e.g., grooming, haircut)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Services (
        service_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_name TEXT NOT NULL UNIQUE
    );
    ''')

    # Create Prices table to store prices for services
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Prices (
        price_id INTEGER PRIMARY KEY AUTOINCREMENT,
        service_id INTEGER NOT NULL,
        price REAL NOT NULL,
        FOREIGN KEY (service_id) REFERENCES Services(service_id)
    );
    ''')

    # Create Schedules table (using foreign keys for services and prices)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Schedules (
        schedule_id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER NOT NULL,
        dog_id INTEGER NOT NULL,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        service_id INTEGER NOT NULL,
        price_id INTEGER NOT NULL,
        FOREIGN KEY (client_id) REFERENCES Clients(client_id),
        FOREIGN KEY (dog_id) REFERENCES Dogs(dog_id),
        FOREIGN KEY (service_id) REFERENCES Services(service_id),
        FOREIGN KEY (price_id) REFERENCES Prices(price_id),
        CHECK (date != ''),  -- Ensure date is not empty
        CHECK (time != '')   -- Ensure time is not empty
    );
    ''')
    # Crea tabla empleados
    cursor.execute('''  
    CREATE TABLE IF NOT EXISTS Employees (  
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,  
        username TEXT NOT NULL UNIQUE,  
        password TEXT NOT NULL,  
        role TEXT NOT NULL,  
        email TEXT NOT NULL UNIQUE,  
        CHECK (username != ''),  
        CHECK (password != ''),  
        CHECK (role != ''),      
        CHECK (email != '')     
    );  
''')  
    
    # Create Expenses table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Expenses (
        expense_id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        CHECK (amount >= 0)  -- Ensure that expenses can't have negative values
    );
    ''')

    # Create indexes on frequently queried columns
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_client_id ON Schedules(client_id);')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_dog_id ON Schedules(dog_id);')

    # Commit changes within a transaction
    try:
        conn.commit()
    except Exception as e:
        print(f"Error committing changes: {e}")
        conn.rollback()
    try:  
        cursor.execute('''  
            INSERT INTO Employees (username, password, role, email)  
            VALUES (?, ?, ?, ?);  
        ''', ('DoGroomy', '1234', 'Supervisor', 'info-DoGroomy@gmail.com'))  

        conn.commit()  # Guarda los cambios  
        print("Empleado insertado correctamente.")  

    except sqlite3.IntegrityError:  
        print("Error: ya existe un empleado con este username o email.")  
    except Exception as e:  
        print(f"Ocurrió un error: {e}")  

    # Close the connection
    conn.close()

if __name__ == "__main__":
    initialize_database()
    print("Database initialized successfully!")
