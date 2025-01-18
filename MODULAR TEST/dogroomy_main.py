import sys
import sqlite3
from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from client_tab import ClientsTab
from dog_tab import DogsTab
from schedule_tab import ScheduleTab
from current_schedule_tab import CurrentSchedulesTab
from service_tab import ServicesTab
import database_utils

class CanineHaircutApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.conn = sqlite3.connect("canine_haircut_service.db")
        self.cursor = self.conn.cursor()

        self.setWindowTitle("Canine Haircut Service")
        self.setGeometry(100, 100, 600, 400)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Add tabs
        self.tabs.addTab(ClientsTab(self), "Clients")
        self.tabs.addTab(DogsTab(self), "Dogs")
        self.tabs.addTab(ServicesTab(self), "Services & Prices")
        self.tabs.addTab(ScheduleTab(self), "Set Schedule")
        self.tabs.addTab(CurrentSchedulesTab(self), "View Schedules")

# Main app exe
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CanineHaircutApp()
    window.show()
    sys.exit(app.exec_())
