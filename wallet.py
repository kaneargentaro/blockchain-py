import binascii
from Crypto.PublicKey import RSA
from Crypto import Random

WALLET_FILE = 'wallet.txt'

class Wallet:
    def __init__(self):
        self.private_key = None
        self.public_key = None

    def create_keys(self):
        private_key, public_key = self.generate_keys()
        self.private_key = private_key
        self.public_key = public_key

    def save_keys(self):
        if (self.private_key is not None) and (self.public_key is not None):
            try:
                with open(WALLET_FILE, 'w') as f:
                    f.write(self.public_key)
                    f.write('\n')
                    f.write(self.private_key)
            except FileNotFoundError:
                print('Saving wallet failed')

    def load_keys(self):
        try:
            with open(WALLET_FILE, 'r') as f:
                keys = f.readlines()
                self.private_key = keys[0][:-1]
                self.public_key = keys[1]
        except FileNotFoundError:
            print('Loading wallet failed')


    @staticmethod
    def generate_keys():
        private_key = RSA.generate(1024, Random.new().read)
        public_key = private_key.publickey()
        return (
            binascii.hexlify(private_key.exportKey(format='DER')).decode('ascii'),
            binascii.hexlify(public_key.exportKey(format='DER')).decode('ascii')
        )