from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return 'This works'


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify({
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }), 200
    else:
        return jsonify({
            'message': 'Failed to load keys.',
        }), 500


@app.route('/wallet', methods=['POST'])
def create_keys():
    wallet.create_keys()
    if wallet.save_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        return jsonify({
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_balance()
        }), 201
    else:
        return jsonify({
            'message': 'Failed to save keys.',
        }), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_balance()
    if balance is not None:
        return jsonify({
            'message': 'Fetched balance successfully',
            'balance': balance,
        })
    else:
        return jsonify({
            'message': 'Loading balance failed',
            'wallet_set_up': wallet.public_key is not None,
        }), 500


@app.route('/mine', methods=['POST'])
def mine_():
    block = blockchain.mine_block()
    if block:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict__ for tx in dict_block['transactions']]
        return jsonify({
            'message': 'Block added successfully',
            'block': dict_block,
            'funds': blockchain.get_balance()
        }), 201
    else:
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    values = request.get_json()
    if not values:
        return jsonify({
            'message': 'No inputs provided.',
        }), 400

    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        return jsonify({
            'message': 'Required fields are not present.',
        }), 400

    if wallet.public_key is None:
        return jsonify({
            'message': 'No wallet set up.',
        }), 400

    recipient = values['recipient']
    amount = values['amount']

    signature = wallet.sign_transaction(wallet.public_key, recipient, amount)

    if blockchain.add_transaction(recipient, amount, signature):
        return jsonify({
            'message': 'Transaction added successfully',
            'transaction': {
                'sender': wallet.public_key,
                'recipient': recipient,
                'amount': amount,
                'signature': signature,
            },
            'funds': blockchain.get_balance()
        }), 201
    else:
        return jsonify({
            'message': 'Failed to add transaction',
        }), 500

@app.route('/transactions', methods=['GET'])
def get_transactions():
    transactions = blockchain.open_transactions
    dict_transactions = [tx.__dict__ for tx in transactions]
    return jsonify(dict_transactions), 200

@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict__.copy() for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
