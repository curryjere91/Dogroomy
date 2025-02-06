from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableView, QLineEdit, QPushButton, 
    QComboBox, QLabel, QCalendarWidget, QTimeEdit, QDialog, QDialogButtonBox, QMessageBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QDate, QTime

class SchedulesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by Client, Dog, Service, or Date...")
        self.search_bar.textChanged.connect(self.search_schedules)
        self.layout.addWidget(self.search_bar)

        # Table View
        self.schedule_table = QTableView()
        self.schedule_model = QStandardItemModel()
        self.schedule_model.setHorizontalHeaderLabels(["Client", "Dog", "Service", "Date", "Time", "Price"])
        self.schedule_table.setModel(self.schedule_model)
        self.schedule_table.setEditTriggers(QTableView.NoEditTriggers)
        self.layout.addWidget(self.schedule_table)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        add_schedule_button = QPushButton("Add Schedule")
        add_schedule_button.clicked.connect(self.open_add_schedule_dialog)
        buttons_layout.addWidget(add_schedule_button)

        edit_schedule_button = QPushButton("Edit Schedule")
        edit_schedule_button.clicked.connect(self.edit_schedule)
        buttons_layout.addWidget(edit_schedule_button)

        delete_schedule_button = QPushButton("Delete Schedule")
        delete_schedule_button.clicked.connect(self.parent.delete_schedule)
        buttons_layout.addWidget(delete_schedule_button)

        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)

    def search_schedules(self, text):
        # Implement search logic here (placeholder for now)
        print(f"Searching schedules for: {text}")

    def edit_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "No schedule selected.")
            return

        schedule_id = self.get_schedule_id_from_row(selected_row)
        if not schedule_id:
            QMessageBox.warning(self, "Error", "Could not find schedule ID.")
            return

        try:
            self.parent.cursor.execute(
                """
                SELECT Clients.name, Dogs.name, Services.service_name, Schedules.date, Schedules.time, Prices.price
                FROM Schedules
                JOIN Clients ON Schedules.client_id = Clients.client_id
                JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                JOIN Services ON Schedules.service_id = Services.service_id
                JOIN Prices ON Schedules.price_id = Prices.price_id
                WHERE Schedules.schedule_id = ?
                """,
                (schedule_id,)
            )
            result = self.parent.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Error", "No schedule found with that ID.")
                return

            client_name, dog_name, service_name, date, time, price = result
            dialog = EditScheduleDialog(self, client_name, dog_name, service_name, date, time, price)
            if dialog.exec_() == QDialog.Accepted:
                new_client, new_dog, new_service, new_date, new_time = dialog.get_values()
                self.parent.update_schedule_in_db(schedule_id, new_client, new_dog, new_service, new_date, new_time)
                self.parent.refresh_schedule_table()

        except Exception as e:
            print(f"Error fetching schedule data for edit: {e}")
            QMessageBox.warning(self, "Error", "Failed to fetch schedule data.")

    def open_add_schedule_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Schedule")
        layout = QFormLayout(dialog)

        self.schedule_client_dropdown = QComboBox()
        self.parent.update_client_dropdown(self.schedule_client_dropdown)
        self.schedule_client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)
        layout.addRow("Select Client:", self.schedule_client_dropdown)

        self.schedule_dog_dropdown = QComboBox()
        layout.addRow("Select Dog:", self.schedule_dog_dropdown)

        service_layout = QHBoxLayout()
        self.schedule_service_dropdown = QComboBox()
        self.parent.update_service_dropdown()
        self.schedule_service_dropdown.currentIndexChanged.connect(self.update_price_display)
        service_layout.addWidget(QLabel("Service:"))
        service_layout.addWidget(self.schedule_service_dropdown)

        self.price_label = QLabel("")
        service_layout.addWidget(QLabel("Price:"))
        service_layout.addWidget(self.price_label)
        layout.addRow(service_layout)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setMinimumDate(QDate.currentDate())
        layout.addRow("Date:", self.calendar_widget)

        self.schedule_time_input = QTimeEdit()
        self.schedule_time_input.setDisplayFormat("HH:mm")
        self.schedule_time_input.setTimeRange(QTime(9, 0), QTime(20, 00))
        layout.addRow("Time:", self.schedule_time_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.parent.add_schedule(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)

        dialog.setLayout(layout)
        dialog.exec_()



-----------------------------------------------------------------------------------------------------------------------------------

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QTableView, QLineEdit, QPushButton, 
    QComboBox, QLabel, QCalendarWidget, QTimeEdit, QDialog, QDialogButtonBox, QMessageBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import QDate, QTime

from database_utils import refresh_schedule_table

class SchedulesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()

        # Search Bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by Client, Dog, Service, or Date...")
        self.search_bar.textChanged.connect(self.search_schedules)
        self.layout.addWidget(self.search_bar)

        # Table View
        self.schedule_table = QTableView()
        self.schedule_model = QStandardItemModel()
        self.schedule_model.setHorizontalHeaderLabels(["Client", "Dog", "Service", "Date", "Time", "Price"])
        self.schedule_table.setModel(self.schedule_model)
        self.schedule_table.setEditTriggers(QTableView.NoEditTriggers)
        self.layout.addWidget(self.schedule_table)

        # Buttons Layout
        buttons_layout = QHBoxLayout()
        
        add_schedule_button = QPushButton("Add Schedule")
        add_schedule_button.clicked.connect(self.open_add_schedule_dialog)
        buttons_layout.addWidget(add_schedule_button)

        edit_schedule_button = QPushButton("Edit Schedule")
        edit_schedule_button.clicked.connect(self.edit_schedule)
        buttons_layout.addWidget(edit_schedule_button)

        delete_schedule_button = QPushButton("Delete Schedule")
        delete_schedule_button.clicked.connect(self.delete_schedule)
        buttons_layout.addWidget(delete_schedule_button)

        self.layout.addLayout(buttons_layout)
        self.setLayout(self.layout)

        #refresh schedule table
        refresh_schedule_table(self.schedule_model, self.parent.conn)

    def search_schedules(self, text):
        # Implement search logic here (placeholder for now)
        print(f"Searching schedules for: {text}")

    def edit_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "No schedule selected.")
            return

        schedule_id = self.get_schedule_id_from_row(selected_row)
        if not schedule_id:
            QMessageBox.warning(self, "Error", "Could not find schedule ID.")
            return

        try:
            self.parent.cursor.execute(
                """
                SELECT Clients.name, Dogs.name, Services.service_name, Schedules.date, Schedules.time, Prices.price
                FROM Schedules
                JOIN Clients ON Schedules.client_id = Clients.client_id
                JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                JOIN Services ON Schedules.service_id = Services.service_id
                JOIN Prices ON Schedules.price_id = Prices.price_id
                WHERE Schedules.schedule_id = ?
                """,
                (schedule_id,)
            )
            result = self.parent.cursor.fetchone()
            if not result:
                QMessageBox.warning(self, "Error", "No schedule found with that ID.")
                return

            client_name, dog_name, service_name, date, time, price = result
            dialog = EditScheduleDialog(self, client_name, dog_name, service_name, date, time, price)
            if dialog.exec_() == QDialog.Accepted:
                new_client, new_dog, new_service, new_date, new_time = dialog.get_values()
                self.parent.update_schedule_in_db(schedule_id, new_client, new_dog, new_service, new_date, new_time)
                self.parent.refresh_schedule_table()

        except Exception as e:
            print(f"Error fetching schedule data for edit: {e}")
            QMessageBox.warning(self, "Error", "Failed to fetch schedule data.")

    def open_add_schedule_dialog(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Schedule")
        layout = QFormLayout(dialog)

        self.schedule_client_dropdown = QComboBox()
        self.update_client_dropdown(self.schedule_client_dropdown)
        self.schedule_client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)
        layout.addRow("Select Client:", self.schedule_client_dropdown)

        self.schedule_dog_dropdown = QComboBox()
        layout.addRow("Select Dog:", self.schedule_dog_dropdown)
    
        service_layout = QHBoxLayout()
        self.schedule_service_dropdown = QComboBox()
        self.update_service_dropdown()
        self.schedule_service_dropdown.currentIndexChanged.connect(self.update_price_display)
        service_layout.addWidget(QLabel("Service:"))
        service_layout.addWidget(self.schedule_service_dropdown)

        self.price_label = QLabel("")
        service_layout.addWidget(QLabel("Price:"))
        service_layout.addWidget(self.price_label)
        layout.addRow(service_layout)

        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setGridVisible(True)
        self.calendar_widget.setMinimumDate(QDate.currentDate())
        layout.addRow("Date:", self.calendar_widget)

        self.schedule_time_input = QTimeEdit()
        self.schedule_time_input.setDisplayFormat("HH:mm")
        self.schedule_time_input.setTimeRange(QTime(9, 0), QTime(20, 00))
        layout.addRow("Time:", self.schedule_time_input)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(lambda: self.add_schedule(dialog))
        button_box.rejected.connect(dialog.reject)
        layout.addRow(button_box)

        dialog.setLayout(layout)
        dialog.exec_()

    def delete_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "No schedule selected.")
            return

        try:
            schedule_id = self.get_schedule_id_from_row(selected_row)
            if schedule_id is None:
                QMessageBox.warning(self, "Error", "Could not find schedule ID.")
                return

            confirm = QMessageBox.question(
                self, "Confirm Delete", "Are you sure you want to delete this schedule?",
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.parent.cursor.execute("DELETE FROM Schedules WHERE schedule_id = ?", (schedule_id,))
                self.parent.conn.commit()
                self.parent.refresh_schedule_table()
                QMessageBox.information(self, "Success", "Schedule deleted successfully!")
        except Exception as e:
            print(f"Error deleting schedule: {e}")
            QMessageBox.warning(self, "Error", "Failed to delete schedule.")
        
    def update_client_dropdown(self, dropdown):
        clients = self.parent.get_clients()
        dropdown.clear()
        dropdown.addItems(clients)

    def update_dog_dropdown(self):
        client_name = self.schedule_client_dropdown.currentText() 
        dogs = self.parent.get_dogs_by_client(client_name)
        self.schedule_dog_dropdown.clear()
        self.schedule_dog_dropdown.addItems(dogs)

    def update_service_dropdown(self):
        services = self.parent.get_services()
        self.schedule_service_dropdown.clear()
        self.schedule_service_dropdown.addItems(services)

    def update_price_display(self):
        service_name = self.schedule_service_dropdown.currentText()
        price = self.parent.get_price_by_service(service_name)
        self.price_label.setText(str(price))

    def add_schedule(self, dialog):
        client_name = self.schedule_client_dropdown.currentText()
        dog_name = self.schedule_dog_dropdown.currentText()
        service_name = self.schedule_service_dropdown.currentText()
        date = self.calendar_widget.selectedDate().toString("yyyy-MM-dd")
        time = self.schedule_time_input.time().toString("HH:mm")

        if not all([client_name, dog_name, service_name]):
            QMessageBox.warning(self, "Error", "Please fill all fields before adding a schedule.")
            return

        try:
            # Get the service_id first
            self.parent.cursor.execute(
                "SELECT service_id FROM Services WHERE service_name = ?",
                (service_name,)
            )
            service_result = self.parent.cursor.fetchone()

            if not service_result:
                QMessageBox.warning(self, "Error", "Service not found in database.")
                return

            service_id = service_result[0]

            # Get the price_id using the service_id
            self.parent.cursor.execute(
                "SELECT price_id FROM Prices WHERE service_id = ?",
                (service_id,)
            )
            price_result = self.parent.cursor.fetchone()

            if not price_result:
                QMessageBox.warning(self, "Error", "No price found for selected service.")
                return

            price_id = price_result[0]

            # Insert the new schedule into the database
            self.parent.cursor.execute(
                """
                INSERT INTO Schedules (client_id, dog_id, service_id, price_id, date, time)
                VALUES (
                    (SELECT client_id FROM Clients WHERE name = ?),
                    (SELECT dog_id FROM Dogs WHERE name = ?),
                    ?, ?, ?, ?
                )
                """,
                (client_name, dog_name, service_id, price_id, date, time)
            )

            self.parent.conn.commit()

            # Call refresh_schedule_table from database_utils.py
            refresh_schedule_table(self.schedule_model, self.parent.conn)

            QMessageBox.information(self, "Success", "Schedule added successfully!")
            dialog.accept()

        except Exception as e:
            print(f"Error adding schedule: {e}")
            QMessageBox.warning(self, "Error", "Failed to add schedule.")





class EditScheduleDialog(QDialog): 
    def __init__(self, parent, client_name, dog_name, service_name, date, time, price):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle("Edit Schedule")
        layout = QFormLayout(self)

        self.client_dropdown = QComboBox()
        self.client_dropdown.addItems(self.parent.get_clients())
        self.client_dropdown.setCurrentText(client_name)
        self.client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)
        layout.addRow("Client:", self.client_dropdown)

        self.dog_dropdown = QComboBox()
        self.update_dog_dropdown()
        self.dog_dropdown.setCurrentText(dog_name)
        layout.addRow("Dog:", self.dog_dropdown)

        service_layout = QHBoxLayout()
        self.service_dropdown = QComboBox()
        self.service_dropdown.addItems(self.parent.get_services())
        self.service_dropdown.setCurrentText(service_name)
        self.service_dropdown.currentIndexChanged.connect(self.update_price_display)
        service_layout.addWidget(QLabel("Service:"))
        service_layout.addWidget(self.service_dropdown)

        self.price_label = QLabel(str(price))
        service_layout.addWidget(QLabel("Price:"))
        service_layout.addWidget(self.price_label)
        layout.addRow(service_layout)

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
    
    def get_values(self):
        return (
            self.client_dropdown.currentText(),
            self.dog_dropdown.currentText(),
            self.service_dropdown.currentText(),
            self.calendar_widget.selectedDate().toString("dd-MM-yyyy"),
            self.time_edit.time().toString("HH:mm")
        )

