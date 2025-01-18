from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QTableView, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class CurrentSchedulesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # Reference to the main window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Search bar
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Search by Client, Dog, Service, or Date...")
        self.search_bar.textChanged.connect(self.search_schedules)
        self.layout.addWidget(self.search_bar)

        # Buttons
        delete_schedule_button = QPushButton("Delete Schedule")
        delete_schedule_button.clicked.connect(self.delete_schedule)
        self.layout.addWidget(delete_schedule_button)

        # Table View
        self.schedule_table = QTableView()
        self.schedule_model = QStandardItemModel()
        self.schedule_table.setModel(self.schedule_model)
        self.layout.addWidget(self.schedule_table)

        # Refresh the table on initialization
        self.refresh_schedule_table()

    def refresh_schedule_table(self, search_text=""):
        """Refresh the table with current schedules."""
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
            """
            if search_text:
                query += """
                    WHERE Clients.name LIKE ? OR Dogs.name LIKE ? OR
                          Services.service_name LIKE ? OR Schedules.date LIKE ?
                """
                search_pattern = f"%{search_text}%"
                self.parent.cursor.execute(query, (search_pattern, search_pattern, search_pattern, search_pattern))
            else:
                self.parent.cursor.execute(query)

            for row in self.parent.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.schedule_model.appendRow(row_data)
        except Exception as e:
            print(f"Error refreshing schedule table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh schedule table.")

    def search_schedules(self, text):
        """Filter the schedules based on search input."""
        self.refresh_schedule_table(search_text=text)

    def delete_schedule(self):
        """Delete a selected schedule."""
        selected_row = self.schedule_table.currentIndex().row()
        if selected_row >= 0:
            schedule_id = self.parent.get_schedule_id_from_row(selected_row)
            if schedule_id:
                try:
                    confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this schedule?", QMessageBox.Yes | QMessageBox.No)
                    if confirm == QMessageBox.Yes:
                        self.parent.cursor.execute("DELETE FROM Schedules WHERE schedule_id = ?", (schedule_id,))
                        self.parent.conn.commit()
                        QMessageBox.information(self, "Success", "Schedule deleted successfully!")
                        self.refresh_schedule_table()
                except Exception as e:
                    print(f"Error deleting schedule: {e}")
                    QMessageBox.warning(self, "Error", "Failed to delete schedule.")
