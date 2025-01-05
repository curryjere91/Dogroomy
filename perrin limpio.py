import sys
import sqlite3
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTabWidget,
    QLineEdit, QPushButton, QLabel, QComboBox, QMessageBox, QDateEdit, QTimeEdit, QCalendarWidget,
    QTableView, QDialog, QDialogButtonBox, QHeaderView, QInputDialog)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSignal, Qt, QModelIndex
from PyQt5.QtCore import pyqtSignal, Qt, QDate, QTime, QAbstractTableModel, Qt

class EditScheduleDialog(QDialog):
    def __init__(self, parent, client_name, dog_name, service_name, date, time, price):
        super().__init__(parent)
        self.setWindowTitle("Edit Schedule")
        layout = QFormLayout(self)

        self.client_dropdown = QComboBox()
        self.client_dropdown.addItems(parent.get_clients())
        self.client_dropdown.setCurrentText(client_name)
        self.client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)  # Connect signal
        layout.addRow("Client:", self.client_dropdown)

        self.dog_dropdown = QComboBox()
        self.update_dog_dropdown()  # Call to populate initially
        self.dog_dropdown.setCurrentText(dog_name)
        layout.addRow("Dog:", self.dog_dropdown)

        self.service_dropdown = QComboBox()
        self.service_dropdown.addItems(parent.get_services())
        self.service_dropdown.setCurrentText(service_name)
        self.service_dropdown.currentIndexChanged.connect(self.update_price_display)  # Connect signal
        layout.addRow("Service:", self.service_dropdown)

        self.price_label = QLabel(str(price))
        layout.addRow("Price:", self.price_label)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setSelectedDate(QDate.fromString(date, "dd-MM-yyyy"))
        layout.addRow("Date:", self.calendar_widget)

        self.time_edit = QTimeEdit()
        self.time_edit.setTime(QTime.fromString(time, "HH:mm"))
        layout.addRow("Time:", self.time_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def update_dog_dropdown(self):
        client_name = self.client_dropdown.currentText()
        dogs = self.parent().get_dogs_by_client(client_name)  # Access parent methods
        self.dog_dropdown.clear()
        self.dog_dropdown.addItems(dogs)

    def update_price_display(self):
        service_name = self.service_dropdown.currentText()
        price = self.parent().get_price_by_service(service_name)  # Access parent methods
        self.price_label.setText(str(price))

    def get_values(self):
        return (self.client_dropdown.currentText(), self.dog_dropdown.currentText(),
                self.service_dropdown.currentText(), self.calendar_widget.selectedDate().toString("dd-MM-yyyy"),
                self.time_edit.time().toString("HH:mm"))

class EditClientDialog(QDialog): # Define a custom dialog class
    def __init__(self, parent, name, phone):
        super().__init__(parent)
        self.setWindowTitle("Edit Client")
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(name)
        layout.addRow("Name:", self.name_edit)

        self.phone_edit = QLineEdit(phone)
        layout.addRow("Phone:", self.phone_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def get_values(self):
        return self.name_edit.text(), self.phone_edit.text()

class EditDogDialog(QDialog):  # New dialog for editing dogs
    def __init__(self, parent, name, breed, client_name):
        super().__init__(parent)
        self.setWindowTitle("Edit Dog")
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(name)
        layout.addRow("Name:", self.name_edit)

        self.breed_edit = QLineEdit(breed)
        layout.addRow("Breed:", self.breed_edit)

        self.client_dropdown = QComboBox()
        self.client_dropdown.addItems(parent.get_clients())  # Populate dropdown
        self.client_dropdown.setCurrentText(client_name) # Set current client
        layout.addRow("Client:", self.client_dropdown)


        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def get_values(self):
        return self.name_edit.text(), self.breed_edit.text(), self.client_dropdown.currentText()

class EditServiceDialog(QDialog):
    def __init__(self, parent, service_name, price):
        super().__init__(parent)
        self.setWindowTitle("Edit Service")
        layout = QFormLayout(self)

        self.service_name_edit = QLineEdit(service_name)
        layout.addRow("Service Name:", self.service_name_edit)

        self.price_edit = QLineEdit(str(price))  # Convert price to string
        layout.addRow("Price:", self.price_edit)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def get_values(self):
        return self.service_name_edit.text(), float(self.price_edit.text()) # Convert price back to float

class ScheduleTableModel(QAbstractTableModel): # Custom table model
    def __init__(self, data=None, headers=None, parent=None):
        super().__init__(parent)
        self._data = data or []
        self.headers = headers or []

    def rowCount(self, parent=QModelIndex()):
        return len(self._data)

    def columnCount(self, parent=QModelIndex()):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid() and role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self.headers[section]
        return None

    def update_data(self, new_data): # Method to update table data
        self.beginResetModel() # Begin model reset
        self._data = new_data
        self.endResetModel() # End model reset


class CanineHaircutApp(QMainWindow):

    schedule_updated = pyqtSignal() # New signal for schedule changes
    client_updated = pyqtSignal() # New signal for client changes
    dog_updated = pyqtSignal()   # New signal for dog changes
    service_updated = pyqtSignal() # New signal for service changes



    def __init__(self):
        super().__init__()

        # Initialize database connection
        self.conn = sqlite3.connect("canine_haircut_service.db")
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Canine Haircut Service")
        self.setGeometry(100, 100, 600, 400)

        # Create main layout and tabs
        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        self.create_client_tab()
        self.create_dog_tab()
        self.create_service_tab()
        self.create_schedule_tab()
        self.create_current_schedules_tab()

        self.client_updated.connect(self.update_all_client_dropdowns)
        self.client_updated.connect(self.refresh_client_table)
        self.dog_updated.connect(self.update_all_dog_dropdowns)
        self.dog_updated.connect(self.refresh_dog_table)
        self.service_updated.connect(self.update_all_service_dropdowns)
        self.service_updated.connect(self.refresh_service_table)
        self.schedule_updated.connect(self.refresh_schedule_table)

    def update_all_client_dropdowns(self):
        self.update_client_dropdown(self.dog_client_dropdown)
        self.update_client_dropdown(self.schedule_client_dropdown)

    def update_all_dog_dropdowns(self):
        self.update_dog_dropdown() # This function already updates based on selected client

    def update_all_service_dropdowns(self):
        self.update_service_dropdown()
# Client
    def create_client_tab(self):
        client_tab = QWidget()
        layout = QVBoxLayout() # Changed to QVBoxLayout




          # Client Input Form
        form_layout = QFormLayout()
        self.client_name_input = QLineEdit()
        self.client_phone_input = QLineEdit()
        add_client_button = QPushButton("Add Client")
        add_client_button.clicked.connect(self.add_client)

        form_layout.addRow("Client Name:", self.client_name_input)
        form_layout.addRow("Client Phone:", self.client_phone_input)
        form_layout.addRow(add_client_button)
        layout.addLayout(form_layout) # Add form layout to main layout


         # Search Bar
        self.client_search_bar = QLineEdit()
        self.client_search_bar.setPlaceholderText("Search Client Name or Phone")
        self.client_search_bar.textChanged.connect(self.search_clients)
        layout.addWidget(self.client_search_bar)

        # Client Table View
        self.client_table = QTableView()
        self.client_model = QStandardItemModel()
        self.client_table.setModel(self.client_model)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns to fill space


        # Edit Client Button
        edit_client_button = QPushButton("Edit Client")
        edit_client_button.clicked.connect(self.edit_client)
        layout.addWidget(edit_client_button) # Add button to layout


        # Delete Client Button
        delete_client_button = QPushButton("Delete Client")
        delete_client_button.clicked.connect(self.delete_client)
        layout.addWidget(delete_client_button)

        layout.addWidget(self.client_table)



        client_tab.setLayout(layout)
        self.tabs.addTab(client_tab, "Clients")
        self.refresh_client_table()

    def delete_client(self):
        selected_row = self.client_table.currentIndex().row()
        if selected_row >= 0:
            client_id = self.get_client_id_from_row(selected_row)
            if client_id:
                try:
                     # Confirmation dialog before deleting
                    confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this client? This will also delete associated dogs and schedules.", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        # Delete related schedules
                        self.cursor.execute("DELETE FROM Schedules WHERE client_id = ?", (client_id,))
                        # Delete related dogs
                        self.cursor.execute("DELETE FROM Dogs WHERE client_id = ?", (client_id,))
                        # Delete the client
                        self.cursor.execute("DELETE FROM Clients WHERE client_id = ?", (client_id,))
                        self.conn.commit()
                        self.refresh_client_table()
                        self.client_updated.emit() # Emit the signal to update other parts of the UI
                        QMessageBox.information(self, "Success", "Client, associated dogs, and schedules deleted successfully!")
                        self.refresh_dog_table()
                        self.refresh_schedule_table()
                except Exception as e:
                    print(f"Error deleting client: {e}")
                    QMessageBox.warning(self, "Error", "Failed to delete client.")

    def refresh_client_table(self, search_text=""):
        self.client_model.clear()
        self.client_model.setHorizontalHeaderLabels(["Name", "Phone"]) # Added ID column

        try:
            if search_text:
                query = "SELECT name, phone FROM Clients WHERE name LIKE ? OR phone LIKE ? ORDER BY client_id DESC"
                search_pattern = f"%{search_text}%"
                self.cursor.execute(query, (search_pattern, search_pattern))
            else:
                query = "SELECT name, phone FROM Clients ORDER BY client_id DESC" # Include client_id
                self.cursor.execute(query)

            for row in self.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.client_model.appendRow(row_data)
            self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch) # Stretch columns to fill space

        except Exception as e:
            print(f"Error refreshing client table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh client table.")

    def search_clients(self, text):
        self.refresh_client_table(search_text=text)

    def edit_client(self):
        selected_row = self.client_table.currentIndex().row()
        if selected_row >= 0:
            client_id = self.get_client_id_from_row(selected_row)
            if client_id:
                name, phone = self.get_client_name_phone(client_id)

                dialog = EditClientDialog(self, name, phone) # Create dialog instance
                if dialog.exec_() == QDialog.Accepted: # Show dialog and check result
                    new_name, new_phone = dialog.get_values() # Get values from dialog
                    self.update_client_in_db(client_id, new_name, new_phone)
                    self.refresh_client_table()

    def get_client_id_from_row(self, row):
        try:
            self.cursor.execute("SELECT client_id FROM Clients ORDER BY client_id DESC LIMIT 1 OFFSET ?", (row,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting client ID: {e}")
            return None

    def get_client_name_phone(self, client_id):
        try:
            self.cursor.execute("SELECT name, phone FROM Clients WHERE client_id = ?", (client_id,))
            result = self.cursor.fetchone()
            return result if result else (None, None)
        except Exception as e:
            print(f"Error getting client name and phone: {e}")
            return None, None

    def update_client_in_db(self, client_id, new_name, new_phone):
        try:
            self.cursor.execute("UPDATE Clients SET name = ?, phone = ? WHERE client_id = ?", (new_name, new_phone, client_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Client updated successfully!")
            self.client_updated.emit() # Emit the signal
        except Exception as e:
            print(f"Error updating client: {e}")
            QMessageBox.warning(self, "Error", "Failed to update client.")
# Dogs
    def create_dog_tab(self):
        dog_tab = QWidget()
        layout = QVBoxLayout()  # Change to QVBoxLayout

        # Dog Input Form
        form_layout = QFormLayout()
        self.dog_name_input = QLineEdit()
        self.dog_breed_input = QLineEdit()
        self.dog_client_dropdown = QComboBox()
        self.update_client_dropdown(self.dog_client_dropdown)

        add_dog_button = QPushButton("Add Dog")
        add_dog_button.clicked.connect(self.add_dog)

        form_layout.addRow("Dog Name:", self.dog_name_input)
        form_layout.addRow("Dog Breed:", self.dog_breed_input)
        form_layout.addRow("Select Client:", self.dog_client_dropdown)
        form_layout.addRow(add_dog_button)
        layout.addLayout(form_layout)  # Add form layout to main layout

        # Search Bar
        self.dogs_search_bar = QLineEdit()
        self.dogs_search_bar.setPlaceholderText("Search Dog, Breed or Client")
        self.dogs_search_bar.textChanged.connect(self.search_dogs)
        layout.addWidget(self.dogs_search_bar)

        # Edit Dog Button
        edit_dog_button = QPushButton("Edit Dog")
        edit_dog_button.clicked.connect(self.edit_dog)
        layout.addWidget(edit_dog_button)

        # Delete Dog Button
        delete_dog_button = QPushButton("Delete Dog")
        delete_dog_button.clicked.connect(self.delete_dog)
        layout.addWidget(delete_dog_button)

        # Dog Table View
        self.dog_table = QTableView()
        self.dog_model = QStandardItemModel()
        self.dog_table.setModel(self.dog_model)
        self.dog_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # Stretch columns
        layout.addWidget(self.dog_table)

        dog_tab.setLayout(layout)
        self.tabs.addTab(dog_tab, "Dogs")
        self.refresh_dog_table()  # Refresh dog table initially

    def delete_dog(self):
        selected_row = self.dog_table.currentIndex().row()
        if selected_row >= 0:
            dog_id = self.get_dog_id_from_row(selected_row)
            if dog_id:
                try:
                    confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this dog?", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        self.cursor.execute("DELETE FROM Dogs WHERE dog_id = ?", (dog_id,))
                        self.conn.commit()
                        self.refresh_dog_table()
                        QMessageBox.information(self, "Success", "Dog deleted successfully!")
                        self.dog_updated.emit()
                except Exception as e:
                    print(f"Error deleting dog: {e}")
                    QMessageBox.warning(self, "Error", "Failed to delete dog.")

    def refresh_dog_table(self, search_text=""):
        self.dog_model.clear()
        self.dog_model.setHorizontalHeaderLabels(["Name", "Breed", "Client"])

        try:
            if search_text:
                query = """
                    SELECT Dogs.name, Dogs.breed, Clients.name
                    FROM Dogs
                    INNER JOIN Clients ON Dogs.client_id = Clients.client_id
                    WHERE Dogs.name LIKE ? OR Dogs.breed LIKE ? OR Clients.name LIKE ?
                    ORDER BY Dogs.dog_id DESC
                """
                search_pattern = f"%{search_text}%"
                self.cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            else:
                query = """
                    SELECT Dogs.name, Dogs.breed, Clients.name
                    FROM Dogs
                    INNER JOIN Clients ON Dogs.client_id = Clients.client_id
                    ORDER BY Dogs.dog_id DESC
                """
                self.cursor.execute(query)

            for row in self.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.dog_model.appendRow(row_data)
            self.dog_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
            print(f"Error refreshing dog table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh dog table.")

    def search_dogs(self, text):
        self.refresh_dog_table(search_text=text)

    def edit_dog(self):
        selected_row = self.dog_table.currentIndex().row()
        if selected_row >= 0:
            dog_id = self.get_dog_id_from_row(selected_row)
            if dog_id:
                name, breed, client_name = self.get_dog_name_breed_client(dog_id)
                if name is not None and breed is not None and client_name is not None: # Check if data was retrieved
                    dialog = EditDogDialog(self, name, breed, client_name)
                    if dialog.exec_() == QDialog.Accepted:
                        new_name, new_breed, new_client_name = dialog.get_values()
                        self.update_dog_in_db(dog_id, new_name, new_breed, new_client_name)
                        self.refresh_dog_table()

    def get_dog_id_from_row(self, row):
        try:
            self.cursor.execute("SELECT dog_id FROM Dogs ORDER BY dog_id DESC LIMIT 1 OFFSET ?", (row,))
            result = self.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            print(f"Error getting dog ID: {e}")
            return None

    def get_dog_name_breed_client(self, dog_id):
        try:
            self.cursor.execute("""
                SELECT Dogs.name, Dogs.breed, Clients.name
                FROM Dogs
                JOIN Clients ON Dogs.client_id = Clients.client_id
                WHERE dog_id = ?""", (dog_id,))
            result = self.cursor.fetchone()
            return result if result else (None, None, None)
        except Exception as e:
            print(f"Error getting dog details: {e}")
            return None, None, None

    def update_dog_in_db(self, dog_id, new_name, new_breed, new_client_name):
        try:
            new_client_id = self.get_client_id(new_client_name)
            self.cursor.execute("""
                UPDATE Dogs
                SET name = ?, breed = ?, client_id = ?
                WHERE dog_id = ?
            """, (new_name, new_breed, new_client_id, dog_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Dog updated successfully!")
            self.dog_updated.emit()
        except Exception as e:
            print(f"Error updating dog: {e}")
            QMessageBox.warning(self, "Error", "Failed to update dog.")
# Service
    def create_service_tab(self):

        service_tab = QWidget()
        layout = QFormLayout()

        self.service_name_input = QLineEdit()
        self.service_price_input = QLineEdit()
        add_service_button = QPushButton("Add Service & Price")
        add_service_button.clicked.connect(self.add_service_price)

        layout.addRow("Service Name:", self.service_name_input)
        layout.addRow("Price:", self.service_price_input)
        layout.addRow(add_service_button)


        # Search Bar (added)
        self.service_search_bar = QLineEdit()
        self.service_search_bar.setPlaceholderText("Search Service Name or Price")
        self.service_search_bar.textChanged.connect(self.search_services)  # Connect to search function
        layout.addWidget(self.service_search_bar)


        # Edit Service Button
        edit_service_button = QPushButton("Edit Service")
        edit_service_button.clicked.connect(self.edit_service)
        layout.addRow(edit_service_button)

        # Delete Button
        delete_service_button = QPushButton("Delete Service")
        delete_service_button.clicked.connect(self.delete_service)
        layout.addRow(delete_service_button)


        # Service Table View
        self.service_table = QTableView()
        self.service_model = QStandardItemModel()
        self.service_table.setModel(self.service_model)
        self.service_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addRow(self.service_table)  # Use addRow for the table




        service_tab.setLayout(layout)
        self.tabs.addTab(service_tab, "Services & Prices")
        self.refresh_service_table()

    def delete_service(self):
        selected_row = self.service_table.currentIndex().row()
        if selected_row >= 0:
            service_id = self.get_service_id_from_row(selected_row)
            if service_id:
                try:
                    confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this service?", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        self.cursor.execute("DELETE FROM Prices WHERE service_id = ?", (service_id,)) # Delete from Prices first due to FK constraint
                        self.cursor.execute("DELETE FROM Services WHERE service_id = ?", (service_id,))
                        self.conn.commit()
                        self.refresh_service_table()
                        QMessageBox.information(self, "Success", "Service deleted successfully!")
                        self.service_updated.emit()
                except Exception as e:
                    print(f"Error deleting service: {e}")
                    QMessageBox.warning(self, "Error", "Failed to delete service.")

    def edit_service(self):
        selected_row = self.service_table.currentIndex().row()
        if selected_row >= 0:
            service_id = self.get_service_id_from_row(selected_row)
            if service_id:
                service_name, price = self.get_service_name_price(service_id)
                dialog = EditServiceDialog(self, service_name, price)
                if dialog.exec_() == QDialog.Accepted:
                    new_service_name, new_price = dialog.get_values()
                    self.update_service_in_db(service_id, new_service_name, new_price)
                    self.refresh_service_table()

    def get_service_id_from_row(self, row):
         try:
             self.cursor.execute("SELECT service_id FROM Services ORDER BY service_id DESC LIMIT 1 OFFSET ?", (row,))
             result = self.cursor.fetchone()
             return result[0] if result else None
         except Exception as e:
             print(f"Error getting service ID: {e}")
             return None

    def get_service_name_price(self, service_id):
        try:
            self.cursor.execute("""
                SELECT service_name, price
                FROM Services
                JOIN Prices ON Services.service_id = Prices.service_id
                WHERE Services.service_id = ?
            """, (service_id,))
            result = self.cursor.fetchone()
            return result
        except Exception as e:
            print(f"Error getting service name and price:", e)
            return None, None

    def update_service_in_db(self, service_id, new_service_name, new_price):
        try:
            self.cursor.execute("UPDATE Services SET service_name = ? WHERE service_id = ?", (new_service_name, service_id))
            self.cursor.execute("UPDATE Prices SET price = ? WHERE service_id = ?", (new_price, service_id))

            self.conn.commit()
            QMessageBox.information(self, "Success", "Service updated successfully!")
            self.service_updated.emit()
        except Exception as e:
            print(f"Error updating service:", e)
            QMessageBox.warning(self, "Error", "Failed to update service.")

    def refresh_service_table(self, search_text=""):
        self.service_model.clear()
        self.service_model.setHorizontalHeaderLabels(["Service Name", "Price"])

        try:
            if search_text:
                query = """
                    SELECT Services.service_name, Prices.price
                    FROM Services
                    INNER JOIN Prices ON Services.service_id = Prices.service_id
                    WHERE Services.service_name LIKE ? OR Prices.price LIKE ?
                    ORDER BY Services.service_id DESC
                """
                search_pattern = f"%{search_text}%"
                self.cursor.execute(query, (search_pattern, search_pattern))
            else:
                query = """
                    SELECT Services.service_name, Prices.price
                    FROM Services
                    INNER JOIN Prices ON Services.service_id = Prices.service_id
                    ORDER BY Services.service_id DESC
                """
                self.cursor.execute(query)

            for row in self.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.service_model.appendRow(row_data)
            self.service_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        except Exception as e:
            print(f"Error refreshing service table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh service table.")

    def search_services(self, text):
        self.refresh_service_table(search_text=text)

    def create_schedule_tab(self):
        schedule_tab = QWidget()
        layout = QFormLayout()

        self.schedule_client_dropdown = QComboBox()
        self.update_client_dropdown(self.schedule_client_dropdown)
        self.schedule_client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)

        self.schedule_dog_dropdown = QComboBox()

        self.schedule_service_dropdown = QComboBox()
        self.update_service_dropdown()
        self.schedule_service_dropdown.currentIndexChanged.connect(self.update_price_display)




        # Add QCalendarWidget for date selection
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)  # Optional: Show grid lines on the calendar
        self.calendar_widget.setMinimumDate(QDate.currentDate())  # Optional: Prevent selecting past dates
        self.calendar_widget.clicked.connect(self.update_selected_date)  # Update date display when a date is clicked

        self.selected_date_label = QLabel(f"Selected Date: {QDate.currentDate().toString('dd-MM-yyyy')}")



        # Enhanced time input with QTimeEdit
        self.schedule_time_input = QTimeEdit()
        self.schedule_time_input.setDisplayFormat("HH:mm")
        self.schedule_time_input.clear()
        self.schedule_time_input.setSpecialValueText(":")  # Show an empty placeholder initially
        self.schedule_time_input.setTimeRange(QTime(9, 0), QTime(20, 00))  # Restrict to valid times




        self.price_label = QLabel("")

        add_schedule_button = QPushButton("Add Schedule")
        add_schedule_button.clicked.connect(self.add_schedule)

        # Add widgets to the layout
        layout.addRow("Select Client:", self.schedule_client_dropdown)
        layout.addRow("Select Dog:", self.schedule_dog_dropdown)
        layout.addRow("Service:", self.schedule_service_dropdown)
        layout.addRow("Price:", self.price_label)
        layout.addRow("Date:", self.calendar_widget)  # Use calendar widget for date selection
        layout.addRow(self.selected_date_label)  # Show selected date below the calendar
        layout.addRow("Time:", self.schedule_time_input)
        layout.addRow(add_schedule_button)

        schedule_tab.setLayout(layout)
        self.tabs.addTab(schedule_tab, "Schedules")

    def create_current_schedules_tab(self):
        current_schedules_tab = QWidget()
        layout = QVBoxLayout()

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by Client, Dog, Service, or Date...")
        self.search_bar.textChanged.connect(self.search_schedules)  # Connect to search function
        layout.addWidget(self.search_bar)

        # Delete Button
        delete_schedule_button = QPushButton("Delete Schedule")
        delete_schedule_button.clicked.connect(self.delete_schedule)
        layout.addWidget(delete_schedule_button)

        # Edit Button
        edit_schedule_button = QPushButton("Edit Schedule")
        edit_schedule_button.clicked.connect(self.edit_schedule)
        layout.addWidget(edit_schedule_button)

        # Table View
        #self.schedule_table = QTableView()
        #self.schedule_model = QStandardItemModel()
        #self.schedule_table.setModel(self.schedule_model)
        # Table View (using custom model)
        self.schedule_table = QTableView()
        self.schedule_model = ScheduleTableModel(headers=["Client", "Dog", "Service", "Date", "Time", "Price"], parent=self) # Initialize with headers
        self.schedule_table.setModel(self.schedule_model)



        # Make the table read-only
        self.schedule_table.setEditTriggers(QTableView.NoEditTriggers)

        layout.addWidget(self.schedule_table)

        current_schedules_tab.setLayout(layout)
        self.tabs.addTab(current_schedules_tab, "Current Schedules")

        self.refresh_schedule_table()  # Initial population of the table
        self.schedule_updated.connect(self.refresh_schedule_table)  # Connect signal to refresh function


    def edit_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row >= 0:
            schedule_id = self.get_schedule_id_from_row(selected_row)
            if schedule_id is None:  # Check if schedule_id is None
                QMessageBox.warning(self, "Error", "Could not find schedule ID.")
                return  # Stop execution if no ID is found

            try:
                # Fetch existing schedule data
                self.cursor.execute("""
                    SELECT Clients.name, Dogs.name, Services.service_name, Schedules.date, Schedules.time, Prices.price
                    FROM Schedules  -- Added Schedules to ensure correct table selection
                    JOIN Clients ON Schedules.client_id = Clients.client_id
                    JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                    JOIN Services ON Schedules.service_id = Services.service_id
                    JOIN Prices ON Schedules.price_id = Prices.price_id
                    WHERE Schedules.schedule_id = ?
                """, (schedule_id,))
                result = self.cursor.fetchone()

                if result is None: # Check if the query returned a result
                    QMessageBox.warning(self, "Error", "No schedule found with that ID.")
                    return

                client_name, dog_name, service_name, date, time, price = result # Unpack only if result is not None

                dialog = EditScheduleDialog(self, client_name, dog_name, service_name, date, time, price)
                if dialog.exec_() == QDialog.Accepted:
                        new_client, new_dog, new_service, new_date, new_time = dialog.get_values()
                        # Update database with new values (implementation below)
                        self.update_schedule_in_db(schedule_id, new_client, new_dog, new_service, new_date, new_time)
                        self.refresh_schedule_table()  # Refresh table after update

            except Exception as e:
                    print(f"Error fetching schedule data for edit: {e}")
                    QMessageBox.warning(self, "Error", "Failed to fetch schedule data.")

    def get_schedule_id_from_row(self, row_index):
        try:
            if self.schedule_model.rowCount() > 0: # Check if the model has data
                return self.schedule_model._data[row_index][self.headers.index("schedule_id")] # Access schedule_id directly from model
            else:
                return None
        except Exception as e:
            print(f"Error getting schedule ID: {e}")
            return None


    def update_schedule_in_db(self, schedule_id, new_client, new_dog, new_service, new_date, new_time):
        try:
            new_client_id = self.get_client_id(new_client)
            new_dog_id = self.get_dog_id(new_dog)
            new_service_id = self.get_service_id_by_name(new_service)  # Get service_id
            new_price_id = self.get_price_id_by_service_id(new_service_id) # Get price_id based on service_id

            self.cursor.execute("""
                UPDATE Schedules
                SET client_id = ?, dog_id = ?, service_id = ?, price_id = ?, date = ?, time = ?  -- Correct column names
                WHERE schedule_id = ?
            """, (new_client_id, new_dog_id, new_service_id, new_price_id, new_date, new_time, schedule_id))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Schedule updated successfully!")
            self.schedule_updated.emit()
        except Exception as e:
            print(f"Error updating schedule: {e}")
            QMessageBox.warning(self, "Error", "Failed to update schedule.")

    def delete_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row >= 0:
            try:
                # Get the underlying data for the selected row
                model_index = self.schedule_model.index(selected_row, 0)  # Use column 0 for the index
                schedule_id = self.get_schedule_id_from_row(selected_row) # Get schedule_id using the corrected method

                if schedule_id is not None: # Check if schedule_id was found
                    confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this schedule?", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        self.cursor.execute("DELETE FROM Schedules WHERE schedule_id = ?", (schedule_id,))
                        self.conn.commit()
                        self.refresh_schedule_table() # Refresh the table to reflect changes
                        QMessageBox.information(self, "Success", "Schedule deleted successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Could not find schedule ID.")

            except Exception as e:
                print(f"Error deleting schedule: {e}")
                QMessageBox.warning(self, "Error", "Failed to delete schedule.")

    def get_schedule_id_from_row(self, row_index):
        """Retrieves the schedule_id from the model's data based on the row index."""
        try:
            if 0 <= row_index < self.schedule_model.rowCount():  # Check for valid row index
                schedule_id_index = self.schedule_model.headers.index("schedule_id") # Get the index of "schedule_id" column
                schedule_id = self.schedule_model._data[row_index][schedule_id_index]
                return schedule_id
            else:
                print(f"Invalid row index: {row_index}")  # Print a message for debugging
                return None
        except ValueError as e: # Handle ValueError if "schedule_id" is not found in headers
            print(f"Error getting schedule ID: {e}")
            return None
        except Exception as e:
            print(f"Error getting schedule ID: {e}")
            return None

    def update_selected_date(self, date):
        """Update the label to display the selected date."""
        self.selected_date_label.setText(f"Selected Date: {date.toString('dd-MM-yyyy')}")

    def tab_changed(self, index):
        if index == self.tabs.indexOf(self.tabs.widget(3)):  # Check if Schedules tab is selected (index 3)
            self.schedule_date_input.setFocus()

    def update_service_dropdown(self):
        services = self.get_services()
        self.schedule_service_dropdown.clear()
        self.schedule_service_dropdown.addItems(services)

    def update_price_display(self):
        service_name = self.schedule_service_dropdown.currentText()
        price = self.get_price_by_service(service_name)
        if price is not None:
            self.price_label.setText(str(price))
        else:
            self.price_label.setText("")

    def get_price_by_service(self, service_name):
        self.cursor.execute("SELECT price FROM Prices WHERE service_id = (SELECT service_id FROM Services WHERE service_name = ?)", (service_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_schedule(self):
        client_name = self.schedule_client_dropdown.currentText()
        dog_name = self.schedule_dog_dropdown.currentText()
        service_name = self.schedule_service_dropdown.currentText()
        date = self.calendar_widget.selectedDate().toString("dd-MM-yyyy")
        time = self.schedule_time_input.time().toString("HH:mm")

        if client_name and dog_name and service_name:
            client_id = self.get_client_id(client_name)
            dog_id = self.get_dog_id(dog_name) # Assuming you have this function
            service_id = self.get_service_id_by_name(service_name)
            price_id = self.get_price_id_by_service_id(service_id)

            try:
                self.cursor.execute("""
                    INSERT INTO Schedules (client_id, dog_id, date, time, service_id, price_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (client_id, dog_id, date, time, service_id, price_id))
                self.conn.commit()
                QMessageBox.information(self, "Success", "Schedule added successfully!")
                self.schedule_updated.emit() # Emit signal to refresh the table
            except Exception as e:
                print(f"Error adding schedule: {e}")
                QMessageBox.warning(self, "Error", "Failed to add schedule.")
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def get_dog_id(self, dog_name):
        self.cursor.execute("SELECT dog_id FROM Dogs WHERE name = ?", (dog_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_service_id_by_name(self, service_name):
        self.cursor.execute("SELECT service_id FROM Services WHERE service_name = ?", (service_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_price_id_by_service_id(self, service_id):
        self.cursor.execute("SELECT price_id FROM Prices WHERE service_id = ?", (service_id,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def update_client_dropdown(self, dropdown):
        clients = self.get_clients()
        dropdown.clear()
        dropdown.addItems(clients)

    def update_dog_dropdown(self):
        client_name = self.schedule_client_dropdown.currentText()
        dogs = self.get_dogs_by_client(client_name)
        self.schedule_dog_dropdown.clear()
        self.schedule_dog_dropdown.addItems(dogs)

    def get_clients(self):
        self.cursor.execute("SELECT name FROM Clients")
        return [row[0] for row in self.cursor.fetchall()]

    def get_dogs(self):
        self.cursor.execute("SELECT name FROM Dogs")
        return [row[0] for row in self.cursor.fetchall()]

    def get_dogs_by_client(self, client_name):
        client_id = self.get_client_id(client_name)
        self.cursor.execute("SELECT name FROM Dogs WHERE client_id = ?", (client_id,))
        return [row[0] for row in self.cursor.fetchall()]

    def get_services(self):
        self.cursor.execute("SELECT service_name FROM Services")
        return [row[0] for row in self.cursor.fetchall()]

    def get_client_id(self, client_name):
        self.cursor.execute("SELECT client_id FROM Clients WHERE name = ?", (client_name,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def add_client(self):
        name = self.client_name_input.text()
        phone = self.client_phone_input.text()

        if name and phone:
            self.cursor.execute("INSERT INTO Clients (name, phone) VALUES (?, ?)", (name, phone))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Client added successfully!")
            self.update_client_dropdown(self.dog_client_dropdown)
            self.update_client_dropdown(self.schedule_client_dropdown)
            self.client_name_input.clear()  # Clear input fields
            self.client_phone_input.clear()
            self.client_updated.emit()
            self.refresh_client_table() # Refresh the table after adding a client
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def add_dog(self):
        name = self.dog_name_input.text()
        breed = self.dog_breed_input.text()
        client_name = self.dog_client_dropdown.currentText()

        if name and breed and client_name:
            client_id = self.get_client_id(client_name)
            self.cursor.execute("INSERT INTO Dogs (client_id, name, breed) VALUES (?, ?, ?)", (client_id, name, breed))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Dog added successfully!")
            self.dog_updated.emit()
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def add_service_price(self):
        name = self.service_name_input.text()
        try:
            price = float(self.service_price_input.text())
            if not name:
                raise ValueError("Service name cannot be empty.")  # Provide a specific error message

            self.cursor.execute("INSERT INTO Services (service_name) VALUES (?)", (name,))
            service_id = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO Prices (service_id, price) VALUES (?, ?)", (service_id, price))
            self.conn.commit()
            QMessageBox.information(self, "Success", "Service and price added successfully!")
            self.service_updated.emit()

            # Update service dropdown in the schedule tab
            self.update_service_dropdown()

        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")

    def refresh_schedule_table(self, search_text=""):
        """Refreshes the schedule table, including the schedule_id."""
        try:
            if search_text:
                query = """
                    SELECT SELECT Clients.name AS Client, Dogs.name AS Dog, Services.service_name AS Service, 
                           Schedules.date, Schedules.time, Prices.price, Schedules.schedule_id
                    FROM Schedules
                    JOIN Clients ON Schedules.client_id = Clients.client_id
                    JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                    JOIN Services ON Schedules.service_id = Services.service_id
                    JOIN Prices ON Schedules.price_id = Prices.price_id
                    WHERE
                        Clients.name LIKE ? OR
                        Dogs.name LIKE ? OR
                        Services.service_name LIKE ? OR
                        Schedules.date LIKE ?
                    ORDER BY Schedules.schedule_id DESC
                """
                search_pattern = f"%{search_text}%"
                self.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))

            else:
                query = """
                    SELECT Clients.name AS Client, Dogs.name AS Dog, Services.service_name AS Service, 
                           Schedules.date, Schedules.time, Prices.price, Schedules.schedule_id  -- Include schedule_id here
                    FROM Schedules
                    JOIN Clients ON Schedules.client_id = Clients.client_id
                    JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                    JOIN Services ON Schedules.service_id = Services.service_id
                    JOIN Prices ON Schedules.price_id = Prices.price_id
                    ORDER BY Schedules.schedule_id DESC
                """
                self.cursor.execute(query)

            new_data = []
            for row in self.cursor.fetchall():
                new_data.append(row)

            self.schedule_model.headers = [description[0] for description in self.cursor.description] # Dynamically get headers
            self.schedule_model.update_data(new_data)
            self.schedule_table.resizeColumnsToContents()

        except Exception as e:
            print(f"Error refreshing schedule table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh schedule table.")

    def search_schedules(self, text):
        self.refresh_schedule_table(search_text=text) # Call refresh_schedule_table with the search text


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CanineHaircutApp()
    window.show()
    sys.exit(app.exec_())