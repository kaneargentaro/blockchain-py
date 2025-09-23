from blockchain import Blockchain

from utils.verification import Verification
from wallet import Wallet

class Node:
    def __init__(self):
        self.wallet = Wallet()
        self.blockchain = None

    def get_user_action(self):
        """ Returns the user input for transactions in a float"""
        print("\nWhat would you like to do?")
        print("\t1: Add a new transaction value")
        print("\t2: Mine blockchain")
        print("\t3: Print blockchain")
        print("\t4: Check transaction validity")
        print("\t5: Create wallet")
        print("\t6: Load wallet")
        print("\t6: Save wallet")
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
                if self.blockchain.add_transaction(recipient=recipient, sender=self.wallet.public_key, amount=amount):
                    print('Transaction added.')
                else:
                    print('Transaction failed.')
            elif action == '2':
                if not self.blockchain.mine_block():
                    print("Mining failed. Are you missing a wallet?")
            elif action == '3':
                self.print_blockchain()
            elif action == '4':
                if Verification.verify_transactions(self.blockchain.open_transactions(), self.blockchain.get_balance):
                    print('Transactions verified.')
                else:
                    print('Transactions failed.')
            elif action == '5':
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif action == '6':
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif action == '7':
                self.wallet.save_keys()
            elif action == 'q':
                should_continue = False
            else:
                print("Invalid input, try again")

            if not Verification.verify_chain(blockchain=self.blockchain.chain):
                print("Invalid chain, try again")
                break

            print(f'Balance of {self.wallet.public_key}: {self.blockchain.get_balance():6.2f}')

        print('Finished')

if __name__ == '__main__':
    node = Node()
    node.listen_for_input()