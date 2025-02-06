from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton,
    QTableView, QMessageBox, QHeaderView, QDialog
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSignal
import sqlite3
import re


class AddServiceDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Service")
        layout = QFormLayout()

        self.service_name_input = QLineEdit()
        self.service_price_input = QLineEdit()

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.accept)

        layout.addRow("Service Name:", self.service_name_input)
        layout.addRow("Price:", self.service_price_input)
        layout.addRow(add_button)

        self.setLayout(layout)

    def get_values(self):
        return self.service_name_input.text(), self.service_price_input.text()

class EditServiceDialog(QDialog):
    def __init__(self, parent, service_name, price):
        super().__init__(parent)
        self.setWindowTitle("Edit Service")
        layout = QFormLayout()

        self.service_name_input = QLineEdit(service_name)
        self.service_price_input = QLineEdit(str(price))

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)

        layout.addRow("Service Name:", self.service_name_input)
        layout.addRow("Price:", self.service_price_input)
        layout.addRow(save_button)

        self.setLayout(layout)

    def get_values(self):
        return self.service_name_input.text(), self.service_price_input.text()

class ServicesTab(QWidget):
    service_updated = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.conn = sqlite3.connect("canine_haircut_service.db")
        self.cursor = self.conn.cursor()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_search_bar()
        self.create_service_table()
        self.create_action_buttons()
        self.refresh_service_table()

    def create_search_bar(self):
        self.service_search_bar = QLineEdit()
        self.service_search_bar.setPlaceholderText("Search Service Name or Price")
        self.service_search_bar.textChanged.connect(self.search_services)
        self.layout.addWidget(self.service_search_bar)

    def create_service_table(self):
        self.service_table = QTableView()
        self.service_model = QStandardItemModel()
        self.service_model.setHorizontalHeaderLabels(["Service Name", "Price"])
        self.service_table.setModel(self.service_model)
        self.service_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.service_table)

    def create_action_buttons(self):
        button_layout = QHBoxLayout()
        
        self.add_service_button = QPushButton("Add Service")
        self.add_service_button.clicked.connect(self.show_add_service_dialog)
        
        self.edit_service_button = QPushButton("Edit Service")
        self.edit_service_button.clicked.connect(self.edit_service)
        
        self.delete_service_button = QPushButton("Delete Service")
        self.delete_service_button.clicked.connect(self.delete_service)

        button_layout.addWidget(self.add_service_button)
        button_layout.addWidget(self.edit_service_button)
        button_layout.addWidget(self.delete_service_button)
        
        self.layout.addLayout(button_layout)

    def show_add_service_dialog(self):
        dialog = AddServiceDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            service_name, price = dialog.get_values()
            if not self.validate_price(price):
                QMessageBox.warning(self, "Error", "Invalid price format. Must be numeric with up to two decimals.")
                return
            if service_name and price:
                self.add_service_to_db(service_name, price)
            else:
                QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def add_service_to_db(self, name, price):
        try:
            self.cursor.execute("INSERT INTO Services (service_name) VALUES (?)", (name,))
            service_id = self.cursor.lastrowid
            self.cursor.execute("INSERT INTO Prices (service_id, price) VALUES (?, ?)", (service_id, price))
            self.conn.commit()            
            self.refresh_service_table()
            QMessageBox.information(self, "Success", "Service added successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add service: {e}")

    def refresh_service_table(self, search_text=""):
        self.service_model.clear()
        self.service_model.setHorizontalHeaderLabels(["Service Name", "Price"])

        query = """
            SELECT Services.service_name, Prices.price
            FROM Services
            INNER JOIN Prices ON Services.service_id = Prices.service_id
            WHERE Services.service_name LIKE ? OR Prices.price LIKE ?
            ORDER BY Services.service_id DESC
        """
        search_pattern = f"%{search_text}%"
        self.cursor.execute(query, (search_pattern, search_pattern))

        for row in self.cursor.fetchall():
            row_data = [QStandardItem(str(item)) for item in row]
            self.service_model.appendRow(row_data)

        self.service_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

    def search_services(self, text):
        self.refresh_service_table(search_text=text)

    def edit_service(self):
        selected_row = self.service_table.currentIndex().row()
        if selected_row >= 0:
            service_id = self.get_service_id_from_row(selected_row)
            if service_id:
                service_name, price = self.get_service_name_price(service_id)
                dialog = EditServiceDialog(self, service_name, price)
                if dialog.exec_() == QDialog.Accepted:
                    new_service_name, new_price = dialog.get_values()
                    if not self.validate_price(new_price):
                        QMessageBox.warning(self, "Error", "Invalid price format. Must be numeric with up to two decimals.")
                        return
                    self.update_service_in_db(service_id, new_service_name, new_price)

    def update_service_in_db(self, service_id, new_name, new_price):
        try:
            self.cursor.execute("UPDATE Services SET service_name = ? WHERE service_id = ?", (new_name, service_id))
            self.cursor.execute("UPDATE Prices SET price = ? WHERE service_id = ?", (new_price, service_id))
            self.conn.commit()            
            self.service_updated.emit()
            self.refresh_service_table()
            QMessageBox.information(self, "Success", "Service updated successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update service: {e}")

    def delete_service(self):
        selected_row = self.service_table.currentIndex().row()
        
        if selected_row < 0:
            QMessageBox.warning(self, "Error", "Please select a service to delete.")
            return

        service_id = self.get_service_id_from_row(selected_row)
        if not service_id:
            QMessageBox.warning(self, "Error", "Failed to retrieve service ID.")
            return

        confirm = QMessageBox.question(
            self, "Confirm Delete", 
            "Are you sure you want to delete this service?", 
            QMessageBox.Yes | QMessageBox.No
        )

        if confirm == QMessageBox.No:
            return  # User canceled deletion

        try:
            # Using a transaction to ensure atomicity
            self.cursor.execute("DELETE FROM Prices WHERE service_id = ?", (service_id,))
            self.cursor.execute("DELETE FROM Services WHERE service_id = ?", (service_id,))
            self.conn.commit()

            QMessageBox.information(self, "Success", "Service deleted successfully!")
            self.refresh_service_table()

        except sqlite3.Error as e:
            self.conn.rollback()  # Rollback in case of an error
            QMessageBox.warning(self, "Error", f"Failed to delete service: {e}")

    def get_service_id_from_row(self, row):
        self.cursor.execute("SELECT service_id FROM Services ORDER BY service_id DESC LIMIT 1 OFFSET ?", (row,))
        result = self.cursor.fetchone()
        return result[0] if result else None

    def get_service_name_price(self, service_id):
        self.cursor.execute("""
            SELECT service_name, price
            FROM Services
            JOIN Prices ON Services.service_id = Prices.service_id
            WHERE Services.service_id = ?
        """, (service_id,))
        result = self.cursor.fetchone()
        return result if result else ("", "")

    def validate_price(self, price):
        return bool(re.match(r"^\d+(\.\d{1,2})?$", str(price)))  # Ensures numeric value with up to 2 decimals

    def closeEvent(self, event):
        self.cursor.close()
        self.conn.close()
        event.accept()