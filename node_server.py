from flask import Flask, jsonify
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
        }), 201
    else:
        return jsonify({
            'message': 'Failed to save keys.',
        }), 500


@app.route('/mine', methods=['POST'])
def mine_():
    block = blockchain.mine_block()
    if block:
        dict_block = block.__dict__.copy()
        dict_block['transactions'] = [tx.__dict for tx in dict_block['transactions']]
        return jsonify({
            'message': 'Block added successfully',
            'block': dict_block
        }), 201
    else:
        response = {
            'message': 'Adding a block failed',
            'wallet_set_up': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_chain():
    chain = blockchain.chain
    dict_chain = [block.__dict__.copy() for block in chain]
    for dict_block in dict_chain:
        dict_block['transactions'] = [tx.__dict.copy() for tx in dict_block['transactions']]
    return jsonify(dict_chain), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
