import json
from functools import reduce
from block import Block
from transaction import Transaction
from hash_util import hash_block
from verification import Verification

MINING_REWARD = 10
blockchain = []
open_transactions = []
owner = 'John'


def load_data():
    global blockchain, open_transactions
    try:
        with open('data.json', 'r') as f:
            data_lines = f.readlines()

            blockchain_json = data_lines[0].rstrip('\n')
            raw_blockchain = json.loads(blockchain_json)

            blockchain = [
                Block(
                    index=block['index'],
                    previous_hash=block['previous_hash'],
                    transactions=[
                        Transaction(
                            sender=tx['sender'],
                            recipient=tx['recipient'],
                            amount=tx['amount']
                        )
                        for tx in block['transactions']
                    ],
                    proof=block['proof'],
                    timestamp=block['timestamp']
                )
                for block in raw_blockchain
            ]

            transactions_json = data_lines[1]
            raw_transactions = json.loads(transactions_json)

            open_transactions = [
                {
                    'transactions': [
                        Transaction(
                            tx['sender'],
                            tx['recipient'],
                            tx['amount'],
                        ) for tx in block['transactions']
                    ],
                }
                for block in raw_transactions
            ]
    except (IOError, IndexError):
        genesis_block = Block(
            index=0,
            previous_hash='',
            transactions=[],
            proof=100,
            timestamp=0
        )
        blockchain = [genesis_block]
        open_transactions = []
    finally:
        pass


def save_data():
    try:
        with (open('blockchain.txt', 'w') as outfile):
            savable_chain = [
                block.__dict__ for block in [
                    Block(
                        block_el.index,
                        block_el.previous_hash,
                        [
                            tx.__dict__ for tx in block_el.transactions
                        ],
                        block_el.proof,
                        block_el.timestamp
                    )
                    for block_el in blockchain
                ]
            ]
            outfile.write(json.dumps(savable_chain))
            outfile.write('\n')
            savable_tx = [tx.__dict__ for tx in open_transactions]
            outfile.write(json.dumps(savable_tx))
            # save_data = {
            #     'chain': blockchain,
            #     'ot': open_transactions,
            # }
            # outfile.write(pickle.dumps(save_data))
    except (IOError, IndexError):
        print('Could not save blockchain')


def add_transaction(recipient, sender=owner, amount=1.0):
    """ Adds a transaction value to the blockchain

    Arguments:
        :sender: The sender of the coins
        :recipient: The recipient of the coins
        :amount: The amount of the coins
    """
    transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
    verifier = Verification()
    if verifier.verify_transaction(transaction, get_balance):
        open_transactions.append(transaction)
        save_data()
        return True
    return False


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    verifier = Verification()
    while not verifier.valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof

def mine_block():
    """ Mines a new block"""
    last_block = blockchain[-1]
    proof = proof_of_work()
    reward_transaction = Transaction(sender='MINING', recipient=owner, amount=MINING_REWARD)
    copied_open_transactions = open_transactions[:]
    copied_open_transactions.append(reward_transaction)
    block = Block(len(blockchain), hash_block(last_block), copied_open_transactions, proof)
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
    print("\t4: Check transaction validity")
    print("\tq: Exit")
    return input("User input: ")


def get_balance(participant):
    tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in blockchain]
    open_tx_sender = [tx for tx in open_transactions if tx.sender == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                    blockchain]
    amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                             tx_recipient, 0)
    return amount_received - amount_sent


load_data()

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
            save_data()
    elif action == '3':
        print_blockchain(blockchain)
    elif action == '4':
        verifier = Verification()
        if verifier.verify_transactions(open_transactions, get_balance):
            print('Transactions verified.')
        else:
            print('Transactions failed.')
    elif action == 'q':
        should_continue = False
    else:
        print("Invalid input, try again")

    verifier = Verification()
    if not verifier.verify_chain(blockchain=blockchain):
        print("Invalid chain, try again")
        break

    print(f'Balance of {owner}: {get_balance(owner):6.2f}')

print('Finished')
