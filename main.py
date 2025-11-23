import sqlite3
import sys

from PyQt6 import uic
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication, QWidget, QTableWidgetItem, QHeaderView
)


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


class CoffeeWidget(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi(open("main.ui", encoding="utf-8"), self)
        self.sql_conn = SQLConnector("coffee.sqlite")
        self.initUI()

    def initUI(self):
        self.update_table()

    def update_table(self):
        cursor = self.sql_conn.connection.cursor()
        rows = cursor.execute("SELECT * FROM Beans").fetchall()
        for i in range(len(rows)):
            rows[i] = list(rows[i])
        rows.reverse()
        headers = ["ID", "Название сорта", "Степень прожарки", "Молотый/в зернах", "Описание вкуса", "Цена", "Объем упаковки"]
        self.tableWidget.clear()
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setRowCount(len(rows))
        self.tableWidget.setColumnCount(len(headers))
        self.tableWidget.setHorizontalHeaderLabels(headers)
        for r in range(len(rows)):
            for c in range(len(headers)):
                item = QTableWidgetItem(str(rows[r][c]), Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                self.tableWidget.setItem(r, c, item)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = CoffeeWidget()
    ex.show()
    sys.exit(app.exec())