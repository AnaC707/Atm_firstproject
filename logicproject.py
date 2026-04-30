from PyQt6.QtWidgets import *
from guiproject import *
import csv
import os

class Accounts:
    def __init__(self, name, pin, balance, acc_type):
        self.__name = name
        self.__pin = pin
        self.__balance = balance
        self.__type = acc_type

    def check_pin(self, pin):
        return self.__pin == pin

    def get_pin(self):
        return self.__pin

    def get_name(self):
        return self.__name

    def get_balance(self):
        return self.__balance

    def get_type(self):
        return self.__type

    def deposit(self, amount):
        self.__balance += amount

    def withdraw(self, amount):
        if amount > self.__balance:
            return False
        self.__balance -= amount
        return True

class ManageAccount:
    def __init__(self):
        self.accounts = {}
        self.load_accounts()

    def account_exists(self, name):
        return name in self.accounts

    def authenticate(self, name, pin):
        return self.accounts[name].check_pin(pin)

    def get_account(self, name):
        return self.accounts[name]

    def load_accounts(self):
        if not os.path.isfile("accounts.csv"):
            return

        with open("accounts.csv", "r") as file:
            reader = csv.DictReader(file)
            for row in reader:
                name = row["Name"]
                pin = row["Pin"]
                balance = float(row["Balance"].replace("$", ""))
                acc_type = row["Type"]

                self.accounts[name] = Accounts(name, pin, balance, acc_type)

    def save_accounts(self):
        with open("accounts.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Pin", "Balance", "Type"])

            for acc in self.accounts.values():
                writer.writerow([acc.get_name(), acc.get_pin(), f"${acc.get_balance():.2f}", acc.get_type()])

    def save_record(self, name, acc_type, transaction, amount, balance):
        with open("record.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, acc_type, transaction, amount, balance])

class Logic(QMainWindow, Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.system = ManageAccount()
        self.current_user = None
        self.connections()

    def connections(self):
        self.push_b1.clicked.connect(self.enter_transaction)
        self.push_b2.clicked.connect(self.change_account)
        self.push_b3.clicked.connect(self.login)

    def enter_transaction(self):
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Login first")
            return

        acc = self.system.get_account(self.current_user)
        try:
            amount = float(self.input_amount.text())
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Please enter a valid number")
            return

        if self.r_button2.isChecked():
            acc.deposit(amount)
            self.label_balance.setText(f"Deposited: ${amount:.2f}\nBalance: ${acc.get_balance():.2f}")
            self.system.save_record(acc.get_name(), acc.get_type(), "Deposit", amount, acc.get_balance())

        elif self.r_button1.isChecked():
            if not acc.withdraw(amount):
                QMessageBox.warning(self, "Error", "Insufficient Funds")
                return

            self.label_balance.setText(f"Withdrawal: ${amount:.2f}\nBalance: ${acc.get_balance():.2f}")
            self.system.save_record(acc.get_name(),acc.get_type(), "Withdraw", amount, acc.get_balance())

        else:
            QMessageBox.warning(self, "Error", "Select an option")
            return

        self.system.save_accounts()
        self.input_amount.clear()
        self.buttonGroup.setExclusive(False)
        self.r_button1.setChecked(False)
        self.r_button2.setChecked(False)
        self.buttonGroup.setExclusive(True)
        QMessageBox.information(self, "Success", "Transaction completed")

    def change_account(self):
        if self.acc_type.text() == "Checking Account":
            self.acc_type.setText("Saving Account")
        else:
            self.acc_type.setText("Checking Account")

        self.input_name.clear()
        self.input_pin.clear()
        self.input_amount.clear()
        self.label_balance.clear()
        self.current_user = None
        self.input_name.setFocus()
        self.buttonGroup.setExclusive(False)
        self.r_button1.setChecked(False)
        self.r_button2.setChecked(False)
        self.buttonGroup.setExclusive(True)

    def login(self):
        name = self.input_name.text().strip()
        pin = self.input_pin.text().strip()
        if not name or not pin:
            QMessageBox.warning(self, "Error", "Enter both Name and PIN")
            return

        if not self.system.account_exists(name):
            QMessageBox.warning(self, "Error", "Account not Found")
            return

        if not self.system.authenticate(name, pin):
            QMessageBox.warning(self, "Error", "Incorrect PIN")
            return

        self.current_user = name
        acc = self.system.get_account(name)
        if acc.get_type() == "Checking":
            self.acc_type.setText("Checking Account")
        else:
            self.acc_type.setText("Saving Account")

        self.welcome_mssg.setText(f"Welcome {name}!")
        self.show_balance()

    def show_balance(self):
        acc = self.system.get_account(self.current_user)
        self.label_balance.setText(f"Balance: ${acc.get_balance():.2f}")
