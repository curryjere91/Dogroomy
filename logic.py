import sqlite3
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import pyqtSignal
from main_interface import Ui_Main
from PyQt5 import QtWidgets
from datetime import datetime, timedelta  
import locale  
from PyQt5 import QtWidgets, QtGui, QtCore 



class ClientManager:  
    def __init__(self):  
        self.ui = Ui_Main()  
        self.conn = sqlite3.connect("canine_haircut_service.db")  
        self.cursor = self.conn.cursor()  
        self.current_date = datetime.now()  

        # Connect signals  
        self.schedule_updated = pyqtSignal()  # New signal for schedule changes  
        self.client_updated = pyqtSignal()     # New signal for client changes  
        self.dog_updated = pyqtSignal()        # New signal for dog changes  
        self.service_updated = pyqtSignal()    # New signal for service changes  

    def close_connection(self):  
        self.conn.close() 


    def refresh_client_table(self, tableClients):  
        self.cursor.execute("SELECT * FROM Clients")  
        datos = self.cursor.fetchall()  
        tableClients.setRowCount(len(datos))  

        for fila, cliente in enumerate(datos):  
            for columna, valor in enumerate(cliente):  
                item = QtWidgets.QTableWidgetItem(str(valor))  
                tableClients.setItem(fila, columna, item)  

        tableClients.setColumnHidden(0, True)


##Load Dias Turnos###############################
    def check_schedule(self, date):
        self.cursor.execute("""
            SELECT 
                c.name AS cliente_nombre,
                c.surname AS cliente_apellido,
                s.service_name AS servicio,
                sc.time AS hora,
                sc.color
            FROM Schedules sc
            JOIN Clients c ON sc.client_id = c.client_id
            JOIN Services s ON sc.service_id = s.service_id
            WHERE sc.date = ? order by hora ASC
        """, (date,))

        return self.cursor.fetchall() 
               
        self.conn.commit()
    def load_week(self, group_box,grupListTurno):  
        locale.setlocale(locale.LC_TIME, 'Spanish_Spain')
        for i in range(7):  
            dia = self.current_date + timedelta(days=i)  
            day_label = group_box.findChild(QtWidgets.QLabel, f"labelNumDia{i + 1}")  
            name_label = group_box.findChild(QtWidgets.QLabel, f"labelNomDia{i + 1}")  
            name_ano = group_box.findChild(QtWidgets.QLabel, f"labelMonth_2")  
            name_mes = group_box.findChild(QtWidgets.QLabel, f"labelMonth")  
            day_label.setText(dia.strftime("%d"))  
            name_label.setText(dia.strftime("%A").capitalize()) 
            name_ano.setText(str(dia.year))
            name_mes.setText(dia.strftime("%B").capitalize())
            list_turn = grupListTurno.findChild(QtWidgets.QGroupBox,f"grupListTurno{i + 1}")
            turnos = self.check_schedule(dia.strftime("%Y-%m-%d"))
            layout = list_turn.layout()
            if layout is not None:
                for j in reversed(range(layout.count())):
                    widget = layout.itemAt(j).widget()
                    if widget is not None:
                        widget.deleteLater()
            for turno in turnos:
                nombre, apellido, servicio, horas, color = turno
                self.create_turno_widget(list_turn, nombre, apellido, servicio, horas, color)
       
    def previous_week(self, group_box,groupBox_18):  
        self.current_date -= timedelta(weeks=1)  
        self.load_week(group_box,groupBox_18)  

    def next_week(self,group_box,groupBox_18):  
        self.current_date += timedelta(weeks=1)  
        self.load_week(group_box,groupBox_18) 

    def previous_month(self,group_box,groupBox_18):      
        if self.current_date.month == 1:  
            self.current_date = self.current_date.replace(year=self.current_date.year - 1, month=12)  
        else:  
            self.current_date = self.current_date.replace(month=self.current_date.month - 1)  
    
        self.load_week(group_box,groupBox_18) 

    def next_month(self,group_box,groupBox_18):          
        if self.current_date.month == 12:  
            self.current_date = self.current_date.replace(year=self.current_date.year + 1, month=1)  
        else:  
            self.current_date = self.current_date.replace(month=self.current_date.month + 1)  
        self.load_week(group_box,groupBox_18)  
    
    def previous_year(self,group_box,groupBox_18):  
        self.current_date -= timedelta(days=365)  # Restar un año  
        self.load_week(group_box,groupBox_18)  

    def next_year(self,group_box,groupBox_18):  
        self.current_date += timedelta(days=365)  # Sumar un año  
        self.load_week(group_box,groupBox_18)

    def load_schedule(self,grupListTurno, nombre, apellido, servicio, horas, color):
        layout = grupListTurno.layout()  
        if layout is not None:  
            for i in reversed(range(layout.count())):  
                widget = layout.itemAt(i).widget()  
                if widget is not None:  
                    widget.deleteLater()
        self.create_turno_widget(grupListTurno, nombre, apellido, servicio, horas, color) 
        
           
        
##Clientes###############################
    def add_client(self, name, surname, address, email, phone):
        self.cursor.execute("INSERT INTO Clients (name, surname, address, email, phone) VALUES (?, ?, ?, ?, ?)",
                            (name, surname, address, email, phone))
               
        self.conn.commit()
    
    def del_client(self, name, surname, address, email, phone):  
        query = """  
        DELETE FROM Clients   
        WHERE name = ? AND surname = ? AND address = ? AND email = ? AND phone = ?  
        """  
        self.cursor.execute(query, (name, surname, address, email, phone))  
        self.conn.commit()  

    def edit_client(self, client_id, name, surname, address, email, phone):  
        query = """  
        UPDATE Clients  
        SET name = ?, surname = ?, address = ?, email = ?, phone = ?  
        WHERE client_id = ?  
        """  
        self.cursor.execute(query, (name, surname, address, email, phone, client_id))  
        self.conn.commit()  

    def get_clients(self):
        self.cursor.execute("SELECT name, surname, client_id FROM Clients")
        datos = self.cursor.fetchall()  
        return datos

