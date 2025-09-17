blockchain = []


def add_value(transaction_amount, last_transaction=None):
    """ Adds a transaction value to the blockchain

    Arguments:
        :transaction_amount {float} -- Transaction amount to be added to the blockchain
        :last_transaction {list} -- Transaction hash to be added to the blockchain

    """
    if last_transaction is None:
        blockchain.append([transaction_amount])
    else:
        blockchain.append([last_transaction, transaction_amount])


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
    return float(input("Please enter transaction amount: "))

def get_user_action():
    """ Returns the user input for transactions in a float"""
    print("\nWhat would you like to do?")
    print("\t1: Add a new transaction value")
    print("\t2: Print blockchain")
    print("\tq: Exit")
    return input("User input: ")

while True:
    action=get_user_action()
    if action == '1':
        tx_amount = get_transaction_value()
        add_value(transaction_amount=tx_amount, last_transaction=get_last_blockchain_value())
    elif action == '2':
        print_blockchain(blockchain)
    elif action == 'q':
        break
    else:
        print("Invalid input, try again")

print('Finished')
