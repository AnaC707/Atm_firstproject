from PyQt6.QtWidgets import *
from guiproject import *
import csv
import os

class Accounts:
    """
    A class that sets the information of one account at a time.
    """
    def __init__(self, name: str, pin: str, balance: float, acc_type: str)->None:
        """
        This method stores what the account needs to log in.
        :param name: name of the account's owner
        :param pin: pin to log in
        :param balance: starting balance of the account
        :param acc_type: type of the account
        """
        self.__name = name
        self.__pin = pin
        self.__balance = balance
        self.__type = acc_type

    def check_pin(self, pin: str)->bool:
        """
        A method that checks if the pin matches the stored one.
        :param pin: pin entered by the user
        :return: True if valid, False if not
        """
        return self.__pin == pin

    def get_pin(self)-> str:
        """
        The method returns the pin of the account.
        :return: pin as a string
        """
        return self.__pin

    def get_name(self)->str:
        """
        The method returns the name of the owner's account.
        :return: owner's account name
        """
        return self.__name

    def get_balance(self)->float:
        """
        The method returns the balance of the account.
        :return: account's current balance
        """
        return self.__balance

    def get_type(self)->str:
        """
        The method returns the type of the account.
        :return: checking or saving type
        """
        return self.__type

    def deposit(self, amount: float)->None:
        """
        This method adds money to the account balance.
        :param amount: user's input to deposit
        """
        self.__balance += amount

    def withdraw(self, amount: float)->bool:
        """
        This method withdraws money if there is enough balance.
        :param amount: user's input to withdraw
        :return: True if successful, False if not
        """
        if amount > self.__balance:
            return False
        self.__balance -= amount
        return True

class ManageAccount:
    """
    A class that manages all stored bank accounts.
    """
    def __init__(self)->None:
        """
        A method that manages the accounts, creates an empty dictionary,
        and loads the account's data.
        """
        self.accounts = {}
        self.load_accounts()

    def account_exists(self, name: str)->bool:
        """
        The method checks if an account exists.
        :param name: user's name
        :return: True if account exists, False if not
        """
        return name in self.accounts

    def authenticate(self, name: str, pin: str)->bool:
        """
        The method checks if login inputs are correct.
        :param name: user's name
        :param pin: pin to log in
        :return: True if they are correct, False if not
        """
        return self.accounts[name].check_pin(pin)

    def get_account(self, name: str)->Accounts:
        """
        The method finds the user in the dictionary and returns their account object.
        :param name: user's name
        :return: account object
        """
        return self.accounts[name]

    def load_accounts(self)->None:
        """
        This method loads information from the csv file. It reads each row
        in the file and saves it in a dictionary.
        """
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

    def save_accounts(self)->None:
        """
        This method rewrites the accounts csv file, storing the updated
        information when a transaction is made.
        """
        with open("accounts.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(["Name", "Pin", "Balance", "Type"])

            for acc in self.accounts.values():
                writer.writerow([acc.get_name(), acc.get_pin(), f"${acc.get_balance() :.2f}", acc.get_type()])

    def save_record(self, name: str, acc_type: str, transaction: str, amount: float, balance: float)->None:
        """
        This method adds and saves the transaction history in record.csv
        :param name: user's name
        :param acc_type: account type, checking or saving
        :param transaction: deposit or withdraw
        :param amount: user's transaction input
        :param balance: new balance after transaction
        """
        with open("record.csv", "a", newline="") as file:
            writer = csv.writer(file)
            writer.writerow([name, acc_type, transaction, amount, balance])

class Logic(QMainWindow, Ui_MainWindow):
    """
    A class that manages the user interface for the ATM program
    """
    def __init__(self)->None:
        """
        This method creates the main window, sets the default user
        to None, and calls the connections function.
        """
        super().__init__()
        self.setupUi(self)
        self.system = ManageAccount()
        self.current_user = None
        self.connections()

    def connections(self)->None:
        """
        The method connects the GUI push buttons their respective functions.
        """
        self.push_b1.clicked.connect(self.enter_transaction)
        self.push_b2.clicked.connect(self.change_account)
        self.push_b3.clicked.connect(self.login)

    def enter_transaction(self)->None:
        """
        This method checks if a user is logged in, validates the entered amount,
        processes the selected transaction, updates balance, saves files, and
        resets every input and radio button. With the suggestion of AI, I implemented
        a pop-up message/window when an error occurs or the transaction is successful.
        """
        if not self.current_user:
            QMessageBox.warning(self, "Error", "Log in first")
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
            self.label_balance.setText(f"Deposited: ${amount:.2f}\nBalance: ${acc.get_balance() :.2f}")
            self.system.save_record(acc.get_name(), acc.get_type(), "Deposit", amount, acc.get_balance())

        elif self.r_button1.isChecked():
            if not acc.withdraw(amount):
                QMessageBox.warning(self, "Error", "Insufficient Funds")
                return

            self.label_balance.setText(f"Withdrawal: ${amount:.2f}\nBalance: ${acc.get_balance() :.2f}")
            self.system.save_record(acc.get_name(), acc.get_type(), "Withdraw", amount, acc.get_balance())

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

    def change_account(self)->None:
        """
        This method switches the account label between Checking and Saving.
        It also clears all input, radio buttons, and logs the user out.
        """
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

    def login(self)->None:
        """
        The method checks that the name and pin were entered, verifies if
        the account exists, authenticates the pin, sets and welcomes the
        current user, and displays the account balance.
        """
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

    def show_balance(self)->None:
        """
        This method sets the current balance of the account.
        """
        acc = self.system.get_account(self.current_user)
        self.label_balance.setText(f"Balance: ${acc.get_balance() :.2f}")