##Mascotas###############################
    def refresh_pet_table(self, tablePets):
        query = """
        SELECT Dogs.name, Dogs.breed, CONCAT(Clients.name, ' ', Clients.surname) AS cliente
        FROM Dogs
        JOIN Clients ON Dogs.client_id = Clients.client_id
    """
        self.cursor.execute(query)
        datos = self.cursor.fetchall()
        tablePets.setRowCount(len(datos))
        for fila, dog in enumerate(datos):  
            for columna, valor in enumerate(dog):
                item = QtWidgets.QTableWidgetItem(valor)
                tablePets.setItem(fila, columna, item)

    def add_pet(self, name, breed, client_id):
        print(name, breed, client_id)
        self.cursor.execute("INSERT INTO Dogs (client_id, name, breed) VALUES (?, ?, ?)",
                            (client_id, name, breed, ))
        self.conn.commit()

    def create_turno_widget(self, grupListTurno, nombre, apellido, servicio, horas, color):  
    # Crea una instancia del widget TurnoWidget  
        turno_widget = TurnoWidget(nombre, apellido, servicio, horas, color)           
        if not grupListTurno.layout():  
            layout = QtWidgets.QVBoxLayout(grupListTurno)  
           # grupListTurno.setLayout(layout)  
        grupListTurno.layout().addWidget(turno_widget)  
    
        return turno_widget             

class ScheduleManager:  
    def __init__(self):  
        self.ui = Ui_Main()  
        self.conn = sqlite3.connect("canine_haircut_service.db")  
        self.cursor = self.conn.cursor()


class TurnoWidget(QtWidgets.QGroupBox):  
    def __init__(self, nombre, apellido, servicio, horas, tema, parent=None):  
        super().__init__(parent)  
         
        self.themes = {  
            "verde": {  
                "color": "rgb(52, 175, 0)", 
                "background-color": "rgba(79, 241, 19, 50)"  
            },  
            "amarillo": {  
                "color": "rgb(255, 193, 7)",    
                "background-color": "rgba(255, 255, 102, 50)" 
            },  
            "rojo": {  
                "color": "rgb(255, 0, 0)", 
                "background-color": "rgba(255, 205, 210, 50)" 
            }  
        }

        if tema in self.themes:  
            self.color = self.themes[tema]["color"]  
            self.background_color = self.themes[tema]["background-color"]  
        else:  
            self.color = "rgb(0, 0, 0)" 
            self.background_color = "rgb(255, 255, 255)" 

        # Configuración del grupo  
        self.setMinimumSize(QtCore.QSize(0, 70))  
        self.setMaximumSize(QtCore.QSize(150, 70))  
        self.setStyleSheet("")  
        self.setTitle("")  
        self.setObjectName("classTurno")  

        # Etiqueta con el nombre  
        self.turnNom = QtWidgets.QLabel(self)  
        self.turnNom.setGeometry(QtCore.QRect(20, 0, 111, 16))  
        font = QtGui.QFont()  
        font.setBold(True)  
        font.setWeight(75)  
        self.turnNom.setFont(font)  
        self.turnNom.setStyleSheet(f"color: {self.color};")  
        self.turnNom.setObjectName("turnNom")  
        self.turnNom.setText(f"{nombre} {apellido}")  

        # Línea vertical  
        self.turnLine = QtWidgets.QFrame(self)  
        self.turnLine.setGeometry(QtCore.QRect(10, 0, 5, 61))  
        self.turnLine.setMinimumSize(QtCore.QSize(5, 0))  
        self.turnLine.setMaximumSize(QtCore.QSize(5, 16777215))  
        self.turnLine.setStyleSheet(f"background-color: {self.color};")  
        self.turnLine.setFrameShape(QtWidgets.QFrame.VLine)  
        self.turnLine.setFrameShadow(QtWidgets.QFrame.Sunken)  

        # Etiqueta del servicio  
        self.trunServicio = QtWidgets.QLabel(self)  
        self.trunServicio.setGeometry(QtCore.QRect(20, 20, 111, 16))  
        self.trunServicio.setStyleSheet(f"color: {self.color};")  
        self.trunServicio.setObjectName("trunServicio")  
        self.trunServicio.setText(servicio)  

        # Etiqueta del horario  
        self.turnHorario = QtWidgets.QLabel(self)  
        self.turnHorario.setGeometry(QtCore.QRect(20, 40, 111, 16))  
        self.turnHorario.setStyleSheet(f"color: {self.color};")  
        self.turnHorario.setObjectName("turnHorario")  
        self.turnHorario.setText(horas)  

        # Fondo del grupo  
        self.turnBackGro = QtWidgets.QFrame(self)  
        self.turnBackGro.setGeometry(QtCore.QRect(10, 0, 150, 61))  
        self.turnBackGro.setMinimumSize(QtCore.QSize(150, 0))  
        self.turnBackGro.setMaximumSize(QtCore.QSize(150, 16777215))  
        self.turnBackGro.setStyleSheet(f"background-color: {self.background_color};")  
        self.turnBackGro.setFrameShape(QtWidgets.QFrame.VLine)  
        self.turnBackGro.setFrameShadow(QtWidgets.QFrame.Sunken)  

    