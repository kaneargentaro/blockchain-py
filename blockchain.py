from functools import reduce
from hashlib import sha256
import json

MINING_REWARD = 10
genesis_block = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
}
blockchain = [genesis_block]
open_transactions = []
owner = 'John'
participants = set(owner)


def hash_block(block):
    return sha256(json.dumps(block).encode()).hexdigest()


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Adds a transaction value to the blockchain

    Arguments:
        :sender: The sender of the coins
        :recipient: The recipient of the coins
        :amount: The amount of the coins
    """
    transaction = {
        'sender': sender,
        'recipient': recipient,
        'amount': amount
    }
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(recipient)
        participants.add(sender)
        return True
    return False

def verify_transaction(transaction):
    """ Verifies if the transaction is valid"""
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']

def mine_block():
    """ Mines a new block"""
    last_block = blockchain[-1]
    reward_transaction = {
        'sender': 'MINING',
        'recipient': owner,
        'amount': MINING_REWARD
    }
    copied_open_transactions = open_transactions[:]
    copied_open_transactions.append(reward_transaction)
    block = {
        'previous_hash': hash_block(last_block),
        'index': len(blockchain),
        'transactions': copied_open_transactions,
    }
    blockchain.append(block)
    return True


def get_last_blockchain_value():
    """ Returns the last blockchain value """
    if (len(blockchain)) <= 0:
        return None
    else:
        return blockchain[-1]


def print_blockchain(blockchain):
    """ Prints the blockchain """
    for block in blockchain:
        print(block)


def get_transaction_value():
    """ Returns the user input for transactions in a float"""
    tx_recipient = input("Enter recipient: ")
    tx_amount = float(input("Enter amount: "))
    return tx_recipient, tx_amount


def get_user_action():
    """ Returns the user input for transactions in a float"""
    print("\nWhat would you like to do?")
    print("\t1: Add a new transaction value")
    print("\t2: Mine blockchain")
    print("\t3: Print blockchain")
    print("\t4: Print participants")
    print("\t5: Check transaction validity")
    print("\th: Manipulate the blockchain")
    print("\tq: Exit")
    return input("User input: ")


def verify_chain():
    # block_index = 0
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index - 1]):
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])

def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block['transactions'] if tx['sender' == participant]] for block in blockchain]
    open_tx_sender = [tx for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx['amount'] for tx in block['transactions'] if tx['recipient' == participant]] for block in blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    return amount_received - amount_sent


should_continue = True
while should_continue:
    action = get_user_action()
    if action == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient=recipient, amount=amount):
            print('Transaction added.')
        else:
            print('Transaction failed.')
    elif action == '2':
        if mine_block():
            open_transactions = []
    elif action == '3':
        print_blockchain(blockchain)
    elif action == '4':
        print(participants)
    elif action == '5':
        if (verify_transactions()):
            print('Transactions verified.')
        else:
            print('Transactions failed.')
    elif action == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {
                'previous_hash': '',
                'index': 0,
                'transactions': [{'sender': "Chris", 'recipient': "Max", 'amount': 12}],
            }
    elif action == 'q':
        should_continue = False
    else:
        print("Invalid input, try again")

    if not verify_chain():
        print("Invalid chain, try again")
        break

    print(f'Balance of {owner}: {get_balance(owner):6.2f}')

print('Finished')
