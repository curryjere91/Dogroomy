from PyQt5.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableView, QHeaderView, QMessageBox
from PyQt5.QtGui import QStandardItemModel, QStandardItem


class ClientsTab(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent  # Reference to the main window
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        # Input Form
        self.client_name_input = QLineEdit()
        self.client_phone_input = QLineEdit()
        add_client_button = QPushButton("Add Client")
        add_client_button.clicked.connect(self.add_client)

        form_layout = QFormLayout()
        form_layout.addRow("Client Name:", self.client_name_input)
        form_layout.addRow("Client Phone:", self.client_phone_input)
        form_layout.addRow(add_client_button)
        self.layout.addLayout(form_layout)

        # Client Table View
        self.client_table = QTableView()
        self.client_model = QStandardItemModel()
        self.client_table.setModel(self.client_model)
        self.client_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.client_table)

        # Refresh the table on initialization
        self.refresh_client_table()

    def add_client(self):
        name = self.client_name_input.text()
        phone = self.client_phone_input.text()

        if name and phone:
            self.parent.cursor.execute("INSERT INTO Clients (name, phone) VALUES (?, ?)", (name, phone))
            self.parent.conn.commit()
            QMessageBox.information(self, "Success", "Client added successfully!")
            self.client_name_input.clear()
            self.client_phone_input.clear()
            self.refresh_client_table()
        else:
            QMessageBox.warning(self, "Error", "Please fill in all fields.")

    def refresh_client_table(self):
        self.client_model.clear()
        self.client_model.setHorizontalHeaderLabels(["Name", "Phone"])
        try:
            self.parent.cursor.execute("SELECT name, phone FROM Clients ORDER BY client_id DESC")
            for row in self.parent.cursor.fetchall():
                row_data = [QStandardItem(str(item)) for item in row]
                self.client_model.appendRow(row_data)
        except Exception as e:
            print(f"Error refreshing client table: {e}")
            QMessageBox.warning(self, "Error", "Failed to refresh client table.")
