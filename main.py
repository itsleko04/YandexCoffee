import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidgetItem, QHeaderView, QTableWidget
)


class Event:
    """Глобальная реализация событий"""
    def __init__(self):
        self.__functions = []

    def connect(self, func):
        """Подписать метод"""
        self.__functions.append(func)

    def disconnect(self, func):
        """Отписать метод"""
        self.__functions.remove(func)

    def invoke(self):
        """Вызвать событие"""
        for func in self.__functions:
            func()

    def clear(self):
        self.__functions.clear()


class SQLConnector:
    def __init__(self, database):
        self.database = database
        self.connect()
        
        self.connection.autocommit = True
        self.last_cursor = None

    def execute_with_response(self, query: str):
        cursor = self.connection.cursor()
        self.last_cursor = cursor
        cursor.execute(query)
        return cursor.execute(query).fetchall()

    def execute_without_response(self, query: str):
        cursor = self.connection.cursor()
        self.last_cursor = cursor
        cursor.execute(query)

    def connect(self):
        self.connection = sqlite3.connect(self.database)

    def close(self):
        self.connection.close()


class AddCoffeeWidget(QWidget):
    def __init__(self, parent: CoffeeWidget):
        super().__init__()
        self.w_parent = parent
        self.sql_conn = self.w_parent.sql_conn
        self.initUI()

    def initUI(self):
        uic.loadUi(open("addEditCoffeeForm.ui", encoding="utf-8"), self)
        self.addButton.clicked.connect(self.save_data)

    def closeEvent(self, a0):
        self.w_parent.on_close.disconnect(self.close)
        return super().closeEvent(a0)

    def save_data(self):
        title = self.titleEdit.text()
        roasting = self.roastingEdit.text()
        grounded = self.groundedEdit.text()
        taste = self.tasteEdit.text()
        try:
            cost = int(self.costEdit.text())
            volume = int(self.volumeEdit.text())
        except ValueError:
            return
        self.sql_conn.execute_without_response(f"INSERT INTO Beans VALUES({self.w_parent.coffies_count + 1}, \
                                               '{title}', '{roasting}', '{grounded}', '{taste}', {cost}, {volume})")
        self.w_parent.show_table()
        self.close()


class CoffeeWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.on_close = Event()

        self.coffies_count = 0
        self.sql_conn = SQLConnector("coffee.sqlite")

        uic.loadUi(open("main.ui", encoding="utf-8"), self)
        self.initUI()

    def closeEvent(self, a0):
        self.on_close.invoke()
        return super().closeEvent(a0)

    def initUI(self):
        self.show_table()
        self.addButton.clicked.connect(self.add_record)
        self.tableWidget.cellChanged.connect(self.update_sql_with_table)

    def show_table(self):
        cursor = self.sql_conn.connection.cursor()
        rows = cursor.execute("SELECT * FROM Beans").fetchall()
        headers = ["ID", "Название сорта", "Степень прожарки", "Молотый/в зернах", "Описание вкуса", "Цена", "Объем упаковки"]
        self.tableWidget.clear()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        self.coffies_count = 0
        for r in range(len(rows)):
            self.coffies_count += 1
            for c in range(len(headers)):
                item = QTableWidgetItem(str(rows[r][c]), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tableWidget.setItem(r, c, item)
    
    def add_record(self):
        self.widget = AddCoffeeWidget(self)
        self.widget.show()
        self.on_close.connect(self.widget.close)
    
    def update_sql_with_table(self, rowIndex, columnIndex):
        row = []
        for c in range(self.tableWidget.columnCount()):
            row.append(self.tableWidget.item(rowIndex, c).text())
        self.sql_conn.execute_without_response(f"UPDATE Beans SET title='{row[1]}', roasting='{row[2]}', \
            grounded='{row[3]}', taste='{row[4]}', cost={row[5]}, pack_volume={row[6]} WHERE id={rowIndex + 1}")
        self.sql_conn.connection.commit()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeWidget()
    ex.show()
    sys.exit(app.exec())