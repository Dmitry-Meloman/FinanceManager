from PyQt6 import QtCore, QtGui, QtWidgets

class Ui_AddTransactionDialog(object):
    def setupUi(self, AddTransactionDialog):
        AddTransactionDialog.setObjectName("AddTransactionDialog")
        AddTransactionDialog.resize(400, 300)  # Увеличиваем высоту окна
        
        self.verticalLayout = QtWidgets.QVBoxLayout(AddTransactionDialog)
        self.verticalLayout.setObjectName("verticalLayout")
        
        # Amount layout
        amountLayout = QtWidgets.QHBoxLayout()
        amountLayout.setObjectName("amountLayout")
        
        self.labelSum = QtWidgets.QLabel(AddTransactionDialog)
        self.labelSum.setObjectName("labelSum")
        amountLayout.addWidget(self.labelSum)
        
        self.amountSpin = QtWidgets.QDoubleSpinBox(AddTransactionDialog)
        self.amountSpin.setObjectName("amountSpin")
        self.amountSpin.setMinimum(0.01)
        self.amountSpin.setMaximum(1000000.00)
        self.amountSpin.setPrefix("₽ ")
        amountLayout.addWidget(self.amountSpin)
        
        self.verticalLayout.addLayout(amountLayout)
        
        # Category layout
        categoryLayout = QtWidgets.QHBoxLayout()
        categoryLayout.setObjectName("categoryLayout")
        
        self.labelCategory = QtWidgets.QLabel(AddTransactionDialog)
        self.labelCategory.setObjectName("labelCategory")
        categoryLayout.addWidget(self.labelCategory)
        
        self.categoryCombo = QtWidgets.QComboBox(AddTransactionDialog)
        self.categoryCombo.setObjectName("categoryCombo")
        categoryLayout.addWidget(self.categoryCombo)
        
        self.verticalLayout.addLayout(categoryLayout)
        
        # Date layout
        dateLayout = QtWidgets.QHBoxLayout()
        dateLayout.setObjectName("dateLayout")
        
        self.labelDate = QtWidgets.QLabel(AddTransactionDialog)
        self.labelDate.setObjectName("labelDate")
        dateLayout.addWidget(self.labelDate)
        
        self.dateEdit = QtWidgets.QDateEdit(AddTransactionDialog)
        self.dateEdit.setObjectName("dateEdit")
        self.dateEdit.setCalendarPopup(True)
        dateLayout.addWidget(self.dateEdit)
        
        self.verticalLayout.addLayout(dateLayout)
        
        # Description layout
        descLayout = QtWidgets.QHBoxLayout()
        descLayout.setObjectName("descLayout")
        
        self.labelDesc = QtWidgets.QLabel(AddTransactionDialog)
        self.labelDesc.setObjectName("labelDesc")
        descLayout.addWidget(self.labelDesc)
        
        self.descriptionEdit = QtWidgets.QLineEdit(AddTransactionDialog)
        self.descriptionEdit.setObjectName("descriptionEdit")
        descLayout.addWidget(self.descriptionEdit)
        
        self.verticalLayout.addLayout(descLayout)
        
        # Receipt layout
        receiptLayout = QtWidgets.QHBoxLayout()
        receiptLayout.setObjectName("receiptLayout")
        
        self.loadReceiptButton = QtWidgets.QPushButton(AddTransactionDialog)
        self.loadReceiptButton.setObjectName("loadReceiptButton")
        receiptLayout.addWidget(self.loadReceiptButton)
        
        self.receiptLabel = QtWidgets.QLabel(AddTransactionDialog)
        self.receiptLabel.setObjectName("receiptLabel")
        self.receiptLabel.setText("Чек не загружен")
        receiptLayout.addWidget(self.receiptLabel)
        
        self.verticalLayout.addLayout(receiptLayout)
        
        # Button box
        self.buttonBox = QtWidgets.QDialogButtonBox(AddTransactionDialog)
        self.buttonBox.setOrientation(QtCore.Qt.Orientation.Horizontal)
        self.buttonBox.setStandardButtons(
            QtWidgets.QDialogButtonBox.StandardButton.Cancel |
            QtWidgets.QDialogButtonBox.StandardButton.Ok
        )
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)
        
        self.retranslateUi(AddTransactionDialog)
        self.buttonBox.accepted.connect(AddTransactionDialog.accept)
        self.buttonBox.rejected.connect(AddTransactionDialog.reject)
        QtCore.QMetaObject.connectSlotsByName(AddTransactionDialog)
    
    def retranslateUi(self, AddTransactionDialog):
        _translate = QtCore.QCoreApplication.translate
        AddTransactionDialog.setWindowTitle(_translate("AddTransactionDialog", "Добавить транзакцию"))
        self.labelSum.setText(_translate("AddTransactionDialog", "Сумма:"))
        self.labelCategory.setText(_translate("AddTransactionDialog", "Категория:"))
        self.labelDate.setText(_translate("AddTransactionDialog", "Дата:"))
        self.labelDesc.setText(_translate("AddTransactionDialog", "Описание:"))
        self.loadReceiptButton.setText(_translate("AddTransactionDialog", "Загрузить чек")) 