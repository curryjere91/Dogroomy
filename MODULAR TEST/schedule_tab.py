from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QComboBox, QCalendarWidget, QTimeEdit, QPushButton, QLabel, QMessageBox, QVBoxLayout
)
from PyQt5.QtCore import QDate, QTime


class ScheduleTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # Reference to the main window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Form for scheduling
        self.schedule_client_dropdown = QComboBox()
        self.schedule_dog_dropdown = QComboBox()
        self.schedule_service_dropdown = QComboBox()
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setMinimumDate(QDate.currentDate())
        self.schedule_time_input = QTimeEdit()
        self.schedule_time_input.setDisplayFormat("HH:mm")
        self.price_label = QLabel("")

        self.update_client_dropdown()
        self.update_service_dropdown()
        self.schedule_client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)
        self.schedule_service_dropdown.currentIndexChanged.connect(self.update_price_display)

        add_schedule_button = QPushButton("Add Schedule")
        add_schedule_button.clicked.connect(self.add_schedule)

        # Layout setup
        form_layout = QFormLayout()
        form_layout.addRow("Select Client:", self.schedule_client_dropdown)
        form_layout.addRow("Select Dog:", self.schedule_dog_dropdown)
        form_layout.addRow("Select Service:", self.schedule_service_dropdown)
        form_layout.addRow("Price:", self.price_label)
        form_layout.addRow("Date:", self.calendar_widget)
        form_layout.addRow("Time:", self.schedule_time_input)
        form_layout.addRow(add_schedule_button)

        self.layout.addLayout(form_layout)

    def update_client_dropdown(self):
        """Populate the client dropdown."""
        clients = self.parent.get_clients()
        self.schedule_client_dropdown.clear()
        self.schedule_client_dropdown.addItems(clients)
        self.update_dog_dropdown()

    def update_dog_dropdown(self):
        """Populate the dog dropdown based on the selected client."""
        client_name = self.schedule_client_dropdown.currentText()
        dogs = self.parent.get_dogs_by_client(client_name)
        self.schedule_dog_dropdown.clear()
        self.schedule_dog_dropdown.addItems(dogs)

    def update_service_dropdown(self):
        """Populate the service dropdown."""
        services = self.parent.get_services()
        self.schedule_service_dropdown.clear()
        self.schedule_service_dropdown.addItems(services)

    def update_price_display(self):
        """Update the displayed price based on the selected service."""
        service_name = self.schedule_service_dropdown.currentText()
        price = self.parent.get_price_by_service(service_name)
        self.price_label.setText(str(price) if price else "")

    def add_schedule(self):
        """Add a new schedule to the database."""
        client_name = self.schedule_client_dropdown.currentText()
        dog_name = self.schedule_dog_dropdown.currentText()
        service_name = self.schedule_service_dropdown.currentText()
        date = self.calendar_widget.selectedDate().toString("dd-MM-yyyy")
        time = self.schedule_time_input.time().toString("HH:mm")

        if client_name and dog_name and service_name:
            client_id = self.parent.get_client_id(client_name)
            dog_id = self.parent.get_dog_id(dog_name)
            service_id = self.parent.get_service_id_by_name(service_name)
            price_id = self.parent.get_price_id_by_service_id(service_id)

            try:
                self.parent.cursor.execute("""
                    INSERT INTO Schedules (client_id, dog_id, date, time, service_id, price_id)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (client_id, dog_id, date, time, service_id, price_id))
                self.parent.conn.commit()
                QMessageBox.information(self, "Success", "Schedule added successfully!")
                self.parent.schedule_updated.emit()
            except Exception as e:
                print(f"Error adding schedule: {e}")
                QMessageBox.warning(self, "Error", "Failed to add schedule.")
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")
