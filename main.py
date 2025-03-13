import sys  
from PyQt5 import QtWidgets ,QtCore, QtGui   
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizeGrip
from main_interface import Ui_Main  
import sqlite3 
from logic import *

class MainWindow(QtWidgets.QMainWindow):  
    def __init__(self):  
        super(MainWindow, self).__init__()  

        self.version = "1.2.4" #Control de version 

        self.is_logged_in = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  
        self.central_widget = QtWidgets.QWidget(self)  
        self.setCentralWidget(self.central_widget)  
        self.logic = ClientManager()
        self.ui = Ui_Main()  
        self.ui.setupUi(self.central_widget)  
        QSizeGrip(self.ui.size_grip)
        self.resize(1200, 600)
        self.ui.label.setText(QtCore.QCoreApplication.translate("Main", "DoGroomy " + self.version, None))
        self.ui.minimizePushButton.clicked.connect(lambda: self.showMinimized())
        self.ui.closePushButton.clicked.connect(lambda: self.close())
        self.ui.exitButton.clicked.connect(lambda: self.logout())
        self.ui.maximizePushButton.clicked.connect(lambda: self.restoreOrMaximizeWindow())
        self.clickedPosition = None
        self.ui.header_frame.mousePressEvent = self.headerMousePressEvent  
        self.ui.header_frame.mouseMoveEvent = self.headerMouseMoveEvent  
        self.ui.header_frame.mouseReleaseEvent = self.headerMouseReleaseEvent  
        self.ui.buttonShowMenu.clicked.connect(lambda: self.slideLeftMenu())
        self.ui.addClient.clicked.connect(lambda: self.showWindow('Add_Clients_frame'))
        self.ui.addPet.clicked.connect(lambda: self.showaddPetFrame())
        self.ui.clientPushButton.clicked.connect(lambda: self.showWindow('Clients_frame'))
        self.ui.pushButton_4.clicked.connect(lambda: self.showWindow('addScheduleFrame'))
        self.ui.buttonNoti.clicked.connect(lambda: self.showNotificationLis())
        self.ui.petPushButton.clicked.connect(lambda: self.showWindow('petFrame'))
        self.ui.scheduleButton.clicked.connect(lambda: self.showWindow('scheduleFrame'))
        self.ui.ServiceButton.clicked.connect(lambda: self.showWindow('serviceFrame'))
        self.ui.backAddClient.clicked.connect(lambda: self.showWindow('Clients_frame'))
        self.ui.backAddPet.clicked.connect(lambda: self.showWindow('petFrame'))
        self.ui.pushButton_9.clicked.connect(lambda: self.login())
        self.ui.pushButton_15.clicked.connect(lambda: self.addClient())
        self.ui.pushButton_16.clicked.connect(lambda: self.agregarMascota())
        self.ui.delPet.clicked.connect(lambda: self.agregarMascota())
        self.ui.tableClients.cellClicked.connect(self.on_cell_clicked)
        self.ui.delClient.clicked.connect(lambda: self.eliminarCliente(self.ui.tableClients.currentRow()))  
        self.ui.editClient.clicked.connect(lambda: self.editarCliente(self.ui.tableClients.currentRow()))  
        self.ui.lineEdit.textChanged.connect(self.filter_clients)
        self.ui.btnPreDay.clicked.connect(lambda:self.logic.previous_week(self.ui.groupBox_5,self.ui.groupBox_18))
        self.ui.btnNextDay.clicked.connect(lambda:self.logic.next_week(self.ui.groupBox_5,self.ui.groupBox_18))
        self.ui.btnNextYear.clicked.connect(lambda:self.logic.next_year(self.ui.groupBox_5,self.ui.groupBox_18))
        self.ui.btnPreYear.clicked.connect(lambda:self.logic.previous_year(self.ui.groupBox_5,self.ui.groupBox_18))
        self.ui.btnNextMonth.clicked.connect(lambda:self.logic.next_month(self.ui.groupBox_5,self.ui.groupBox_18))
        self.ui.btnPreMonth.clicked.connect(lambda:self.logic.previous_month(self.ui.groupBox_5,self.ui.groupBox_18))

        self.logic.load_week(self.ui.groupBox_5,self.ui.groupBox_18)
        
        self.show()

    

    def filter_clients(self):  
        search_text = self.ui.lineEdit.text().lower()  
        self.logic.refresh_client_table(self.ui.tableClients)  
        for row in range(self.ui.tableClients.rowCount()):  
            name_item = self.ui.tableClients.item(row, 1)  
            surname_item = self.ui.tableClients.item(row, 2)

            if name_item is not None and surname_item is not None:  
                name = name_item.text().lower()  
                surname = surname_item.text().lower()  
                if search_text in name or search_text in surname:  
                    self.ui.tableClients.showRow(row) 
                else:  
                    self.ui.tableClients.hideRow(row) 
            else:  
                self.ui.tableClients.hideRow(row)  

    def eliminarCliente(self, row):  
        if row >= 0:   
            datos_fila = []  
            for col in range(self.ui.tableClients.columnCount()):  
                item = self.ui.tableClients.item(row, col)  
                if item is not None:  
                    datos_fila.append(item.text())  
                else:  
                    datos_fila.append("")  
                    
            print(f"Fila: {row}, Contenido: {datos_fila}")   
            self.logic.del_client(datos_fila[1], datos_fila[2], datos_fila[3], datos_fila[4], datos_fila[5]) 
            self.logic.refresh_client_table(self.ui.tableClients)  
        else:  
            print("No hay fila seleccionada.")  

    def editarCliente(self, row):  
            if row >= 0:   
                datos_fila = []  
                for col in range(self.ui.tableClients.columnCount()):  
                    item = self.ui.tableClients.item(row, col)  
                    if item is not None:  
                        datos_fila.append(item.text())  
                    else:  
                        datos_fila.append("")         
                self.logic.edit_client(datos_fila[0], datos_fila[1], datos_fila[2], datos_fila[3], datos_fila[4],datos_fila[5]) 
                self.logic.refresh_client_table(self.ui.tableClients)  
            else:  
                print("No hay fila seleccionada.")  
    
    def on_cell_clicked(self, row, column):  
        datos_fila = []  
        for col in range(self.ui.tableClients.columnCount()):  
            item = self.ui.tableClients.item(row, col)  
            if item is not None:  
                datos_fila.append(item.text())  
            else:  
                datos_fila.append("")  
               
        print(f"Fila: {row}, Contenido: {datos_fila}")  
    
    def showaddPetFrame(self):
        self.showWindow('Add_Pet_Frame')
        self.ui.comboBox.clear()
        clients = self.logic.get_clients()
        for client in clients:
            clientName = client[0] + " " + client[1]
            idClient =  client[2]
            self.ui.comboBox.addItem(clientName, idClient)
    
    def agregarMascota(self):
        name = self.ui.lineEdit_9.text()
        breed = self.ui.lineEdit_7.text()
        selected_index = self.ui.comboBox.currentIndex()  
        client = self.ui.comboBox.itemData(selected_index)
        self.logic.add_pet(name, breed, client)
        self.logic.refresh_pet_table(self.ui.tablePets) 
        self.showWindow('petFrame')
       
    def addClient(self):
        name = self.ui.lineEdit_2.text()
        surname = self.ui.lineEdit_3.text()
        phone = self.ui.lineEdit_4.text()
        address = self.ui.lineEdit_5.text()
        email = self.ui.lineEdit_6.text()
        if not name or not surname or not phone or not address or not email:
            self.ui.Lmsjclient.setText("Todos los campos son obligatorios.")
            self.ui.Lmsjclient.setStyleSheet("color: red")
        else:           
            self.logic.add_client(name, surname, phone, address, email) 
            self.logic.refresh_client_table(self.ui.tableClients)  
            self.ui.lineEdit_2.clear()
            self.ui.lineEdit_3.clear()
            self.ui.lineEdit_4.clear()
            self.ui.lineEdit_5.clear()
            self.ui.lineEdit_6.clear()
            self.showWindow('Clients_frame')

    def logout(self):
        self.showWindow('LoginFrame')
        self.ui.side_menu_container.setFixedWidth(0)
        self.ui.userLabelTop.setText("")
        self.ui.userLabelTop.setFixedWidth(0)  
        self.ui.buttonShowMenu.setIcon(QIcon(QPixmap(u":/icons/icons/align-left.svg")))
        self.is_logged_in = False

    def login(self):  
        username = self.ui.Users.text()  
        password = self.ui.Pass.text()  

        
        conn = sqlite3.connect("canine_haircut_service.db")  
        cursor = conn.cursor()  

        
        cursor.execute('''  
            SELECT * FROM Employees WHERE username = ? AND password = ?;  
        ''', (username, password))  

        result = cursor.fetchone()  

         
        if result:  
            self.ui.LoginMsjLabel.setFixedWidth(0)
            self.is_logged_in = True
            self.showWindow('scheduleFrame')
            self.slideLeftMenu()
            self.ui.userLabelTop.setText(username)
            self.ui.userLabelTop.setFixedWidth(16777215)  
            self.logic.refresh_client_table(self.ui.tableClients)
            self.logic.refresh_pet_table(self.ui.tablePets) 
        else:  
            self.ui.LoginMsjLabel.setText("Usuario o contraseña incorrectos.") 
            self.ui.LoginMsjLabel.setStyleSheet("color: red;")  
            self.ui.LoginMsjLabel.setFixedWidth(16777215)  
        
        self.ui.Users.clear()  
        self.ui.Pass.clear()  

        
        cursor.close()  
        conn.close()    
   
    def showWindow(self, frame_to_show):    
        frames = [  
            self.ui.Add_Clients_frame,  
            self.ui.Add_Pet_Frame,  
            self.ui.Clients_frame,  
            self.ui.LoginFrame,  
            self.ui.RegistrerFrame,  
            self.ui.addScheduleFrame,  
            self.ui.panelNotifications,  
            self.ui.petFrame,  
            self.ui.scheduleFrame,  
            self.ui.serviceFrame,  
        ]  
 
        for frame in frames:  
            frame.setFixedWidth(0) 

        selected_frame = getattr(self.ui, frame_to_show, None)  

        if selected_frame:  
            selected_frame.setFixedWidth(16777215) 
      
    def showNotificationLis(self):
        if self.is_logged_in == True:
            width = self.ui.panelNotifications.width()
            if width == 0:
                new_width = 200
            else:
                new_width = 0
            self.animation = QtCore.QPropertyAnimation(self.ui.panelNotifications, b"maximumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(new_width)
            self.animation.start()

    def slideLeftMenu(self):
        if self.is_logged_in == True:
            width = self.ui.side_menu_container.width()
            if width == 0:
                new_width = 200
                self.ui.buttonShowMenu.setIcon(QIcon(QPixmap(u":/icons/icons/chevron-left.svg")))
            else:
                new_width = 0
                self.ui.buttonShowMenu.setIcon(QIcon(QPixmap(u":/icons/icons/align-left.svg")))
            self.animation = QtCore.QPropertyAnimation(self.ui.side_menu_container, b"maximumWidth")
            self.animation.setDuration(300)
            self.animation.setStartValue(width)
            self.animation.setEndValue(new_width)
            self.animation.start()

    def restoreOrMaximizeWindow(self):  
        if self.isMaximized():  
            self.showNormal()  
            self.ui.maximizePushButton.setIcon(QIcon(QPixmap(u":/icons/icons/maximize-2.svg")))
        else:  
            self.showMaximized()
            self.ui.maximizePushButton.setIcon(QIcon(QPixmap(u":/icons/icons/minimize-2.svg")))

    def headerMousePressEvent(self, e):  
        if e.button() == Qt.LeftButton:  
            self.clickedPosition = e.globalPos() - self.pos()  
            e.accept()  

    def headerMouseMoveEvent(self, e):  
        if self.clickedPosition is not None:  
            if e.buttons() == Qt.LeftButton:  
                if self.isMaximized()==False:
                    self.move(e.globalPos() - self.clickedPosition)  
                e.accept()  

    def headerMouseReleaseEvent(self, e):  
        if e.button() == Qt.LeftButton:  
            self.clickedPosition = None    

if __name__ == "__main__":  
    app = QtWidgets.QApplication(sys.argv)  
    window = MainWindow()  
    sys.exit(app.exec())  