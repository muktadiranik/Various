import threading
import time
import random


def execute_thread(i):
    print(f"Thread {i} start sleeping at {time.strftime('%H:%M:%S', time.gmtime())}")
    sleep_time = 0.5
    time.sleep(sleep_time)
    print(f"Thread {i} finish sleeping at {time.strftime('%H:%M:%S', time.gmtime())}")


for i in range(10):
    thread = threading.Thread(target=execute_thread, args=(i,))
    thread.start()
    print(f"Active threads: {threading.active_count()}")
    print(f"Thread objects: {threading.enumerate()}")


def get_time(name):
    print(f"Thread {name} start sleeping at {time.strftime('%H:%M:%S', time.gmtime())}")
    sleep_time = 0.5
    time.sleep(sleep_time)
    print(
        f"Thread {name} finish sleeping at {time.strftime('%H:%M:%S', time.gmtime())}"
    )


class CustomThread(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.name = name

    def run(self):
        get_time(self.name)
        print(f"Thread {self.name} execution ends")


thread_1 = CustomThread("1")
thread_2 = CustomThread("2")
thread_1.start()
thread_2.start()

print(f"Thread 1 alive: {thread_1.is_alive()}")
print(f"Thread 2 alive: {thread_2.is_alive()}")

thread_1.join()
thread_2.join()

print("Execution ends")


class BankAccount(threading.Thread):
    account_balance = 100

    def __init__(self, name, money_request):
        threading.Thread.__init__(self)
        self.name = name
        self.money_request = money_request

    @staticmethod
    def get_money(customer):
        print(
            f"{customer.name} tries to withdrawal ${customer.money_request} at {time.strftime('%H:%M:%S', time.gmtime())}"
        )

        if BankAccount.account_balance - customer.money_request > 0:
            BankAccount.account_balance -= customer.money_request
            print("New account balance is : ${}")
        else:
            print("Not enough money in the account")
            print(f"Current balance : ${BankAccount.account_balance}")

    def run(self):
        with threading.Lock():
            BankAccount.get_money(self)


a = BankAccount("a", 100)
b = BankAccount("b", 100)

a.start()
b.start()

a.join()
b.join()

print("Execution ends")
