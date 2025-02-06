from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, 
    QLabel, QComboBox, QMessageBox, QTableView, QHeaderView, QDialog, QDialogButtonBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, pyqtSignal

class EditDogDialog(QDialog):
    def __init__(self, parent, name="", breed="", client_name=""):
        super().__init__(parent)
        self.setWindowTitle("Edit Dog")
        layout = QFormLayout(self)

        self.name_edit = QLineEdit(name)
        self.breed_edit = QLineEdit(breed)
        self.client_dropdown = QComboBox()
        self.client_dropdown.addItems(parent.get_clients())
        self.client_dropdown.setCurrentText(client_name)

        layout.addRow("Dog Name:", self.name_edit)
        layout.addRow("Breed:", self.breed_edit)
        layout.addRow("Select Client:", self.client_dropdown)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addRow(button_box)

    def get_values(self):
        return self.name_edit.text(), self.breed_edit.text(), self.client_dropdown.currentText()

class DogsTab(QWidget):
    dog_updated = pyqtSignal()
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QVBoxLayout()

        self.dogs_search_bar = QLineEdit()
        self.dogs_search_bar.setPlaceholderText("Search Dog, Breed or Client")
        self.dogs_search_bar.textChanged.connect(self.search_dogs)
        layout.addWidget(self.dogs_search_bar)

        self.dog_table = QTableView()
        self.dog_model = QStandardItemModel()
        self.dog_table.setModel(self.dog_model)
        self.dog_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.dog_table)

        button_layout = QHBoxLayout()
        add_dog_button = QPushButton("Add Dog")
        add_dog_button.clicked.connect(self.add_dog)
        button_layout.addWidget(add_dog_button)

        edit_dog_button = QPushButton("Edit Dog")
        edit_dog_button.clicked.connect(self.edit_dog)
        button_layout.addWidget(edit_dog_button)

        delete_dog_button = QPushButton("Delete Dog")
        delete_dog_button.clicked.connect(self.delete_dog)
        button_layout.addWidget(delete_dog_button)

        layout.addLayout(button_layout)
        self.setLayout(layout)
        self.refresh_dog_table()

    def add_dog(self):
        dialog = EditDogDialog(self.parent)
        if dialog.exec_() == QDialog.Accepted:
            name, breed, client_name = dialog.get_values()
            self.add_dog_to_db(name, breed, client_name)

    def add_dog_to_db(self, name, breed, client_name):
        try:
            client_id = self.parent.get_client_id(client_name)
            if client_id is None:
                QMessageBox.warning(self, "Error", "Client not found.")
                return
            self.parent.cursor.execute(
                "INSERT INTO Dogs (client_id, name, breed) VALUES (?, ?, ?)", 
                (client_id, name, breed)
            )
            self.parent.conn.commit()
            self.refresh_dog_table()
            QMessageBox.information(self, "Success", "Dog added successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to add dog: {e}")

    def edit_dog(self):
        selected_row = self.dog_table.currentIndex().row()
        if selected_row >= 0:
            dog_id = self.get_dog_id_from_row(selected_row)
            name, breed, client_name = self.get_dog_name_breed_client(dog_id)
            dialog = EditDogDialog(self.parent, name, breed, client_name)
            if dialog.exec_() == QDialog.Accepted:
                new_name, new_breed, new_client_name = dialog.get_values()
                self.update_dog_in_db(dog_id, new_name, new_breed, new_client_name)

    def update_dog_in_db(self, dog_id, new_name, new_breed, new_client_name):
        try:
            client_id = self.parent.get_client_id(new_client_name)
            if client_id is None:
                QMessageBox.warning(self, "Error", "Client not found.")
                return
            self.parent.cursor.execute(
                "UPDATE Dogs SET name = ?, breed = ?, client_id = ? WHERE dog_id = ?", 
                (new_name, new_breed, client_id, dog_id)
            )
            self.parent.conn.commit()
            self.dog_updated.emit()
            self.refresh_dog_table()
            QMessageBox.information(self, "Success", "Dog updated successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to update dog: {e}")

    def delete_dog(self):
        selected_row = self.dog_table.currentIndex().row()
        if selected_row >= 0:
            dog_id = self.get_dog_id_from_row(selected_row)
            confirm = QMessageBox.question(
                self, "Confirm Delete", 
                "Are you sure you want to delete this dog?", 
                QMessageBox.Yes | QMessageBox.No
            )
            if confirm == QMessageBox.Yes:
                self.remove_dog_from_db(dog_id)

    def remove_dog_from_db(self, dog_id):
        try:
            self.parent.cursor.execute("DELETE FROM Dogs WHERE dog_id = ?", (dog_id,))
            self.parent.conn.commit()
            QMessageBox.information(self, "Success", "Dog deleted successfully!")
            self.refresh_dog_table()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to delete dog: {e}")

    def refresh_dog_table(self, search_text=""):
        self.dog_model.clear()
        self.dog_model.setHorizontalHeaderLabels(["Name", "Breed", "Client"])

        try:
            query = """
                SELECT Dogs.name, Dogs.breed, Clients.name 
                FROM Dogs 
                INNER JOIN Clients ON Dogs.client_id = Clients.client_id
                WHERE Dogs.name LIKE ? OR Dogs.breed LIKE ? OR Clients.name LIKE ?
                ORDER BY Dogs.dog_id DESC
            """
            search_pattern = f"%{search_text}%"
            self.parent.cursor.execute(query, (search_pattern, search_pattern, search_pattern))
            for row in self.parent.cursor.fetchall():
                self.dog_model.appendRow([QStandardItem(str(item)) for item in row])
            self.dog_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to refresh dog table: {e}")

    def search_dogs(self, text):
        self.refresh_dog_table(search_text=text)

    def get_dog_id_from_row(self, row):
        try:
            self.parent.cursor.execute("SELECT dog_id FROM Dogs ORDER BY dog_id DESC LIMIT 1 OFFSET ?", (row,))
            result = self.parent.cursor.fetchone()
            return result[0] if result else None
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get dog ID: {e}")
            return None

    def get_dog_name_breed_client(self, dog_id):
        try:
            self.parent.cursor.execute(
                "SELECT Dogs.name, Dogs.breed, Clients.name FROM Dogs JOIN Clients ON Dogs.client_id = Clients.client_id WHERE dog_id = ?", 
                (dog_id,)
            )
            result = self.parent.cursor.fetchone()
            return result if result else (None, None, None)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to get dog details: {e}")
            return (None, None, None)