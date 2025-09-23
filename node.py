from blockchain import Blockchain

from utils.verification import Verification


class Node:
    def __init__(self):
        self.id = 'John' #str(uuid4())
        self.blockchain = Blockchain(self.id)

    def get_user_action(self):
        """ Returns the user input for transactions in a float"""
        print("\nWhat would you like to do?")
        print("\t1: Add a new transaction value")
        print("\t2: Mine blockchain")
        print("\t3: Print blockchain")
        print("\t4: Check transaction validity")
        print("\tq: Exit")
        return input("User input: ")

    def print_blockchain(self):
        """ Prints the blockchain """
        for block in self.blockchain.chain:
            print(block)

    def get_transaction_value(self):
        """ Returns the user input for transactions in a float"""
        tx_recipient = input("Enter recipient: ")
        tx_amount = float(input("Enter amount: "))
        return tx_recipient, tx_amount

    def listen_for_input(self):
        should_continue = True
        while should_continue:
            action = self.get_user_action()
            if action == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                if self.blockchain.add_transaction(recipient=recipient, sender=self.id, amount=amount):
                    print('Transaction added.')
                else:
                    print('Transaction failed.')
            elif action == '2':
                self.blockchain.mine_block()
            elif action == '3':
                self.print_blockchain()
            elif action == '4':
                if Verification.verify_transactions(self.blockchain.open_transactions(), self.blockchain.get_balance):
                    print('Transactions verified.')
                else:
                    print('Transactions failed.')
            elif action == 'q':
                should_continue = False
            else:
                print("Invalid input, try again")

            if not Verification.verify_chain(blockchain=self.blockchain.chain):
                print("Invalid chain, try again")
                break

            print(f'Balance of {self.id}: {self.blockchain.get_balance():6.2f}')

        print('Finished')

if __name__ == '__main__':
    node = Node()
    node.listen_for_input()