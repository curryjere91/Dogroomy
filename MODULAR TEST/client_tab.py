from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableView, 
    QMessageBox, QHeaderView, QHBoxLayout, QDialog
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import pyqtSignal

class AddClientDialog(QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle("Add Client")
        layout = QFormLayout()

        self.client_name_input = QLineEdit()
        self.client_phone_input = QLineEdit()

        add_button = QPushButton("Add")
        add_button.clicked.connect(self.accept)

        layout.addRow("Client Name:", self.client_name_input)
        layout.addRow("Client Phone:", self.client_phone_input)
        layout.addRow(add_button)

        self.setLayout(layout)

    def get_values(self):
        return self.client_name_input.text(), self.client_phone_input.text()

class EditClientDialog(QDialog):
    def __init__(self, parent, name, phone):
        super().__init__(parent)
        self.setWindowTitle("Edit Client")
        layout = QFormLayout()

        self.client_name_input = QLineEdit(name)
        self.client_phone_input = QLineEdit(phone)

        save_button = QPushButton("Save")
        save_button.clicked.connect(self.accept)
        
        layout.addRow("Client Name:", self.client_name_input)
        layout.addRow("Client Phone:", self.client_phone_input)
        layout.addRow(save_button)

        self.setLayout(layout)

    def get_values(self):
        return self.client_name_input.text(), self.client_phone_input.text()

class ClientsTab(QWidget):
    client_updated = pyqtSignal()
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.create_search_bar()
        self.create_client_table()
        self.create_action_buttons()
        self.refresh_client_table()

    def create_search_bar(self):
        self.client_search_bar = QLineEdit()
        self.client_search_bar.setPlaceholderText("Search Client Name or Phone")
        self.client_search_bar.textChanged.connect(self.search_clients)
        self.layout.addWidget(self.client_search_bar)

    def create_client_table(self):
        self.client_table = QTableView()
        self.client_model = QStandardItemModel()
        self.client_model.setHorizontalHeaderLabels(["Name", "Phone"])
        self.client_table.setModel(self.client_model)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.client_table)

    def create_action_buttons(self):
        button_layout = QHBoxLayout()
        self.add_client_button = QPushButton("Add Client")
        self.add_client_button.clicked.connect(self.show_add_client_dialog)
        self.edit_client_button = QPushButton("Edit Client")
        self.edit_client_button.clicked.connect(self.edit_client)
        self.delete_client_button = QPushButton("Delete Client")
        self.delete_client_button.clicked.connect(self.delete_client)
        button_layout.addWidget(self.add_client_button)
        button_layout.addWidget(self.edit_client_button)
        button_layout.addWidget(self.delete_client_button)
        self.layout.addLayout(button_layout)

    def show_add_client_dialog(self):
        dialog = AddClientDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            name, phone = dialog.get_values()
            if not self.validate_phone(phone):
                QMessageBox.warning(self, "Error", "Phone number must contain only digits.")
                return
            if name and phone:
                self.add_client_to_db(name, phone)
            else:
                QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def add_client_to_db(self, name, phone):
        try:
            self.parent.cursor.execute("INSERT INTO Clients (name, phone) VALUES (?, ?)", (name, phone))
            self.parent.conn.commit()
            self.refresh_client_table()
            QMessageBox.information(self, "Success", "Client added successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add client: {e}")

    def refresh_client_table(self, search_text=""):
        self.client_model.clear()
        self.client_model.setHorizontalHeaderLabels(["Name", "Phone"])

        try:
            query = "SELECT name, phone FROM Clients"
            params = ()
            if search_text:
                query += " WHERE name LIKE ? OR phone LIKE ?"
                search_pattern = f"%{search_text}%"
                params = (search_pattern, search_pattern)
            query += " ORDER BY client_id DESC"

            self.parent.cursor.execute(query, params)
            for row in self.parent.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.client_model.appendRow(row_data)
            self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh client table: {e}")

    def search_clients(self, text):
        self.refresh_client_table(search_text=text)

    def edit_client(self):
        selected_row = self.client_table.currentIndex().row()
        if selected_row >= 0:
            name = self.client_model.item(selected_row, 0).text()
            phone = self.client_model.item(selected_row, 1).text()
            dialog = EditClientDialog(self, name, phone)
            if dialog.exec_() == QDialog.Accepted:
                new_name, new_phone = dialog.get_values()
                if not self.validate_phone(new_phone):
                    QMessageBox.warning(self, "Error", "Phone number must contain only digits.")
                    return
                self.update_client_in_db(name, phone, new_name, new_phone)

    def update_client_in_db(self, old_name, old_phone, new_name, new_phone):
        try:
            self.parent.cursor.execute(
                "UPDATE Clients SET name = ?, phone = ? WHERE name = ? AND phone = ?",
                (new_name, new_phone, old_name, old_phone)
            )
            self.parent.conn.commit()
            self.client_updated.emit()
            self.refresh_client_table()
            QMessageBox.information(self, "Success", "Client updated successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update client: {e}")

    def delete_client(self):
        selected_row = self.client_table.currentIndex().row()
        if selected_row >= 0:
            name = self.client_model.item(selected_row, 0).text()
            phone = self.client_model.item(selected_row, 1).text()
            confirm = QMessageBox.question(
                self, "Confirm Delete", 
                f"Are you sure you want to delete {name}?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.remove_client_from_db(name, phone)

    def remove_client_from_db(self, name, phone):
        try:
            # Delete the client, the database will cascade delete related dogs and schedules
            self.parent.cursor.execute("DELETE FROM Clients WHERE name = ? AND phone = ?", (name, phone))
            self.parent.conn.commit()
            self.refresh_client_table()
            QMessageBox.information(self, "Success", "Client and all associated dogs and schedules deleted successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete client: {e}")

    def validate_phone(self, phone):
        return phone.isdigit()