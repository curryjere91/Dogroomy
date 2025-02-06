from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QTableView, QMessageBox, QHeaderView, QDialog, QComboBox, QLabel, QCalendarWidget, QTimeEdit,
    QDialogButtonBox, QDialog, QPushButton, QGraphicsView, QGraphicsScene, QGraphicsEllipseItem, QGraphicsLineItem
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem,  QPen, QBrush
from PyQt5.QtCore import QDate, QTime, QDateTime, Qt, QPointF
import math

class AnalogClockDialog(QDialog):
    '''CLOCK WIDGET'''
    last_selected_time = QTime(12, 0)
    last_is_pm = False

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select Time")
        self.setFixedSize(300, 420)

        layout = QVBoxLayout(self)

        # Top layout for time display and AM/PM toggle
        top_layout = QHBoxLayout()
        self.time_label = QLabel("Selected Time: 12:00", self)
        self.time_label.setAlignment(Qt.AlignCenter)
        self.ampm_button = QPushButton("AM")
        self.ampm_button.clicked.connect(self.toggle_ampm)
        top_layout.addWidget(self.time_label)
        top_layout.addWidget(self.ampm_button)

        # Graphics View for the Clock
        self.view = QGraphicsView()
        self.scene = QGraphicsScene(0, 0, 250, 250)
        self.view.setScene(self.scene)

        # Draw the clock face
        clock_face = QGraphicsEllipseItem(0, 0, 250, 250)
        clock_face.setBrush(QBrush(Qt.white))
        self.scene.addItem(clock_face)

        # Center point
        self.center = QPointF(125, 125)

        # Draw hour ticks (12-hour format)
        for i in range(12):
            angle = math.radians(i * 30 - 90)
            x1 = 125 + 100 * math.cos(angle)
            y1 = 125 + 100 * math.sin(angle)
            x2 = 125 + 110 * math.cos(angle)
            y2 = 125 + 110 * math.sin(angle)
            self.scene.addLine(x1, y1, x2, y2, QPen(Qt.black, 2))

        # Hour hand
        self.hour_hand = QGraphicsLineItem(125, 125, 125, 80)
        self.hour_hand.setPen(QPen(Qt.blue, 4))
        self.scene.addItem(self.hour_hand)

        # Minute hand
        self.minute_hand = QGraphicsLineItem(125, 125, 125, 50)
        self.minute_hand.setPen(QPen(Qt.red, 3))
        self.scene.addItem(self.minute_hand)

        # Select Button
        self.select_button = QPushButton("Select Time")
        self.select_button.clicked.connect(self.accept)

        # Add widgets to layout
        layout.addLayout(top_layout)
        layout.addWidget(self.view)
        layout.addWidget(self.select_button)

        # Mouse click event to set time
        self.view.setMouseTracking(True)
        self.view.mousePressEvent = self.set_time_from_click

        # Restore last selected time
        self.selected_time = AnalogClockDialog.last_selected_time
        self.is_pm = AnalogClockDialog.last_is_pm
        self.update_hands()
        self.update_time_label()  # Ensure the label is updated with the last selected time

    def toggle_ampm(self):
        self.is_pm = not self.is_pm
        self.ampm_button.setText("PM" if self.is_pm else "AM")
        self.update_time_label()

    def set_time_from_click(self, event):
        pos = self.view.mapToScene(event.pos())
        dx = pos.x() - self.center.x()
        dy = pos.y() - self.center.y()
        angle = math.degrees(math.atan2(dy, dx)) + 90

        if angle < 0:
            angle += 360

        if event.button() == Qt.LeftButton:
            hour = (round(angle / 30) + 12) % 12
            if hour == 0:
                hour = 12
            self.selected_time.setHMS(hour, self.selected_time.minute(), 0)
        elif event.button() == Qt.RightButton:
            minute = (round(angle / 30) * 5) % 60
            self.selected_time.setHMS(self.selected_time.hour(), minute, 0)

        self.update_hands()

    def update_hands(self):
        hour_angle = ((self.selected_time.hour() % 12) * 30) - 90
        xh = 125 + 45 * math.cos(math.radians(hour_angle))
        yh = 125 + 45 * math.sin(math.radians(hour_angle))
        self.hour_hand.setLine(125, 125, xh, yh)

        minute_angle = (self.selected_time.minute() * 6) - 90
        xm = 125 + 70 * math.cos(math.radians(minute_angle))
        ym = 125 + 70 * math.sin(math.radians(minute_angle))
        self.minute_hand.setLine(125, 125, xm, ym)

        self.update_time_label()

    def update_time_label(self):
        hour = self.selected_time.hour()
        minute = self.selected_time.minute()

        if self.is_pm and hour != 12:
            hour += 12
        elif not self.is_pm and hour == 12:
            hour = 0

        self.time_label.setText(f"Selected Time: {QTime(hour, minute).toString('HH:mm')}")

    def get_selected_time(self):
        hour = self.selected_time.hour()
        if self.is_pm and hour != 12:
            hour += 12
        elif not self.is_pm and hour == 12:
            hour = 0

        AnalogClockDialog.last_selected_time = QTime(hour, self.selected_time.minute(), 0)
        AnalogClockDialog.last_is_pm = self.is_pm
        return AnalogClockDialog.last_selected_time

