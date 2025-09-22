import json
from functools import reduce
from collections import OrderedDict
# import pickle
from block import Block
from hash_util import hash_string_256, hash_block

MINING_REWARD = 10
blockchain = []
open_transactions = []
owner = 'John'
participants = set(owner)


def load_data():
    global blockchain
    global open_transactions
    try:
        with open('data.json', 'r') as f:
            # file_content = pickle.loads(f.read())
            # global blockchain
            # global open_transactions
            # blockchain = file_content['chain']
            # open_transactions = file_content['ot']
            data = f.readlines()
            blockchain = json.loads(data[0][:-1])
            blockchain = [Block(block['index'],
                                block['previous_hash'],
                                [
                                    OrderedDict(
                                        [
                                            ('sender', tx['sender']),
                                            ('recipient', tx['recipient']),
                                            ('amount', tx['amount']),
                                        ]) for tx in block['transactions']
                                ],
                                block['proof'],
                                block['timestamp']
                                )
                          for block in blockchain]
            open_transactions = json.loads(data[1])
            open_transactions = [{
                'transactions': [
                    OrderedDict(
                        [
                            ('sender', tx['sender']),
                            ('recipient', tx['recipient']),
                            ('amount', tx['amount']),
                        ]) for tx in block['transactions']
                ],
            } for block in open_transactions]
    except (IOError, IndexError):

        genesis_block = Block(0, '',[],100, 0)
        blockchain = [genesis_block]
        open_transactions = []
    finally:
        pass


def save_data():
    try:
        with (open('blockchain.p', 'w') as outfile):
            outfile.write(json.dumps(blockchain))
            outfile.write('\n')
            outfile.write(json.dumps(open_transactions))
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
    transaction = OrderedDict([('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(recipient)
        participants.add(sender)
        save_data()
        return True
    return False


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_string_256(guess)
    return guess_hash[:2] == '00'


def verify_transaction(transaction):
    """ Verifies if the transaction is valid"""
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def mine_block():
    """ Mines a new block"""
    last_block = blockchain[-1]
    proof = proof_of_work()
    reward_transaction = OrderedDict([('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
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
    print("\t4: Print participants")
    print("\t5: Check transaction validity")
    print("\tq: Exit")
    return input("User input: ")


def verify_chain():
    # block_index = 0
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block.previous_hash != hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


def get_balance(participant):
    tx_sender = [[tx['amount'] for tx in block.transactions if tx['sender' == participant]] for block in blockchain]
    open_tx_sender = [tx for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    tx_recipient = [[tx['amount'] for tx in block.transactions if tx['recipient' == participant]] for block in
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
        print(participants)
    elif action == '5':
        if (verify_transactions()):
            print('Transactions verified.')
        else:
            print('Transactions failed.')
    elif action == 'q':
        should_continue = False
    else:
        print("Invalid input, try again")

    if not verify_chain():
        print("Invalid chain, try again")
        break

    print(f'Balance of {owner}: {get_balance(owner):6.2f}')

print('Finished')
