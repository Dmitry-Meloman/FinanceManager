# main.py - Главный модуль приложения для учета финансов

import sys
import os
from PyQt6 import QtWidgets, QtGui, QtCore
from PyQt6.QtCore import Qt, QDate
from ui.main_window import Ui_MainWindow
from ui.add_transaction import Ui_AddTransactionDialog
import database as db

def get_resource_path(relative_path):
    """Получает абсолютный путь к ресурсу для работы как в режиме разработки, так и в режиме exe"""
    try:
        # PyInstaller создает временную папку и хранит путь в _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

class ReceiptViewerDialog(QtWidgets.QDialog):
    """Диалоговое окно для просмотра чека"""
    def __init__(self, receipt_path, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Просмотр чека")
        self.setMinimumSize(600, 800)
        
        layout = QtWidgets.QVBoxLayout(self)
        
        # Создаем QLabel для отображения изображения
        self.image_label = QtWidgets.QLabel()
        self.image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Загружаем изображение
        pixmap = QtGui.QPixmap(receipt_path)
        if not pixmap.isNull():
            # Масштабируем изображение, сохраняя пропорции
            scaled_pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)
        else:
            self.image_label.setText("Ошибка загрузки изображения")
        
        layout.addWidget(self.image_label)
        
        # Добавляем кнопку закрытия
        close_button = QtWidgets.QPushButton("Закрыть")
        close_button.clicked.connect(self.accept)
        layout.addWidget(close_button)

    def resizeEvent(self, event):
        """Обработка изменения размера окна"""
        super().resizeEvent(event)
        if self.image_label.pixmap():
            # Перемасштабируем изображение при изменении размера окна
            pixmap = QtGui.QPixmap(self.image_label.pixmap())
            scaled_pixmap = pixmap.scaled(
                self.width(), self.height(),
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            )
            self.image_label.setPixmap(scaled_pixmap)