class EditScheduleDialog(QDialog):
    def __init__(self, parent, client_name="", dog_name="", service_name="", date="", time="", price=0.0):
        super().__init__(parent)
        self.setWindowTitle("Edit Schedule")
        layout = QFormLayout(self)

        # Client Dropdown (Editable)
        self.client_dropdown = QComboBox()
        self.client_dropdown.setEditable(True)  # Allow typing to filter
        self.client_dropdown.addItems(parent.get_clients())
        self.client_dropdown.setCurrentText(client_name)  # Set the provided client name
        self.client_dropdown.currentIndexChanged.connect(self.update_dog_dropdown)  # Connect signal
        layout.addRow("Client:", self.client_dropdown)

        # Dog Dropdown (Editable)
        self.dog_dropdown = QComboBox()
        self.dog_dropdown.setEditable(True)  # Allow typing to filter
        self.update_dog_dropdown()  # Populate dogs for the first client
        self.dog_dropdown.setCurrentText(dog_name)  # Set the provided dog name
        layout.addRow("Dog:", self.dog_dropdown)

        # Service Dropdown (Editable)
        self.service_dropdown = QComboBox()
        self.service_dropdown.setEditable(True)  # Allow typing to filter
        self.service_dropdown.addItems(parent.get_services())
        self.service_dropdown.setCurrentText(service_name)  # Set the provided service name
        self.service_dropdown.currentIndexChanged.connect(self.update_price_display)  # Connect signal
        layout.addRow("Service:", self.service_dropdown)

        # Price Label (Updated dynamically)
        self.price_label = QLabel(str(price))
        layout.addRow("Price:", self.price_label)

        # Calendar Widget (Only current day)
        self.calendar_widget = QCalendarWidget()
        self.calendar_widget.setMinimumDate(QDate.currentDate())  # Only allow current day
        self.calendar_widget.setSelectedDate(QDate.fromString(date, "dd-MM-yyyy") if date else QDate.currentDate())
        layout.addRow("Date:", self.calendar_widget)

        # Time Selection Button and Label
        self.time_label = QLabel(time if time else "12:00")
        self.time_button = QPushButton("Select Time")
        self.time_button.clicked.connect(self.select_time)
        time_layout = QHBoxLayout()
        time_layout.addWidget(self.time_label)
        time_layout.addWidget(self.time_button)
        layout.addRow("Time:", time_layout)

        # Initialize selected time
        self.selected_time = QTime.fromString(time, "HH:mm") if time else QTime(12, 0)

        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def select_time(self):
        dialog = AnalogClockDialog(self)
        dialog.selected_time = self.selected_time
        if dialog.exec_() == QDialog.Accepted:
            self.selected_time = dialog.get_selected_time()
            self.time_label.setText(self.selected_time.toString("HH:mm"))

    def update_dog_dropdown(self):
        """Update the dog dropdown based on the selected client."""
        client_name = self.client_dropdown.currentText()
        dogs = self.parent().get_dogs_by_client(client_name)  # Access parent methods
        self.dog_dropdown.clear()
        self.dog_dropdown.addItems(dogs)
        self.dog_dropdown.setCurrentIndex(0)  # Set first dog as default

    def update_price_display(self):
        """Update the price label based on the selected service."""
        service_name = self.service_dropdown.currentText()
        price = self.parent().get_price_by_service(service_name)  # Access parent methods
        self.price_label.setText(str(price) if price else "0.0")

    def get_values(self):
        """Return the selected values from the dialog."""
        return (
            self.client_dropdown.currentText(),
            self.dog_dropdown.currentText(),
            self.service_dropdown.currentText(),
            self.calendar_widget.selectedDate().toString("dd-MM-yyyy"),
            self.selected_time.toString("HH:mm"),
            float(self.price_label.text())  # Return price as a float
        )

class ScheduleTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_search_bar()
        self.create_schedule_table()
        self.create_action_buttons()
        self.refresh_schedule_table()

    def create_search_bar(self):
        self.schedule_search_bar = QLineEdit()
        self.schedule_search_bar.setPlaceholderText("Search Schedule")
        self.schedule_search_bar.textChanged.connect(self.search_schedules)
        self.layout.addWidget(self.schedule_search_bar)

    def create_schedule_table(self):
        self.schedule_table = QTableView()
        self.schedule_model = QStandardItemModel()
        self.schedule_model.setHorizontalHeaderLabels(["Client", "Dog", "Service", "Date", "Time", "Price"])
        self.schedule_table.setModel(self.schedule_model)
        self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.schedule_table)

    def create_action_buttons(self):
        button_layout = QHBoxLayout()

        self.add_schedule_button = QPushButton("Add Schedule")
        self.add_schedule_button.clicked.connect(self.show_add_schedule_dialog)

        self.edit_schedule_button = QPushButton("Edit Schedule")
        self.edit_schedule_button.clicked.connect(self.edit_schedule)

        self.delete_schedule_button = QPushButton("Delete Schedule")
        self.delete_schedule_button.clicked.connect(self.delete_schedule)

        button_layout.addWidget(self.add_schedule_button)
        button_layout.addWidget(self.edit_schedule_button)
        button_layout.addWidget(self.delete_schedule_button)

        self.layout.addLayout(button_layout)

    def show_add_schedule_dialog(self):
        dialog = EditScheduleDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            client_name, dog_name, service_name, date, time, price = dialog.get_values()
            if not self.validate_schedule_time(date, time):
                QMessageBox.warning(self, "Error", "The selected time is in the past or overlaps with another schedule.")
                return
            self.add_schedule_to_db(client_name, dog_name, service_name, date, time, price)

    def validate_schedule_time(self, date, time):
        """Check if the selected time is valid and does not overlap with existing schedules."""
        selected_datetime = QDateTime.fromString(f"{date} {time}", "dd-MM-yyyy HH:mm")
        if selected_datetime < QDateTime.currentDateTime():
            return False  # Time is in the past

        # Check for overlapping schedules
        self.parent.cursor.execute(
            """
            SELECT COUNT(*) FROM Schedules
            WHERE date = ? AND time = ?
            """,
            (date, time)
        )
        result = self.parent.cursor.fetchone()
        return result[0] == 0  # No overlapping schedules

    def add_schedule_to_db(self, client_name, dog_name, service_name, date, time, price):
        try:
            client_id = self.parent.get_client_id(client_name)
            dog_id = self.parent.get_dog_id(dog_name)
            service_id = self.parent.get_service_id_by_name(service_name)
            price_id = self.parent.get_price_id_by_service_id(service_id)

            if not all([client_id, dog_id, service_id, price_id]):
                QMessageBox.warning(self, "Error", "Invalid client, dog, or service.")
                return

            self.parent.cursor.execute(
                "INSERT INTO Schedules (client_id, dog_id, service_id, date, time, price_id) VALUES (?, ?, ?, ?, ?, ?)",
                (client_id, dog_id, service_id, date, time, price_id)
            )
            self.parent.conn.commit()
            QMessageBox.information(self, "Success", "Schedule added successfully!")
            self.refresh_schedule_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add schedule: {e}")

    def refresh_schedule_table(self, search_text=""):
        self.schedule_model.clear()
        self.schedule_model.setHorizontalHeaderLabels(["Client", "Dog", "Service", "Date", "Time", "Price"])

        try:
            query = """
                SELECT Clients.name, Dogs.name, Services.service_name, Schedules.date, Schedules.time, Prices.price
                FROM Schedules
                JOIN Clients ON Schedules.client_id = Clients.client_id
                JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                JOIN Services ON Schedules.service_id = Services.service_id
                JOIN Prices ON Schedules.price_id = Prices.price_id
                WHERE Clients.name LIKE ? OR Dogs.name LIKE ? OR Services.service_name LIKE ?
                ORDER BY Schedules.schedule_id DESC
            """
            search_pattern = f"%{search_text}%"
            self.parent.cursor.execute(query, (search_pattern, search_pattern, search_pattern))

            for row in self.parent.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.schedule_model.appendRow(row_data)
            self.schedule_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh schedule table: {e}")

    def search_schedules(self, text):
        self.refresh_schedule_table(search_text=text)

    def edit_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row >= 0:
            schedule_id = self.get_schedule_id_from_row(selected_row)
            if schedule_id is None:  # Check if schedule_id is None
                QMessageBox.warning(self, "Error", "Could not find schedule ID.")
                return  # Stop execution if no ID is found

            try:
                # Fetch existing schedule data
                self.parent.cursor.execute("""
                    SELECT Clients.name, Dogs.name, Services.service_name, Schedules.date, Schedules.time, Prices.price
                    FROM Schedules
                    JOIN Clients ON Schedules.client_id = Clients.client_id
                    JOIN Dogs ON Schedules.dog_id = Dogs.dog_id
                    JOIN Services ON Schedules.service_id = Services.service_id
                    JOIN Prices ON Schedules.price_id = Prices.price_id
                    WHERE Schedules.schedule_id = ?
                """, (schedule_id,))
                result = self.parent.cursor.fetchone()

                if result is None:  # Check if the query returned a result
                    QMessageBox.warning(self, "Error", "No schedule found with that ID.")
                    return

                client_name, dog_name, service_name, date, time, price = result  # Unpack only if result is not None

                dialog = EditScheduleDialog(self.parent, client_name, dog_name, service_name, date, time, price)
                if dialog.exec_() == QDialog.Accepted:
                    new_client, new_dog, new_service, new_date, new_time, new_price = dialog.get_values()
                    # Update database with new values
                    self.update_schedule_in_db(schedule_id, new_client, new_dog, new_service, new_date, new_time, new_price)
                    self.refresh_schedule_table()  # Refresh table after update

            except Exception as e:
                print(f"Error fetching schedule data for edit: {e}")
                QMessageBox.warning(self, "Error", "Failed to fetch schedule data.")

    def update_schedule_in_db(self, schedule_id, new_client, new_dog, new_service, new_date, new_time, New_price):
        try:
            # Fetch IDs for the new client, dog, service, and price
            client_id = self.parent.get_client_id(new_client)
            dog_id = self.parent.get_dog_id(new_dog)
            service_id = self.parent.get_service_id_by_name(new_service)
            price_id = self.parent.get_price_id_by_service_id(service_id)

            if not all([client_id, dog_id, service_id, price_id]):
                QMessageBox.warning(self, "Error", "Invalid client, dog, or service.")
                return

            # Update the schedule in the database
            self.parent.cursor.execute(
                """
                UPDATE Schedules
                SET client_id = ?, dog_id = ?, service_id = ?, date = ?, time = ?, price_id = ?
                WHERE schedule_id = ?
                """,
                (client_id, dog_id, service_id, new_date, new_time, price_id, schedule_id)
            )
            self.parent.conn.commit()
            QMessageBox.information(self, "Success", "Schedule updated successfully!")
            self.refresh_schedule_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update schedule: {e}")

    def delete_schedule(self):
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row >= 0:
            try:
                # Get the schedule_id for the selected row
                schedule_id = self.get_schedule_id_from_row(selected_row)

                if schedule_id is not None:  # Check if schedule_id was found
                    confirm = QMessageBox.question(
                        self, "Confirm Delete", 
                        "Are you sure you want to delete this schedule?", 
                        QMessageBox.Yes | QMessageBox.No
                    )
                    if confirm == QMessageBox.Yes:
                        # Delete the schedule from the database
                        self.parent.cursor.execute("DELETE FROM Schedules WHERE schedule_id = ?", (schedule_id,))
                        self.parent.conn.commit()
                        self.refresh_schedule_table()  # Refresh the table to reflect changes
                        QMessageBox.information(self, "Success", "Schedule deleted successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Could not find schedule ID.")

            except Exception as e:
                print(f"Error deleting schedule: {e}")
                QMessageBox.warning(self, "Error", "Failed to delete schedule.")

    def get_schedule_id_from_row(self, row):
        try:
            # Fetch the schedule_id for the selected row
            self.parent.cursor.execute("SELECT schedule_id FROM Schedules ORDER BY schedule_id DESC LIMIT 1 OFFSET ?", (row,))
            result = self.parent.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get schedule ID: {e}")
            return None