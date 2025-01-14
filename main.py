import sys  
from PyQt5 import QtWidgets ,QtCore, QtGui   
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QSizeGrip
from main_interface import Ui_Main  
import sqlite3 

class MainWindow(QtWidgets.QMainWindow):  
    def __init__(self):  
        super(MainWindow, self).__init__()  
        self.is_logged_in = False
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)  
        self.central_widget = QtWidgets.QWidget(self)  
        self.setCentralWidget(self.central_widget)  
        self.ui = Ui_Main()  
        self.ui.setupUi(self.central_widget)  
        QSizeGrip(self.ui.size_grip)
        self.resize(1200, 600)
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
        self.ui.addClient_2.clicked.connect(lambda: self.showWindow('Add_Pet_Frame'))
        self.ui.clientPushButton.clicked.connect(lambda: self.showWindow('Clients_frame'))
        self.ui.pushButton_4.clicked.connect(lambda: self.showWindow('addScheduleFrame'))
        self.ui.buttonNoti.clicked.connect(lambda: self.showNotificationLis())
        self.ui.petPushButton.clicked.connect(lambda: self.showWindow('petFrame'))
        self.ui.scheduleButton.clicked.connect(lambda: self.showWindow('scheduleFrame'))
        self.ui.ServiceButton.clicked.connect(lambda: self.showWindow('serviceFrame'))
        self.ui.pushButton_9.clicked.connect(lambda: self.login())

        self.show()

    def logout(self):
        self.showWindow('LoginFrame')
        self.ui.side_menu_container.setFixedWidth(0)
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