class AddTransactionDialog(QtWidgets.QDialog):
    """Диалоговое окно добавления транзакции"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_AddTransactionDialog()
        self.ui.setupUi(self)
        
        # Путь к загруженному чеку
        self.receipt_path = None

        # Настройка начальных значений
        self.ui.dateEdit.setDate(QDate.currentDate())
        
        # Настройка поля ввода суммы
        self.ui.amountSpin.setDecimals(2)  # Устанавливаем 2 знака после запятой
        self.ui.amountSpin.setSuffix(" руб.")  # Добавляем суффикс "руб."
        self.ui.amountSpin.setMinimum(0.00)  # Минимальное значение
        self.ui.amountSpin.setMaximum(999999999.99)  # Максимальное значение
        self.ui.amountSpin.setValue(0.00)  # Начальное значение
        
        self.load_categories()

        # Подключение кнопок
        self.ui.buttonBox.accepted.connect(self.validate_input)
        self.ui.buttonBox.rejected.connect(self.reject)
        self.ui.loadReceiptButton.clicked.connect(self.load_receipt)

    def load_categories(self):
        """Загрузка категорий из базы данных"""
        categories = db.get_all_categories()
        self.ui.categoryCombo.clear()
        for cat in categories:
            self.ui.categoryCombo.addItem(cat[1], cat[0])

    def load_receipt(self):
        """Загрузка изображения чека"""
        file_dialog = QtWidgets.QFileDialog(self)
        file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
        file_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.receipt_path = selected_files[0]
                file_name = os.path.basename(self.receipt_path)
                self.ui.receiptLabel.setText(f"Загружен: {file_name}")
                
                # Показываем превью изображения
                pixmap = QtGui.QPixmap(self.receipt_path)
                if not pixmap.isNull():
                    # Масштабируем изображение для превью
                    scaled_pixmap = pixmap.scaled(200, 200, Qt.AspectRatioMode.KeepAspectRatio)
                    self.ui.receiptLabel.setPixmap(scaled_pixmap)
                else:
                    self.ui.receiptLabel.setText("Ошибка загрузки изображения")

    def validate_input(self):
        """Проверка корректности введенных данных"""
        if self.ui.amountSpin.value() <= 0:
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Сумма должна быть больше нуля!")
            return
        if not self.ui.categoryCombo.currentData():
            QtWidgets.QMessageBox.warning(self, "Ошибка", "Выберите категорию!")
            return
        self.accept()

    def get_data(self):
        """Возвращает введенные данные"""
        return {
            'amount': self.ui.amountSpin.value(),
            'category': self.ui.categoryCombo.currentData(),  # This will be the category_id
            'date': self.ui.dateEdit.date().toString("yyyy-MM-dd"),
            'description': self.ui.descriptionEdit.text(),
            'receipt_path': self.receipt_path
        }


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Главное окно приложения"""

    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # Применяем темную тему
        self.setStyleSheet("""
            QMainWindow, QDialog {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QTableWidget {
                background-color: #2b2b2b;
                color: #ffffff;
                gridline-color: #3d3d3d;
                selection-background-color: #3d3d3d;
                selection-color: #ffffff;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QHeaderView::section {
                background-color: #2b2b2b;
                color: #ffffff;
                padding: 5px;
                border: 1px solid #3d3d3d;
            }
            QPushButton {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                padding: 5px 15px;
                border-radius: 3px;
            }
            QPushButton:hover {
                background-color: #4d4d4d;
            }
            QPushButton:pressed {
                background-color: #5d5d5d;
            }
            QSpinBox, QDoubleSpinBox, QComboBox, QLineEdit, QTextEdit {
                background-color: #3d3d3d;
                color: #ffffff;
                border: 1px solid #4d4d4d;
                padding: 3px;
            }
            QMenuBar {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMenuBar::item {
                background-color: transparent;
                padding: 5px 10px;
            }
            QMenuBar::item:selected {
                background-color: #3d3d3d;
            }
            QMenu {
                background-color: #2b2b2b;
                color: #ffffff;
                border: 1px solid #3d3d3d;
            }
            QMenu::item {
                padding: 5px 20px;
            }
            QMenu::item:selected {
                background-color: #3d3d3d;
            }
            QLabel {
                color: #ffffff;
            }
            QMessageBox {
                background-color: #2b2b2b;
                color: #ffffff;
            }
            QMessageBox QPushButton {
                min-width: 80px;
            }
        """)

        # Настройка интерфейса
        self.setWindowTitle("Учет личных финансов")
        self.setMinimumSize(800, 800)

        try:
            # Инициализация базы данных
            db.initialize()

            # Настройка меню Файл
            self.setup_file_menu()

            # Настройка основной таблицы транзакций
            self.setup_transactions_table()
            
            # Создание и настройка таблицы статистики
            self.setup_statistics_table()

            # Подключение обработчиков
            self.addButton.clicked.connect(self.add_transaction)
            self.deleteButton.clicked.connect(self.delete_transaction)
            self.refreshButton.clicked.connect(self.refresh_data)

            # Горячие клавиши
            self.addAction = QtGui.QAction(self)
            self.addAction.setShortcut("Ctrl+N")
            self.addAction.triggered.connect(self.add_transaction)

            # Загрузка данных
            self.load_data()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка инициализации приложения: {str(e)}")

    def setup_file_menu(self):
        """Настройка меню Файл"""
        # Очищаем существующее меню
        self.menuFile.clear()

        # Экспорт в Excel
        export_action = QtGui.QAction("Экспорт в Excel...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self.export_to_excel)
        self.menuFile.addAction(export_action)

        # Создать резервную копию
        backup_action = QtGui.QAction("Создать резервную копию...", self)
        backup_action.setShortcut("Ctrl+B")
        backup_action.triggered.connect(self.create_backup)
        self.menuFile.addAction(backup_action)

        # Восстановить из резервной копии
        restore_action = QtGui.QAction("Восстановить из резервной копии...", self)
        restore_action.setShortcut("Ctrl+R")
        restore_action.triggered.connect(self.restore_from_backup)
        self.menuFile.addAction(restore_action)

        self.menuFile.addSeparator()

        # Выход
        exit_action = QtGui.QAction("Выход", self)
        exit_action.setShortcut("Alt+F4")
        exit_action.triggered.connect(self.close)
        self.menuFile.addAction(exit_action)

    def export_to_excel(self):
        """Экспорт данных в Excel"""
        try:
            # Запрашиваем путь для сохранения файла
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Сохранить как",
                "",
                "Excel Files (*.xlsx);;All Files (*)"
            )
            
            if not file_path:
                return

            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            # Получаем данные
            transactions = db.get_all_transactions()
            
            # Создаем DataFrame
            data = []
            for trans_id, amount, category_id, date, description, receipt_path in transactions:
                category_name = db.get_category_name(category_id)
                data.append({
                    'Дата': date,
                    'Категория': category_name,
                    'Сумма': amount,
                    'Описание': description,
                    'Чек': 'Да' if receipt_path else 'Нет'
                })

            # Импортируем pandas только когда нужно
            import pandas as pd
            
            # Создаем Excel файл
            df = pd.DataFrame(data)
            df.to_excel(file_path, index=False, sheet_name='Транзакции')
            
            QtWidgets.QMessageBox.information(
                self,
                "Экспорт завершен",
                f"Данные успешно экспортированы в файл:\n{file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось экспортировать данные: {str(e)}"
            )

    def create_backup(self):
        """Создание резервной копии базы данных"""
        try:
            # Запрашиваем путь для сохранения
            file_path, _ = QtWidgets.QFileDialog.getSaveFileName(
                self,
                "Сохранить резервную копию",
                "",
                "SQLite Database (*.db);;All Files (*)"
            )
            
            if not file_path:
                return

            if not file_path.endswith('.db'):
                file_path += '.db'

            # Создаем резервную копию
            import shutil
            shutil.copy2('finance.db', file_path)
            
            QtWidgets.QMessageBox.information(
                self,
                "Резервное копирование",
                f"Резервная копия успешно создана:\n{file_path}"
            )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось создать резервную копию: {str(e)}"
            )

    def restore_from_backup(self):
        """Восстановление данных из резервной копии"""
        try:
            # Предупреждение перед восстановлением
            reply = QtWidgets.QMessageBox.warning(
                self,
                "Восстановление из резервной копии",
                "Восстановление из резервной копии заменит все текущие данные!\n\n"
                "Рекомендуется создать резервную копию текущих данных перед восстановлением.\n\n"
                "Продолжить?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return

            # Запрашиваем файл резервной копии
            file_path, _ = QtWidgets.QFileDialog.getOpenFileName(
                self,
                "Выбрать файл резервной копии",
                "",
                "SQLite Database (*.db);;All Files (*)"
            )
            
            if not file_path:
                return

            # Проверяем, что выбранный файл существует
            if not os.path.exists(file_path):
                raise FileNotFoundError("Файл резервной копии не найден")

            # Закрываем текущее соединение с базой данных
            db.close_connection()

            # Создаем временную копию текущей базы данных
            import shutil
            temp_backup = "finance_temp_backup.db"
            if os.path.exists("finance.db"):
                shutil.copy2("finance.db", temp_backup)

            try:
                # Копируем файл резервной копии
                shutil.copy2(file_path, "finance.db")
                
                # Переинициализируем соединение с базой данных
                db.initialize()
                
                # Перезагружаем данные
                self.load_data()
                
                # Удаляем временную копию
                if os.path.exists(temp_backup):
                    os.remove(temp_backup)
                
                QtWidgets.QMessageBox.information(
                    self,
                    "Восстановление завершено",
                    "Данные успешно восстановлены из резервной копии"
                )
            except Exception as e:
                # В случае ошибки восстанавливаем из временной копии
                if os.path.exists(temp_backup):
                    shutil.copy2(temp_backup, "finance.db")
                    os.remove(temp_backup)
                    db.initialize()
                    self.load_data()
                raise Exception(f"Ошибка при восстановлении: {str(e)}")
                
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось восстановить данные: {str(e)}"
            )

    def setup_transactions_table(self):
        """Настройка основной таблицы транзакций"""
        self.tableWidget.setColumnCount(5)
        self.tableWidget.setHorizontalHeaderLabels(["Дата", "Категория", "Сумма", "Описание", "Чек"])
        
        # Устанавливаем размеры столбцов
        self.tableWidget.setColumnWidth(0, 100)  # Дата
        self.tableWidget.setColumnWidth(1, 150)  # Категория
        self.tableWidget.setColumnWidth(2, 120)  # Сумма
        self.tableWidget.setColumnWidth(4, 150)  # Чек
        self.tableWidget.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeMode.Stretch)  # Описание

        # Настраиваем выравнивание заголовков
        header = self.tableWidget.horizontalHeader()
        for i in range(5):
            header_item = self.tableWidget.horizontalHeaderItem(i)
            if header_item:
                header_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Настройка таблицы для поддержки переноса текста
        self.tableWidget.setWordWrap(True)
        self.tableWidget.verticalHeader().setSectionResizeMode(QtWidgets.QHeaderView.ResizeMode.ResizeToContents)
        
        # Настройка автоматического изменения размера ячеек
        self.tableWidget.resizeRowsToContents()
        self.tableWidget.cellChanged.connect(self.on_cell_changed)
        
        # Подключаем обработчик клика по ячейке
        self.tableWidget.cellClicked.connect(self.handle_cell_click)

        # Включаем множественное выделение
        self.tableWidget.setSelectionMode(QtWidgets.QAbstractItemView.SelectionMode.ExtendedSelection)
        self.tableWidget.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectionBehavior.SelectRows)

    def setup_statistics_table(self):
        """Создание и настройка таблицы статистики"""
        # Создаем виджет для таблицы статистики
        self.statsTable = QtWidgets.QTableWidget(self)
        self.statsTable.setMinimumHeight(200)  # Минимальная высота таблицы
        
        # Добавляем таблицу в вертикальный layout после основной таблицы
        self.verticalLayout.addWidget(self.statsTable)
        
        # Настраиваем заголовок
        self.statsTable.setColumnCount(13)  # 12 месяцев + столбец года
        headers = ["Год"] + [f"{i:02d}" for i in range(1, 13)]  # Год и месяцы 01-12
        self.statsTable.setHorizontalHeaderLabels(headers)
        
        # Настройка внешнего вида
        self.statsTable.horizontalHeader().setDefaultAlignment(Qt.AlignmentFlag.AlignCenter)
        self.statsTable.verticalHeader().setVisible(False)
        
        # Устанавливаем размеры столбцов
        self.statsTable.setColumnWidth(0, 80)  # Год
        for i in range(1, 13):
            self.statsTable.setColumnWidth(i, 90)  # Месяцы

    def update_statistics(self):
        """Обновление таблицы статистики"""
        try:
            # Получаем статистику по годам и месяцам
            stats = db.get_monthly_statistics()
            
            # Очищаем таблицу
            self.statsTable.setRowCount(0)
            
            # Заполняем таблицу данными
            current_row = -1
            current_year = None
            
            for year, month, total in stats:
                if year != current_year:
                    current_year = year
                    current_row += 1
                    self.statsTable.insertRow(current_row)
                    
                    # Добавляем год
                    year_item = QtWidgets.QTableWidgetItem(str(year))
                    year_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    year_item.setFlags(year_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.statsTable.setItem(current_row, 0, year_item)
                    
                    # Инициализируем ячейки месяцев
                    for i in range(1, 13):
                        month_item = QtWidgets.QTableWidgetItem("0.00 руб.")
                        month_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                        month_item.setFlags(month_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                        self.statsTable.setItem(current_row, i, month_item)
                
                # Обновляем сумму для месяца
                if total is not None:
                    amount_str = f"{total:.2f} руб."
                    month_item = QtWidgets.QTableWidgetItem(amount_str)
                    month_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    month_item.setFlags(month_item.flags() & ~Qt.ItemFlag.ItemIsEditable)
                    self.statsTable.setItem(current_row, month, month_item)
            
            # Добавляем подсветку при наведении
            self.statsTable.setStyleSheet("""
                QTableWidget::item:hover {
                    background-color: #e6f3ff;
                }
            """)
            
        except Exception as e:
            print(f"Ошибка при обновлении статистики: {str(e)}")

    def format_amount(self, amount) -> str:
        """Форматирование суммы в нужный формат"""
        try:
            if amount is None:
                return "0.00 руб."
            amount_float = float(amount)
            # Форматируем число с двумя знаками после запятой
            formatted = f"{amount_float:,.2f}".replace(',', ' ')
            return f"{formatted} руб."
        except (ValueError, TypeError):
            return "0.00 руб."

    def on_cell_changed(self, row, column):
        """Обработчик изменения содержимого ячейки"""
        try:
            if column == 3:  # Колонка описания
                self.tableWidget.resizeRowToContents(row)
                # Если описание изменилось, сохраняем его в базе данных
                new_description = self.tableWidget.item(row, column).text()
                transaction_id = self.tableWidget.item(row, 0).data(Qt.ItemDataRole.UserRole)
                if transaction_id:
                    db.update_transaction_description(transaction_id, new_description)
        except Exception as e:
            print(f"Ошибка при обновлении высоты строки: {str(e)}")

    def load_data(self):
        """Загрузка данных в таблицу"""
        try:
            self.tableWidget.setRowCount(0)
            transactions = db.get_all_transactions()

            for row, transaction in enumerate(transactions):
                try:
                    self.tableWidget.insertRow(row)
                    
                    # Проверяем, что у нас достаточно данных
                    if len(transaction) < 6:
                        continue
                    
                    # Распаковываем данные транзакции
                    trans_id, amount, category_id, date, description, receipt_path = transaction
                    
                    # Дата
                    date_item = QtWidgets.QTableWidgetItem(str(date))
                    date_item.setData(Qt.ItemDataRole.UserRole, trans_id)
                    date_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row, 0, date_item)
                    
                    # Категория
                    category_name = db.get_category_name(category_id)
                    category_item = QtWidgets.QTableWidgetItem(category_name)
                    category_item.setData(Qt.ItemDataRole.UserRole, category_id)
                    category_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row, 1, category_item)
                    
                    # Сумма
                    amount_str = self.format_amount(amount)
                    amount_item = QtWidgets.QTableWidgetItem(amount_str)
                    amount_item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                    self.tableWidget.setItem(row, 2, amount_item)
                    
                    # Описание
                    desc_item = QtWidgets.QTableWidgetItem(str(description) if description else "")
                    desc_item.setTextAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
                    desc_item.setFlags(desc_item.flags() | Qt.ItemFlag.ItemIsEditable)
                    self.tableWidget.setItem(row, 3, desc_item)
                    
                    # Чек
                    if receipt_path and isinstance(receipt_path, str) and os.path.exists(receipt_path):
                        receipt_item = QtWidgets.QTableWidgetItem("Просмотреть чек")
                        receipt_item.setData(Qt.ItemDataRole.UserRole, receipt_path)
                        receipt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                        receipt_item.setForeground(QtGui.QBrush(QtGui.QColor("blue")))
                        font = receipt_item.font()
                        font.setUnderline(True)
                        receipt_item.setFont(font)
                    else:
                        receipt_item = QtWidgets.QTableWidgetItem("Нет")
                        receipt_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tableWidget.setItem(row, 4, receipt_item)

                    # Устанавливаем высоту строки в зависимости от содержимого
                    self.tableWidget.resizeRowToContents(row)

                except Exception as e:
                    print(f"Ошибка при добавлении строки {row}: {str(e)}")
                    continue

            # Финальная подгонка размеров
            self.tableWidget.resizeRowsToContents()
            
            # Обновляем статистику
            self.update_statistics()
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки данных: {str(e)}")

    def handle_cell_click(self, row, column):
        """Обработка клика по ячейке таблицы"""
        try:
            if column == 0:  # Дата
                self.edit_date(row)
            elif column == 1:  # Категория
                self.edit_category(row)
            elif column == 2:  # Сумма
                self.edit_amount(row)
            elif column == 4:  # Чек
                item = self.tableWidget.item(row, column)
                if item:
                    receipt_path = item.data(Qt.ItemDataRole.UserRole)
                    if receipt_path and isinstance(receipt_path, str) and os.path.exists(receipt_path):
                        # Если чек существует, открываем его для просмотра
                        viewer = ReceiptViewerDialog(receipt_path, self)
                        viewer.exec()
                    else:
                        # Если чека нет, открываем диалог для его добавления
                        self.add_receipt(row)
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при обработке клика: {str(e)}")

    def edit_date(self, row):
        """Редактирование даты транзакции"""
        try:
            item = self.tableWidget.item(row, 0)
            if not item:
                return
                
            current_date = item.text()
            transaction_id = item.data(Qt.ItemDataRole.UserRole)
            if not transaction_id:
                return
            
            date_dialog = QtWidgets.QDialog(self)
            date_dialog.setWindowTitle("Изменить дату")
            layout = QtWidgets.QVBoxLayout(date_dialog)
            
            date_edit = QtWidgets.QDateEdit(date_dialog)
            date_edit.setCalendarPopup(True)
            try:
                date_edit.setDate(QtCore.QDate.fromString(current_date, "yyyy-MM-dd"))
            except:
                date_edit.setDate(QtCore.QDate.currentDate())
            layout.addWidget(date_edit)
            
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok |
                QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(date_dialog.accept)
            buttons.rejected.connect(date_dialog.reject)
            layout.addWidget(buttons)
            
            if date_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                new_date = date_edit.date().toString("yyyy-MM-dd")
                try:
                    db.update_transaction_date(transaction_id, new_date)
                    self.load_data()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось обновить дату: {str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании даты: {str(e)}")

    def edit_category(self, row):
        """Редактирование категории транзакции"""
        try:
            date_item = self.tableWidget.item(row, 0)
            category_item = self.tableWidget.item(row, 1)
            if not date_item or not category_item:
                return
                
            transaction_id = date_item.data(Qt.ItemDataRole.UserRole)
            current_category_id = category_item.data(Qt.ItemDataRole.UserRole)
            if not transaction_id:
                return
            
            category_dialog = QtWidgets.QDialog(self)
            category_dialog.setWindowTitle("Изменить категорию")
            layout = QtWidgets.QVBoxLayout(category_dialog)
            
            category_combo = QtWidgets.QComboBox(category_dialog)
            categories = db.get_all_categories()
            for cat in categories:
                category_combo.addItem(cat[1], cat[0])
                if cat[0] == current_category_id:
                    category_combo.setCurrentIndex(category_combo.count() - 1)
            layout.addWidget(category_combo)
            
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok |
                QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(category_dialog.accept)
            buttons.rejected.connect(category_dialog.reject)
            layout.addWidget(buttons)
            
            if category_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                new_category_id = category_combo.currentData()
                try:
                    db.update_transaction_category(transaction_id, new_category_id)
                    self.load_data()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось обновить категорию: {str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании категории: {str(e)}")

    def edit_amount(self, row):
        """Редактирование суммы транзакции"""
        try:
            date_item = self.tableWidget.item(row, 0)
            amount_item = self.tableWidget.item(row, 2)
            
            if not date_item or not amount_item:
                return
                
            transaction_id = date_item.data(Qt.ItemDataRole.UserRole)
            if not transaction_id:
                return

            # Получаем текущую сумму
            current_amount_str = amount_item.text().replace(" руб.", "").strip()
            try:
                current_amount = float(current_amount_str)
            except ValueError:
                current_amount = 0.0

            # Создаем диалог для редактирования суммы
            amount_dialog = QtWidgets.QDialog(self)
            amount_dialog.setWindowTitle("Изменить сумму")
            amount_dialog.setMinimumWidth(200)
            layout = QtWidgets.QVBoxLayout(amount_dialog)

            # Создаем спиннер для суммы
            amount_spin = QtWidgets.QDoubleSpinBox(amount_dialog)
            amount_spin.setDecimals(2)
            amount_spin.setSuffix(" руб.")
            amount_spin.setMinimum(0.00)
            amount_spin.setMaximum(999999999.99)
            amount_spin.setValue(current_amount)
            layout.addWidget(amount_spin)

            # Добавляем кнопки OK и Cancel
            buttons = QtWidgets.QDialogButtonBox(
                QtWidgets.QDialogButtonBox.StandardButton.Ok |
                QtWidgets.QDialogButtonBox.StandardButton.Cancel
            )
            buttons.accepted.connect(amount_dialog.accept)
            buttons.rejected.connect(amount_dialog.reject)
            layout.addWidget(buttons)

            if amount_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
                new_amount = amount_spin.value()
                try:
                    # Обновляем сумму в базе данных
                    self.update_transaction_amount(transaction_id, new_amount)
                    self.load_data()
                except Exception as e:
                    QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось обновить сумму: {str(e)}")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при редактировании суммы: {str(e)}")

    def update_transaction_amount(self, transaction_id: int, new_amount: float):
        """Обновление суммы транзакции в базе данных"""
        try:
            db.update_transaction_amount(transaction_id, new_amount)
        except Exception as e:
            raise Exception(f"Ошибка обновления суммы: {str(e)}")

    def add_transaction(self):
        """Добавление новой транзакции"""
        dialog = AddTransactionDialog(self)
        if dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            data = dialog.get_data()
            try:
                db.add_transaction(
                    amount=data['amount'],
                    category_id=data['category'],
                    date=data['date'],
                    description=data['description'],
                    receipt_path=data['receipt_path']
                )
                self.load_data()
            except Exception as e:
                QtWidgets.QMessageBox.critical(self, "Ошибка", f"Не удалось добавить транзакцию: {str(e)}")

    def delete_transaction(self):
        """Удаление выбранных транзакций"""
        selected_rows = self.tableWidget.selectionModel().selectedRows()
        if not selected_rows:
            return

        # Если выбрано несколько строк, запрашиваем подтверждение
        if len(selected_rows) > 1:
            reply = QtWidgets.QMessageBox.question(
                self,
                "Подтверждение удаления",
                f"Вы действительно хотите удалить {len(selected_rows)} выбранных транзакций?",
                QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
                QtWidgets.QMessageBox.StandardButton.No
            )
            if reply == QtWidgets.QMessageBox.StandardButton.No:
                return

        try:
            # Собираем ID всех выбранных транзакций
            transaction_ids = []
            for row_index in sorted([index.row() for index in selected_rows], reverse=True):
                transaction_id = self.tableWidget.item(row_index, 0).data(Qt.ItemDataRole.UserRole)
                if transaction_id:
                    transaction_ids.append(transaction_id)

            # Удаляем транзакции из базы данных
            for trans_id in transaction_ids:
                db.delete_transaction(trans_id)

            # Обновляем отображение
            self.load_data()

            # Показываем сообщение об успешном удалении
            if len(transaction_ids) > 1:
                QtWidgets.QMessageBox.information(
                    self,
                    "Удаление транзакций",
                    f"Успешно удалено {len(transaction_ids)} транзакций"
                )
        except Exception as e:
            QtWidgets.QMessageBox.critical(
                self,
                "Ошибка",
                f"Не удалось удалить транзакции: {str(e)}"
            )

    def refresh_data(self):
        """Обновление данных в таблице"""
        try:
            # Сохраняем текущую выбранную строку
            current_row = self.tableWidget.currentRow()
            
            # Перезагружаем данные
            self.load_data()
            
            # Восстанавливаем выбранную строку, если она существует
            if current_row >= 0 and current_row < self.tableWidget.rowCount():
                self.tableWidget.selectRow(current_row)
                
            # Показываем уведомление об успешном обновлении
            QtWidgets.QMessageBox.information(self, "Обновление", "Данные успешно обновлены")
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при обновлении данных: {str(e)}")

    def closeEvent(self, event):
        """Обработка закрытия окна"""
        db.close_connection()
        event.accept()

    def add_receipt(self, row):
        """Добавление чека к транзакции"""
        try:
            # Получаем ID транзакции
            transaction_id = self.tableWidget.item(row, 0).data(Qt.ItemDataRole.UserRole)
            if not transaction_id:
                return

            # Открываем диалог выбора файла
            file_dialog = QtWidgets.QFileDialog(self)
            file_dialog.setNameFilter("Images (*.png *.jpg *.jpeg *.bmp)")
            file_dialog.setViewMode(QtWidgets.QFileDialog.ViewMode.Detail)
            
            if file_dialog.exec():
                selected_files = file_dialog.selectedFiles()
                if selected_files:
                    receipt_path = selected_files[0]
                    
                    # Обновляем путь к чеку в базе данных
                    try:
                        db.update_transaction_receipt(transaction_id, receipt_path)
                        self.load_data()
                        QtWidgets.QMessageBox.information(
                            self,
                            "Чек добавлен",
                            "Чек успешно добавлен к транзакции"
                        )
                    except Exception as e:
                        QtWidgets.QMessageBox.critical(
                            self,
                            "Ошибка",
                            f"Не удалось добавить чек: {str(e)}"
                        )
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Ошибка", f"Ошибка при добавлении чека: {str(e)}")


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())