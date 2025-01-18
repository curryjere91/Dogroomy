from PyQt5.QtWidgets import (
    QWidget, QFormLayout, QLineEdit, QPushButton, QTableView, QHeaderView, QMessageBox, QVBoxLayout
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class ServicesTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # Reference to the main window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Input Form
        self.service_name_input = QLineEdit()
        self.service_price_input = QLineEdit()
        add_service_button = QPushButton("Add Service")
        add_service_button.clicked.connect(self.add_service)

        form_layout = QFormLayout()
        form_layout.addRow("Service Name:", self.service_name_input)
        form_layout.addRow("Price:", self.service_price_input)
        form_layout.addRow(add_service_button)
        self.layout.addLayout(form_layout)

        # Service Table View
        self.service_table = QTableView()
        self.service_model = QStandardItemModel()
        self.service_table.setModel(self.service_model)
        self.service_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.service_table)

        # Refresh the table on initialization
        self.refresh_service_table()

    def add_service(self):
        """Add a new service and its price to the database."""
        name = self.service_name_input.text()
        try:
            price = float(self.service_price_input.text())
            if not name:
                raise ValueError("Service name cannot be empty.")

            self.parent.cursor.execute("INSERT INTO Services (service_name) VALUES (?)", (name,))
            service_id = self.parent.cursor.lastrowid
            self.parent.cursor.execute("INSERT INTO Prices (service_id, price) VALUES (?, ?)", (service_id, price))
            self.parent.conn.commit()

            QMessageBox.information(self, "Success", "Service added successfully!")
            self.service_name_input.clear()
            self.service_price_input.clear()
            self.refresh_service_table()
        except ValueError as e:
            QMessageBox.warning(self, "Error", f"Invalid input: {e}")
        except Exception as e:
            print(f"Error adding service: {e}")
            QMessageBox.warning(self, "Error", "Failed to add service.")

    def refresh_service_table(self):
        """Refresh the service table with the latest data."""
        self.service_model.clear()
        self.service_model.setHorizontalHeaderLabels(["Service Name", "Price"])
        try:
            self.parent.cursor.execute("""
                SELECT Services.service_name, Prices.price
                FROM Services
                INNER JOIN Prices ON Services.service_id = Prices.service_id
                ORDER BY Services.service_id DESC
            """)
            for row in self.parent.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.service_model.appendRow(row_data)
        except Exception as e:
            print(f"Error refreshing service table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh service table.")
