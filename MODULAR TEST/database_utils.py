import sqlite3
from PyQt5.QtGui import QStandardItem, QStandardItemModel
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QDateTime, QTime

# Utility Methods (shared across tabs)
def get_clients(cursor):
    """Fetch all client names."""
    cursor.execute("SELECT name FROM Clients")
    return [row[0] for row in cursor.fetchall()]

def get_dogs_by_client(cursor, client_name):
    """Fetch all dogs owned by a specific client."""
    client_id = get_client_id(cursor, client_name)
    cursor.execute("SELECT name FROM Dogs WHERE client_id = ?", (client_id,))
    return [row[0] for row in cursor.fetchall()]

def get_services(cursor):
    """Fetch all services."""
    cursor.execute("SELECT service_name FROM Services")
    return [row[0] for row in cursor.fetchall()]

def get_price_by_service(cursor, service_name):
    """Fetch the price of a service."""
    cursor.execute("""
        SELECT price FROM Prices WHERE service_id = 
        (SELECT service_id FROM Services WHERE service_name = ?)
    """, (service_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_client_id(cursor, client_name):
    """Fetch the client ID for a given client name."""
    cursor.execute("SELECT client_id FROM Clients WHERE name = ?", (client_name,))
    result = cursor.fetchone()
    return result[0] if result else None


def get_dog_id(cursor, dog_name):
    """Fetch the dog ID for a given dog name."""
    cursor.execute("SELECT dog_id FROM Dogs WHERE name = ?", (dog_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_service_id_by_name(cursor, service_name):
    """Fetch the service ID for a given service name."""
    cursor.execute("SELECT service_id FROM Services WHERE service_name = ?", (service_name,))
    result = cursor.fetchone()
    return result[0] if result else None

def get_price_id_by_service_id(cursor, service_id):
    """Fetch the price ID for a given service ID."""
    cursor.execute("SELECT price_id FROM Prices WHERE service_id = ?", (service_id,))
    result = cursor.fetchone()
    return result[0] if result else None

def refresh_schedule_table(schedule_model, conn):
    """Fetches updated schedules from the database and refreshes the UI table."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT Clients.name, Dogs.name, Services.service_name, Schedules.date, Schedules.time, Prices.price
            FROM Schedules
            JOIN Clients ON Schedules.client_id = Clients.client_id
            JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
            JOIN Services ON Schedules.service_id = Services.service_id
            JOIN Prices ON Schedules.price_id = Prices.price_id
            """
        )
        results = cursor.fetchall()

        # Clear the existing table
        schedule_model.removeRows(0, schedule_model.rowCount())

        # Populate with new data
        for row in results:
            items = [QStandardItem(str(item)) for item in row]
            schedule_model.appendRow(items)

    except Exception as e:
        print(f"Error refreshing schedule table: {e}")

