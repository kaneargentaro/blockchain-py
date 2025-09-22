import json
from functools import reduce
from block import Block
from transaction import Transaction
from hash_util import hash_block
from verification import Verification


MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(
            index=0,
            previous_hash='',
            transactions=[],
            proof=100,
            timestamp=0
        )
        self.__chain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, new_chain):
        self.__chain = new_chain

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('data.json', 'r') as f:
                data_lines = f.readlines()

                blockchain_json = data_lines[0].rstrip('\n')
                raw_blockchain = json.loads(blockchain_json)

                self.chain = [
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

                self.__open_transactions = [
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
            pass
        finally:
            pass

    def save_data(self):
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
                        for block_el in self.__chain
                    ]
                ]
                outfile.write(json.dumps(savable_chain))
                outfile.write('\n')
                savable_tx = [tx.__dict__ for tx in self.__open_transactions]
                outfile.write(json.dumps(savable_tx))
        except (IOError, IndexError):
            print('Could not save blockchain')

    def proof_of_work(self):
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_balance(self):
        participant = self.hosting_node
        tx_sender = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__chain]
        open_tx_sender = [tx for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender,
                             0)
        tx_recipient = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in
                        self.__chain]
        amount_received = reduce(lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0,
                                 tx_recipient, 0)
        return amount_received - amount_sent

    def get_last_blockchain_value(self):
        """ Returns the last blockchain value """
        if (len(self.__chain)) <= 0:
            return None
        else:
            return self.__chain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        """ Adds a transaction value to the blockchain

        Arguments:
            :sender: The sender of the coins
            :recipient: The recipient of the coins
            :amount: The amount of the coins
        """
        transaction = Transaction(sender=sender, recipient=recipient, amount=amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def mine_block(self):
        """ Mines a new block"""
        last_block = self.__chain[-1]
        proof = self.proof_of_work()
        reward_transaction = Transaction(sender='MINING', recipient=self.hosting_node, amount=MINING_REWARD)
        copied_open_transactions = self.get_open_transactions()
        copied_open_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hash_block(last_block), copied_open_transactions, proof)
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        return True
