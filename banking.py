import sqlite3
import random

# Create a database and a table in it
with sqlite3.connect('card.s3db') as connection:
    cursor = connection.cursor()

    cursor.execute("""CREATE TABLE IF NOT EXISTS card (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        number TEXT,
        pin TEXT,
        balance INTEGER DEFAULT 0
        );""")


class CreditCard():
    """Simple banking system"""

    flag = True
    current_card = ''
    current_pin = 0
    current_balance = None

    def main_menu(self):
        print('1. Create an account')
        print('2. Log into account')
        print('0. Exit')
        self.action = input()
        return self.action

    # User menu
    def action_menu(self):
        print('1. Balance')
        print('2. Add income')
        print('3. Do transfer')
        print('4. Close account')
        print('5. Log out')
        print('0. Exit')
        self.action = input()
        return self.action

    # Luhn checksum calculation
    def control_sum(self, account):
        if len(account) == 16:
            account.pop()
        control = 0
        for i, digit in enumerate(account):
            if (i + 1) % 2:
                digit *= 2
                if digit > 9:
                    digit -= 9
            control += digit
        return 10 - (control % 10)

    def create_card_number(self):
        account_id = [4, 0, 0, 0, 0, 0] + [int(random.randint(0, 9)) for i in range(9)]
        card_num = "".join(str(j) for j in account_id)
        control = self.control_sum(account_id)
        final_card_num = card_num + str(control)[-1]
        return final_card_num

    def create_pin(self):
        pin = "".join(str(random.randint(0, 9)) for i in range(4))
        return pin

    def create_account(self):
        card_number = self.create_card_number()
        pin = self.create_pin()
        params_to_execute = (card_number, pin, 0)
        cursor.execute('INSERT INTO card (number, pin, balance) VALUES (?, ?, ?);', params_to_execute)
        connection.commit()
        print()
        print('Your card has been created')
        print(f'Your card number:\n{card_number}')
        print(f'Your card PIN:\n{pin}\n')

    def login(self):
        card_number = input('\nEnter your card number:\n')
        pin = input('Enter your PIN:\n')
        cursor.execute(f'SELECT number, pin FROM card WHERE number = {card_number};')
        result = cursor.fetchall()
        if len(result) == 0:
            return False
        if pin == result[0][1]:
            self.current_card = card_number
            self.current_pin = pin
            return True

    def log_out(self):
        self.current_card = ''
        self.current_pin = 0
        return False

    def balance(self):
        cursor.execute(f'SELECT balance FROM card WHERE number = {self.current_card}')
        balance = cursor.fetchone()
        self.current_balance = balance[0]

    def add_income(self):
        if self.current_balance is None:
            self.balance()
        income = int(input('\nEnter income:\n'))
        self.current_balance += income
        cursor.execute(f'UPDATE card SET balance = {self.current_balance} WHERE number = {self.current_card}')
        connection.commit()
        print('Income was added!\n')

    def do_transfer(self):
        print('\nTransfer')
        transfer_card = input('Enter card number:\n')
        if transfer_card == self.current_card:
            print("You can't transfer money to the same account!\n")
        elif int(transfer_card[-1]) != self.control_sum([int(i) for i in transfer_card]):
            print("Probably you made mistake in the card number.\nPlease try again!\n")
        else:
            cursor.execute(f'SELECT number FROM card WHERE number = {transfer_card}')
            sql_answer = cursor.fetchone()
            if sql_answer:
                self.balance()
                money_to_trans = int(input('Enter how much money you want to transfer:\n'))
                if money_to_trans > self.current_balance:
                    print('Not enough money!\n')
                else:
                    cursor.execute(f'UPDATE card SET balance = balance - {money_to_trans} WHERE number = {self.current_card}')
                    connection.commit()
                    cursor.execute(f'UPDATE card SET balance = balance + {money_to_trans} WHERE number = {transfer_card}')
                    connection.commit()
                    print('Success!\n')
            else:
                print('Such a card does not exist.\n')

    def close_acc(self):
        cursor.execute(f'DELETE FROM card WHERE number = {self.current_card}')
        connection.commit()
        print('\nThe account has been closed!\n')


my_cart = CreditCard()

while my_cart.flag:
    action = my_cart.main_menu()
    if action == '1':
        my_cart.create_account()
    elif action == '2':
        status = my_cart.login()
        if status:
            print('\nYou have successfully logged in!\n')
            while status:
                logged_action = my_cart.action_menu()
                if logged_action == '1':
                    my_cart.balance()
                    print(f'\nBalance: {str(my_cart.current_balance)}\n')
                elif logged_action == '2':
                    my_cart.add_income()
                elif logged_action == '3':
                    my_cart.do_transfer()
                elif logged_action == '4':
                    my_cart.close_acc()
                    status = my_cart.log_out()
                elif logged_action == '5':
                    status = my_cart.log_out()
                    print('You have successfully logged out!')
                    break
                elif logged_action == '0':
                    my_cart.flag = False
                    print('\nBye!')
                    break
                else:
                    print('Wrong command')
        else:
            print('Wrong card number or PIN!\n')
            continue
    elif action == '0':
        my_cart.flag = False
        connection.commit()
        print('\nBye!')
        break
    else:
        print('Wrong command')
