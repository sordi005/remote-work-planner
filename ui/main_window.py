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
from PyQt6.QtGui import QColor, QBrush
from exceptions import AppError
from services.user_service import UserService
from services.assignment_service import AsignacionService
from .dialogs import AddUserDialog
from datetime import date, timedelta
from PyQt6.QtWidgets import QButtonGroup
from PyQt6.QtWidgets import QMessageBox
from config import RESOURCES_DIR
from PyQt6.QtGui import QCursor


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
        self.resize(1280, 800)
        self.setMinimumSize(1000, 680)
        self._user_service = UserService()
        self._assign_service = AsignacionService()

        # Sidebar (izquierda): botón de alta y lista de empleados
        sidebar = QFrame()
        sidebar.setFrameShape(QFrame.Shape.NoFrame)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(12)

        btn_add_user = QPushButton("Agregar Empleado")
        btn_add_user.setProperty("btn", "primary")
        btn_add_user.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        empleados_label = QLabel("Empleados:")
        empleados_label.setProperty("role", "section") 
        empleados_list = QListWidget()
        self._employees_list = empleados_list
        # Evitar rectángulo punteado de foco en la lista
        self._employees_list.setFocusPolicy(Qt.FocusPolicy.NoFocus)
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

        # Botones de acción (derecha): Editar / Eliminar
        self._btn_edit = QPushButton("Editar empleado")
        self._btn_edit.setProperty("btn", "secondary")
        self._btn_delete = QPushButton("Eliminar empleado")
        self._btn_delete.setProperty("btn", "danger")
        self._btn_edit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_delete.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self._btn_edit.setEnabled(False)
        self._btn_delete.setEnabled(False)
        self._btn_edit.setVisible(False)
        self._btn_delete.setVisible(False)

        header_row = QHBoxLayout()
        header_row.setSpacing(12)
        header_row.addLayout(header_box, 1)
        header_row.addStretch(1)
        header_row.addWidget(self._btn_edit)
        header_row.addWidget(self._btn_delete)

        header_frame = QFrame()
        header_frame.setObjectName("headerPanel")
        header_frame.setLayout(header_row)
        content_layout.addWidget(header_frame)

        # Fila de información (horizontal): estado semanal + último registro (en cajas)
        info_row = QHBoxLayout()
        info_row.setSpacing(16)

        # Registrado esta semana
        self._reg_title = QLabel("Registrado")
        self._reg_title.setProperty("role", "metricTitle")
        self._reg_value = QLabel("-")
        self._reg_value.setProperty("role", "metricValue")
        reg_box = QVBoxLayout()
        reg_box.setSpacing(2)
        reg_box.addWidget(self._reg_title)
        reg_box.addWidget(self._reg_value)

        # Último registro (fecha)
        self._last_date_title = QLabel("Último registro")
        self._last_date_title.setProperty("role", "metricTitle")
        self._last_date_value = QLabel("")
        self._last_date_value.setProperty("role", "metricValue")
        last_date_box = QVBoxLayout()
        last_date_box.setSpacing(2)
        last_date_box.addWidget(self._last_date_title)
        last_date_box.addWidget(self._last_date_value)

        # Último día (nombre)
        self._last_day_title = QLabel("Último día")
        self._last_day_title.setProperty("role", "metricTitle")
        self._last_day_value = QLabel("")
        self._last_day_value.setProperty("role", "metricValue")
        last_day_box = QVBoxLayout()
        last_day_box.setSpacing(2)
        last_day_box.addWidget(self._last_day_title)
        last_day_box.addWidget(self._last_day_value)

        info_row.addLayout(reg_box)
        info_row.addLayout(last_date_box)
        info_row.addLayout(last_day_box)
        info_row.addStretch(8)

        info_frame = QFrame()
        info_frame.setObjectName("infoPanel")
        info_frame.setLayout(info_row)
        content_layout.addWidget(info_frame)

        # Calendario semanal (maqueta con selección de un día)
        self._lbl_week = QLabel("")
        self._lbl_week.setObjectName("weekTitle")
        self._lbl_week.setStyleSheet("font-size: 13px;")

        days_row = QHBoxLayout() 
        days_row.setSpacing(8)
        self._day_buttons: list[QPushButton] = []
        self._day_group = QButtonGroup(self)
        self._day_group.setExclusive(True)

        for _ in range(7):
            btn = QPushButton("-")
            btn.setCheckable(True)
            btn.setMinimumHeight(68)
            btn.setProperty("kind", "day")
            btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
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
        self._btn_edit.clicked.connect(self._on_edit_user)
        self._btn_delete.clicked.connect(self._on_delete_user)

        # Carga inicial de datos de UI
        self.load_users()
        self._setup_week_ui(date.today())
        # Estado de selección de día en calendario
        self._selected_date_iso = None
        # Cargar estilos QSS si existe
        try:
            qss_path = RESOURCES_DIR / "style.qss"
            if qss_path.exists():
                with open(qss_path, "r", encoding="utf-8") as f:
                    self.setStyleSheet(f.read())
        except Exception:
            pass

    def load_users(self) -> None:
        """Carga y pinta el listado de empleados en el sidebar.

        El `id` queda asociado como `UserRole` en cada item para recuperarlo al seleccionar.
        """
        users = self._user_service.list_users()
        self._employees_list.clear()
        # Consultar estado semanal para pintar usuarios registrados
        try:
            status_list = self._assign_service.users_week_status(users)
        except Exception:
            status_list = [(u, False) for u in users]

        from PyQt6.QtWidgets import QListWidgetItem
        # Separar no-registrados (arriba) y registrados (abajo)
        pending = [(u, f) for (u, f) in status_list if not f]
        done = [(u, f) for (u, f) in status_list if f]

        marked_brush = QBrush(QColor(46, 204, 113, 140))  # verde translúcido más visible en dark

        def _add_items(pairs: list[tuple]):
            for u, is_marked in pairs:
                it = QListWidgetItem(u.name)
                it.setData(Qt.ItemDataRole.UserRole, u.id)
                if is_marked:
                    it.setBackground(marked_brush)
                    # Ligeramente más claro el texto para destacar sin molestar
                    it.setForeground(QBrush(QColor(207, 243, 218)))
                    it.setToolTip("Registrado esta semana")
                else:
                    it.setToolTip("Sin registro esta semana")
                self._employees_list.addItem(it)

        _add_items(pending)
        _add_items(done)

    
    def _clear_employee_info(self) -> None:
        """Resetea los labels del encabezado cuando no hay selección."""
        self._lbl_name.setText("Nombre completo")
        self._lbl_docket.setText("Legajo")
        self._reg_value.setText("-")
        self._last_date_value.setText("")
        self._last_day_value.setText("")

    
    def _on_user_selected(self, current, previous) -> None:
        """Actualiza el encabezado con datos y estado del empleado seleccionado."""
        if current is None:
            self._clear_employee_info()
            self._btn_edit.setEnabled(False)
            self._btn_delete.setEnabled(False)
            self._btn_edit.setVisible(False)
            self._btn_delete.setVisible(False)
            # Limpiar selección de calendario
            for b in self._day_buttons:
                b.setChecked(False)
            return
        user_id = current.data(Qt.ItemDataRole.UserRole)
        if user_id is None:
            self._clear_employee_info()
            self._btn_edit.setEnabled(False)
            self._btn_delete.setEnabled(False)
            self._btn_edit.setVisible(False)
            self._btn_delete.setVisible(False)
            return
        user = self._user_service.get_user(int(user_id))
        if user is None:
            self._clear_employee_info()
            self._btn_edit.setEnabled(False)
            self._btn_delete.setEnabled(False)
            self._btn_edit.setVisible(False)
            self._btn_delete.setVisible(False)
            for b in self._day_buttons:
                b.setChecked(False)
            return
        
        # Setear encabezado
        self._lbl_name.setText(f"{user.name}")
        self._lbl_docket.setText(f"Legajo: {user.docket}")
        # Estado de la semana y último registro
        registered = self._assign_service.is_registered_this_week(int(user_id))
        self._reg_value.setText("Sí" if registered else "No")
        # Aplicar semántica de color en QSS
        try:
            self._reg_value.setProperty("status", "yes" if registered else "no")
            self._reg_value.style().unpolish(self._reg_value)
            self._reg_value.style().polish(self._reg_value)
        except Exception:
            pass
        last = self._assign_service.latest_for_user(int(user_id))
        if last:
            self._last_date_value.setText(f"{last.date}")
            self._last_day_value.setText(f"{last.week_day}")
        else:
            self._last_date_value.setText("")
            self._last_day_value.setText("")
        # Habilitar acciones al tener un empleado válido
        self._btn_edit.setEnabled(True)
        self._btn_delete.setEnabled(True)
        self._btn_edit.setVisible(True)
        self._btn_delete.setVisible(True)

        # Pintar el día de la semana actual si existe registro
        try:
            rec = self._assign_service.current_week_record(int(user_id))
        except Exception:
            rec = None
        # Limpiar selección previa
        for b in self._day_buttons:
            b.setChecked(False)
        if rec is not None:
            # Buscar botón cuyo date_iso coincide con rec.date y marcarlo
            target_iso = rec.date
            for b in self._day_buttons:
                if b.property("date_iso") == target_iso and b.isEnabled():
                    b.setChecked(True)
                    break

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
            allow_repeat = False
            # Advertencia si coincide con el día de la semana anterior
            try:
                if self._assign_service.is_same_weekday_as_prev_week(int(user_id), date_iso):
                    prev_rec = self._assign_service.prev_week_record(int(user_id), date_iso)
                    if prev_rec:
                        # Formateo amigable de fecha previa
                        try:
                            y, m, d = map(int, str(prev_rec.date).split("-"))
                            prev_pretty = f"{d:02d}/{m:02d}/{y:04d}"
                        except Exception:
                            prev_pretty = str(prev_rec.date)
                        msg = (
                            f"La semana pasada registró {prev_rec.week_day} {prev_pretty}.\n\n"
                            "¿Deseas continuar igualmente?"
                        )
                    else:
                        msg = (
                            "Este empleado se registró el mismo día la semana anterior.\n\n"
                            "¿Deseas continuar?"
                        )
                    warn = QMessageBox.warning(
                        self,
                        "Advertencia",
                        msg,
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                        QMessageBox.StandardButton.No,
                    )
                    if warn == QMessageBox.StandardButton.Yes:
                        allow_repeat = True
                    else:
                        return
            except Exception:
                pass

            if self._assign_service.is_registered_this_week(int(user_id)):
                resp = QMessageBox.question(
                    self,
                    "Cambiar registro",
                    f"Este empleado ya tiene un registro esta semana.\n\n¿Quieres cambiarlo a {pretty_day}?",
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
                self._assign_service.change_week_assignment(int(user_id), date_iso, allow_repeat_prev_week=allow_repeat)
            else:
                resp = QMessageBox.question(
                    self,
                    "Confirmar asignación",
                    f"¿Registrar el día {pretty_day} para este empleado?",
                )
                if resp != QMessageBox.StandardButton.Yes:
                    return
                self._assign_service.assign_day(int(user_id), date_iso, allow_repeat_prev_week=allow_repeat)

            # Refrescar listado y encabezado conservando selección
            selected_id = int(user_id)
            self.load_users()
            self._select_user_in_list(selected_id)
            # Si el usuario quedó registrado, marcar en lista y calendario
            # (load_users ya repinta la lista; _on_user_selected marcará calendario)

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

    def _on_edit_user(self) -> None:
        """Edita el empleado seleccionado usando el diálogo de alta pre-rellenado."""
        current_item = self._employees_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "Selecciona un empleado", "Primero selecciona un empleado en el listado.")
            return
        user_id = current_item.data(Qt.ItemDataRole.UserRole)
        user = self._user_service.get_user(int(user_id)) if user_id is not None else None
        if user is None:
            QMessageBox.information(self, "No encontrado", "No se pudo cargar el empleado seleccionado.")
            return

        dlg = AddUserDialog(self)
        # Pre-cargar valores actuales
        try:
            dlg._name.setText(user.name)  # tipo simple; diálogo interno
            dlg._docket.setText(user.docket)
        except Exception:
            pass

        if dlg.exec():
            name, docket = dlg.values()
            if not name or not docket:
                QMessageBox.information(self, "Datos incompletos", "Nombre y Docket son obligatorios.")
                return
            try:
                self._user_service.update_user(int(user_id), name, docket)
                # Refrescar y mantener selección
                self.load_users()
                self._select_user_in_list(int(user_id))
            except AppError as e:
                QMessageBox.warning(self, "Error", str(e))

    def _on_delete_user(self) -> None:
        """Elimina el empleado seleccionado previa confirmación."""
        current_item = self._employees_list.currentItem()
        if current_item is None:
            QMessageBox.information(self, "Selecciona un empleado", "Primero selecciona un empleado en el listado.")
            return
        user_id = current_item.data(Qt.ItemDataRole.UserRole)
        if user_id is None:
            QMessageBox.information(self, "Selección inválida", "No se pudo identificar al empleado.")
            return
        resp = QMessageBox.question(
            self,
            "Eliminar empleado",
            "¿Seguro que deseas eliminar este empleado? Esta acción no se puede deshacer.",
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            # Borrado consistente: eliminar registros y luego usuario
            self._assign_service.delete_user_and_records(int(user_id))
            self.load_users()
            self._clear_employee_info()
            self._btn_edit.setEnabled(False)
            self._btn_delete.setEnabled(False)
            self._btn_edit.setVisible(False)
            self._btn_delete.setVisible(False)
        except AppError as e:
            QMessageBox.warning(self, "Error", str(e))


def run_app() -> None:
    app = QApplication.instance() or QApplication([])
    win = MainWindow()
    win.show()
    app.exec()


