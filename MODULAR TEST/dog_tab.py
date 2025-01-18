from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QFormLayout, QLineEdit, QComboBox, QPushButton, QTableView, QHeaderView, QMessageBox
)
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class DogsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # Reference to the main window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Input Form
        self.dog_name_input = QLineEdit()
        self.dog_breed_input = QLineEdit()
        self.dog_client_dropdown = QComboBox()
        self.update_client_dropdown()

        add_dog_button = QPushButton("Add Dog")
        add_dog_button.clicked.connect(self.add_dog)

        form_layout = QFormLayout()
        form_layout.addRow("Dog Name:", self.dog_name_input)
        form_layout.addRow("Dog Breed:", self.dog_breed_input)
        form_layout.addRow("Select Client:", self.dog_client_dropdown)
        form_layout.addRow(add_dog_button)
        self.layout.addLayout(form_layout)

        # Dog Table View
        self.dog_table = QTableView()
        self.dog_model = QStandardItemModel()
        self.dog_table.setModel(self.dog_model)
        self.dog_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.dog_table)

        # Refresh the table on initialization
        self.refresh_dog_table()

    def update_client_dropdown(self):
        """Populate the dropdown with clients from the database."""
        clients = self.parent.get_clients()  # Retrieve clients from the main app
        self.dog_client_dropdown.clear()
        self.dog_client_dropdown.addItems(clients)

    def add_dog(self):
        """Add a new dog to the database."""
        name = self.dog_name_input.text()
        breed = self.dog_breed_input.text()
        client_name = self.dog_client_dropdown.currentText()

        if name and breed and client_name:
            client_id = self.parent.get_client_id(client_name)
            self.parent.cursor.execute(
                "INSERT INTO Dogs (client_id, name, breed) VALUES (?, ?, ?)", (client_id, name, breed)
            )
            self.parent.conn.commit()
            QMessageBox.information(self, "Success", "Dog added successfully!")
            self.dog_name_input.clear()
            self.dog_breed_input.clear()
            self.refresh_dog_table()
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def refresh_dog_table(self):
        """Refresh the dog table with the latest data."""
        self.dog_model.clear()
        self.dog_model.setHorizontalHeaderLabels(["Name", "Breed", "Client"])
        try:
            self.parent.cursor.execute("""
                SELECT Dogs.name, Dogs.breed, Clients.name
                FROM Dogs
                INNER JOIN Clients ON Dogs.client_id = Clients.client_id
                ORDER BY Dogs.dog_id DESC
            """)
            for row in self.parent.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.dog_model.appendRow(row_data)
        except Exception as e:
            print(f"Error refreshing dog table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh dog table.")
