"""Diálogos auxiliares para altas y selección de fecha.

AddUserDialog: captura nombre y legajo (docket) de un nuevo empleado.
AssignDayDialog: selector de fecha con calendario emergente (no valida reglas).
"""

from PyQt6.QtCore import QDate
from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QDateEdit,
)


class AddUserDialog(QDialog):
    """Diálogo simple para ingresar nombre y docket del empleado."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Agregar usuario")
        self._name = QLineEdit()
        self._docket = QLineEdit()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Nombre"))
        layout.addWidget(self._name)
        layout.addWidget(QLabel("Docket"))
        layout.addWidget(self._docket)

        btns = QHBoxLayout()
        btn_ok = QPushButton("Guardar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def values(self) -> tuple[str, str]:
        return self._name.text().strip(), self._docket.text().strip()


class AssignDayDialog(QDialog):
    """Diálogo de calendario para elegir una fecha (formato ISO al leer)."""
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Asignar día")
        self._date = QDateEdit()
        self._date.setCalendarPopup(True)
        self._date.setDate(QDate.currentDate())

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Fecha"))
        layout.addWidget(self._date)

        btns = QHBoxLayout()
        btn_ok = QPushButton("Asignar")
        btn_cancel = QPushButton("Cancelar")
        btn_ok.clicked.connect(self.accept)
        btn_cancel.clicked.connect(self.reject)
        btns.addWidget(btn_ok)
        btns.addWidget(btn_cancel)
        layout.addLayout(btns)

    def date_iso(self) -> str:
        qd = self._date.date()
        return f"{qd.year():04d}-{qd.month():02d}-{qd.day():02d}"


