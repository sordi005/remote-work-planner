"""Ventana principal (UI): sidebar de empleados y panel de información/acciones.

Estructura visual:
- Izquierda: sidebar con botón de alta y lista de empleados
- Derecha: encabezado con datos del empleado y calendario semanal de asignación

Nota: Esta vista no contiene la lógica de negocio. Invoca servicios para consultar
estado y asignar/cambiar registros.
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QFrame,
    QLabel,
    QPushButton,
    QListWidget,
    QMainWindow,
    QSplitter,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)
from exceptions import AppError
from services.user_service import UserService
from services.assignment_service import AsignacionService
from .dialogs import AddUserDialog
from datetime import date, timedelta
from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtWidgets import QMessageBox


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación.

    Se encarga de:
    - Renderizar el sidebar (alta y listado de empleados)
    - Mostrar el encabezado con datos del empleado seleccionado
    - Renderizar un calendario semanal simplificado para seleccionar un día
    - Delegar en los servicios la carga de datos y validaciones de negocio
    """

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Trabajo Remoto - Gestor")
        self.resize(1200, 700)
        self.setMinimumSize(900, 600)
        self._user_service = UserService()
        self._assign_service = AsignacionService()

        # Sidebar (izquierda): botón de alta y lista de empleados
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.NoFrame)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(12)

        btn_add_user = QPushButton("Agregar Empleado")
        empleados_label = QLabel("Empleados:")
        empleados_label.setProperty("role", "section") 
        empleados_list = QListWidget()
        self._employees_list = empleados_list
        sidebar.setMinimumWidth(260)
        sidebar.setMaximumWidth(360)

        sidebar_layout.addWidget(btn_add_user)
        sidebar_layout.addSpacing(12)
        sidebar_layout.addWidget(empleados_label)
        sidebar_layout.addWidget(empleados_list, 1)

        # Contenido (derecha): encabezado + info + calendario semanal
        content = QFrame()
        content.setFrameShape(QFrame.Shape.NoFrame) 
        content_layout = QVBoxLayout(content)
        content_layout.setContentsMargins(24, 24, 24, 24)
        content_layout.setSpacing(12)

        # Encabezado horizontal: nombre (título) y legajo (subtítulo)
        self._lbl_name = QLabel("Nombre completo")
        self._lbl_name.setStyleSheet("font-size: 22px; font-weight: 600;")

        self._lbl_docket = QLabel("Legajo")
        self._lbl_docket.setStyleSheet("color: #666; font-size: 14px;")

        header_box = QVBoxLayout() # QVBoxLayout : Vertical Box Layout
        header_box.setSpacing(2)
        header_box.addWidget(self._lbl_name)
        header_box.addWidget(self._lbl_docket)

        header_frame = QFrame()
        header_frame.setLayout(header_box)
        content_layout.addWidget(header_frame)

        # Fila de información (horizontal): estado semanal + último registro
        info_row = QHBoxLayout()
        info_row.setSpacing(8)

        self._lbl_registered = QLabel("Registrado: -")
        self._lbl_registered.setStyleSheet("font-size: 13px;")

        self._lbl_last_date = QLabel("Último registro: ")
        self._lbl_last_date.setStyleSheet("font-size: 13px;")

        self._lbl_last_day = QLabel("Último Día: ")
        self._lbl_last_day.setStyleSheet("font-size: 13px;")

        info_row.addWidget(self._lbl_registered)
        info_row.addWidget(self._lbl_last_date)
        info_row.addWidget(self._lbl_last_day)
        info_row.addStretch(8)

        info_frame = QFrame()
        info_frame.setLayout(info_row)
        content_layout.addWidget(info_frame)

        # Calendario semanal (maqueta con selección de un día)
        self._lbl_week = QLabel("")
        self._lbl_week.setStyleSheet("font-size: 13px; color: #666;")

        days_row = QHBoxLayout() 
        days_row.setSpacing(8)
        self._day_buttons: list[QPushButton] = []
        self._day_group = QButtonGroup(self)
        self._day_group.setExclusive(True)

        for _ in range(7):
            btn = QPushButton("-")
            btn.setCheckable(True)
            btn.setMinimumHeight(60)
            self._day_buttons.append(btn)
            self._day_group.addButton(btn)
            days_row.addWidget(btn)

        calendar_frame = QFrame()
        cal_layout = QVBoxLayout(calendar_frame)
        cal_layout.setContentsMargins(0, 12, 0, 0)
        cal_layout.setSpacing(8)
        cal_layout.addWidget(self._lbl_week)
        cal_layout.addLayout(days_row)
        content_layout.addWidget(calendar_frame)

        content_layout.addStretch(15)

        # Splitter principal: fija el sidebar y expande el contenido
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(sidebar)
        splitter.addWidget(content)
        splitter.setSizes([260, 740])
        splitter.setChildrenCollapsible(False)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)

        # Contenedor raíz de la ventana
        root = QWidget()
        root_layout = QVBoxLayout(root)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.addWidget(splitter)
        self.setCentralWidget(root)

        # Conexiones de UI
        btn_add_user.clicked.connect(self._on_add_user)
        self._employees_list.currentItemChanged.connect(self._on_user_selected)
        self._day_group.buttonClicked.connect(self._on_day_selected)

        # Carga inicial de datos de UI
        self.load_users()
        self._setup_week_ui(date.today())

    def load_users(self) -> None:
        """Carga y pinta el listado de empleados en el sidebar.

        El `id` queda asociado como `UserRole` en cada item para recuperarlo al seleccionar.
        """
        users = self._user_service.list_users()
        self._employees_list.clear()
        for u in users:
            item_text = u.name
            from PyQt6.QtWidgets import QListWidgetItem
            it = QListWidgetItem(item_text)
            it.setData(Qt.ItemDataRole.UserRole, u.id)
            self._employees_list.addItem(it)

    
    def _clear_employee_info(self) -> None:
        """Resetea los labels del encabezado cuando no hay selección."""
        self._lbl_name.setText("Nombre completo")
        self._lbl_docket.setText("Legajo")
        self._lbl_registered.setText("Registrado esta semana: -")
        self._lbl_last_date.setText("Último Fecha: ")
        self._lbl_last_day.setText("Último Día: ")

    
    def _on_user_selected(self, current, previous) -> None:
        """Actualiza el encabezado con datos y estado del empleado seleccionado."""
        if current is None:
            self._clear_employee_info()
            return
        user_id = current.data(Qt.ItemDataRole.UserRole)
        if user_id is None:
            self._clear_employee_info()
            return
        user = self._user_service.get_user(int(user_id))
        if user is None:
            self._clear_employee_info()
            return
        
        # Setear encabezado
        self._lbl_name.setText(f"{user.name}")
        self._lbl_docket.setText(f"Legajo: {user.docket}")
        # Estado de la semana y último registro
        registered = self._assign_service.is_registered_this_week(int(user_id))
        self._lbl_registered.setText(f"Registrado esta semana: {'Sí' if registered else 'No'}")
        last = self._assign_service.latest_for_user(int(user_id))
        if last:
            self._lbl_last_date.setText(f"Último - Fecha: {last.date}")
            self._lbl_last_day.setText(f"Último - Día: {last.week_day}")
        else:
            self._lbl_last_date.setText("Último - Fecha: ")
            self._lbl_last_day.setText("Último - Día: ")

    # ===== Calendario semanal =====
    def _setup_week_ui(self, base: date) -> None:
        """Configura el calendario semanal para la semana que contiene `base`.

        Calcula lunes-domingo y pinta 7 botones con nombre del día y fecha.
        Lunes/Sábado/Domingo se deshabilitan por regla de negocio.
        """
        start = base - timedelta(days=base.weekday())  # lunes
        end = start + timedelta(days=6)  # domingo
        self._current_week_start = start
        self._lbl_week.setText(f"Semana: {start.strftime('%d/%m/%Y')} - {end.strftime('%d/%m/%Y')}")

        weekday_names = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]
        for i, btn in enumerate(self._day_buttons):
            d = start + timedelta(days=i)
            btn.setText(f"{weekday_names[i]}\n{d.strftime('%d/%m')}")
            btn.setChecked(False)
            # Regla UX: deshabilitar Lunes(0), Sábado(5), Domingo(6)
            btn.setEnabled(i not in (0, 5, 6))
            # Guardar fecha ISO en propiedad
            btn.setProperty("date_iso", d.isoformat())

    def _on_day_selected(self, button: QPushButton) -> None:
        """Gestiona la selección de un día: confirma y asigna/cambia si corresponde."""
        self._selected_date_iso = button.property("date_iso")

        # Validar selección de empleado
        current_item = self._employees_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "Selecciona un empleado", "Primero selecciona un empleado en el listado.")
            return
        user_id = current_item.data(Qt.ItemDataRole.UserRole)
        if user_id is None:
            QMessageBox.information(self, "Selecciona un empleado", "Selección inválida de empleado.")
            return

        # Confirmaciones según estado semanal
        date_iso = self._selected_date_iso
        # Texto amigable dd/mm/YYYY
        try:
            y, m, d = map(int, str(date_iso).split("-"))
            pretty_day = f"{d:02d}/{m:02d}/{y:04d}"
        except Exception:
            pretty_day = str(date_iso)

        try:
            if self._assign_service.is_registered_this_week(int(user_id)):
                resp = QMessageBox.question(
                    self,
                    "Cambiar registro",
                    f"Este empleado ya tiene un registro esta semana.\n\n¿Quieres cambiarlo a {pretty_day}?",
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
                self._assign_service.change_week_assignment(int(user_id), date_iso)
            else:
                resp = QMessageBox.question(
                    self,
                    "Confirmar asignación",
                    f"¿Registrar el día {pretty_day} para este empleado?",
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
                self._assign_service.assign_day(int(user_id), date_iso)

            # Refrescar listado y encabezado conservando selección
            selected_id = int(user_id)
            self.load_users()
            self._select_user_in_list(selected_id)

        except AppError as e:
            QMessageBox.warning(self, "Regla de negocio", str(e))

    def _select_user_in_list(self, target_id: int) -> None:
        """Selecciona en el sidebar el item cuyo UserRole coincide con `target_id`."""
        for i in range(self._employees_list.count()):
            it = self._employees_list.item(i)
            if it.data(Qt.ItemDataRole.UserRole) == target_id:
                self._employees_list.setCurrentRow(i)
                break
        

    def _on_add_user(self) -> None:
        
        dialog = AddUserDialog(self)
        if dialog.exec():
            name, docket = dialog.values()
            if not name or not docket:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.information(self, "Datos incompletos", "Nombre y Docket son obligatorios.")
                return
            try:
                self._user_service.create_user(name, docket)
                self.load_users()
            except AppError as e:
                from PyQt6.QtWidgets import QMessageBox
                QMessageBox.warning(self, "Error", str(e))


def run_app() -> None:
    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    win.show()
    app.exec()


