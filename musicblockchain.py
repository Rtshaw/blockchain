import hashlib
import json
import os
from time import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlparse
from uuid import uuid4
from mp3hash import mp3hash

import requests
from flask import Flask, jsonify, request, render_template

import random
import ecdsa
import base58

class Blockchain:
    def __init__(self):
        self.current_transactions = []
        self.main_chain = []
        self.nodes = set()

        # 創建主鏈創世區塊
        self.new_block('translate_tts.mp3', previous_hash='1', proof=100)

    def register_node(self, address: str) -> None:
        """
        Add a new node to the list of nodes

        :param address: Address of node. Eg. 'http://192.168.0.5:5000'
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    def valid_chain(self, main_chain: List[Dict[str, Any]]) -> bool:
        """
        Determine if a given blockchain is valid

        :param main_chain: A blockchain
        :return: True if valid, False if not
        """

        last_block = main_chain[0]
        current_main_index = 1

        while current_main_index < len(main_chain):
            block = main_chain[current_main_index]
            print(f'{last_block}')
            print(f'{block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if block['previous_hash'] != self.hash(last_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_proof(last_block['proof'], block['proof']):
                return False

            last_block = block
            current_main_index += 1

        return True

    def valid_music_chain(self, music_chain: List[Dict[str, Any]]) -> bool:
        """
        Determine if a given blockchain is valid

        :param music_chain: A blockchain
        :return: True if valid, False if not
        """

        last_music_block = music_chain[0]
        current_index = 1

        while current_index < len(music_chain):
            music_block = music_chain[current_index]
            print(f'{last_music_block}')
            print(f'{music_block}')
            print("\n-----------\n")
            # Check that the hash of the block is correct
            if music_block['previous_hash'] != self.hash(last_music_block):
                return False

            # Check that the Proof of Work is correct
            if not self.valid_music_proof(last_music_block['music_proof'], music_block['music_proof']):
                return False

            last_music_block = music_block
            current_index += 1

        return True

    def resolve_conflicts(self) -> bool:
        """
        共识算法解决冲突
        使用网络中最长的链.

        :return:  如果链被取代返回 True, 否则为False
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.main_chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                mainlength = response.json()['mainlength']
                main_chain = response.json()['main_chain']

                # Check if the length is longer and the main_chain is valid
                if mainlength > max_length and self.valid_chain(main_chain):
                    max_length = mainlength
                    new_chain = main_chain

        # Replace our main_chain if we discovered a new, valid main_chain longer than ours
        if new_chain:
            self.main_chain = new_chain
            return True

        return False

    def resolve_music_conflicts(self) -> bool:
        """
        共识算法解决冲突
        使用网络中最长的链.

        :return:  如果链被取代返回 True, 否则为False
        """

        neighbours = self.nodes
        new_music_chain = None

        # We're only looking for chains longer than ours
        max_length = len(self.music_chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                musiclength = response.json()['musiclength']
                music_chain = response.json()['music_chain']

                # Check if the length is longer and the main_chain is valid
                if musiclength > max_length and self.valid_chain(music_chain):
                    max_length = musiclength
                    new_music_chain = music_chain

        # Replace our main_chain if we discovered a new, valid main_chain longer than ours
        if new_music_chain:
            self.music_chain = new_music_chain
            return True

        return False
        

    # 交易區塊（有交易紀錄）
    def new_music_block(self, main_index, music_proof: int, previous_hash: Optional[str]) -> Dict[str, Any]:

        music_block = {
            'index':len(self.music_chain)+1,
            'main_index':main_index,
            'timestamp':time(),
            'transactions': self.current_transactions,
            'music_proof': music_proof,
            'previous_hash': previous_hash or self.hash(self.music_chain[-1]),
        }

        # Reset the current list of transactions and music chain
        self.current_transactions = []

        self.music_chain.append(music_block)
        return music_block


    # 創建音樂區塊（放音檔hash）
    def new_block(self, mp3path, proof: int, previous_hash: Optional[str]) -> Dict[str, Any]:
        """
        生成新區塊

        :param proof: The proof given by the Proof of Work algorithm
        :param previous_hash: Hash of previous Block
        :return: New Block
        """

        block = {
            'main_index': len(self.main_chain) + 1,
            'timestamp': time(),
            'proof': proof,
            'music_hash':mp3hash(mp3path),
            'previous_hash': previous_hash or self.hash(self.main_chain[-1]),
        }


        # 創立music-chain（交易區塊）的創世區塊
        self.music_chain = []
        self.new_music_block(len(self.main_chain)+1, previous_hash='1', music_proof=100)

        self.main_chain.append(block)
        return block

    # 交易紀錄
    def new_transaction(self, sender: str, recipient: str, amount: int) -> int:
        """
        生成新交易信息，信息将加入到下一个待挖的區塊中

        :param sender: Address of the Sender
        :param recipient: Address of the Recipient
        :param amount: Amount
        :return: The index of the Block that will hold this transaction
        """
        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount,
        })

        return self.last_music_block['index'] + 1

    # 錢包
    def create_wallet(self, account: str, password: str, identity: int) -> int:
        """
        創建錢包，生成錢包地址並回傳

        :param account: 使用者於系統中註冊之帳號
        :param password: 使用者於系統中註冊之密碼
        :param identity: 使用者於系統中註冊所提供之身分證
        :return: wallet_address
        """

        private_key = hex(random.randint(1, 8288608480668846482228684402464624222246648088028668608040264462))[2:]
        if len(private_key) != 64:
            for i in range(64 - len(private_key)):
                private_key = '0' + private_key

        private_key = bytes.fromhex(private_key)

        sk = ecdsa.SigningKey.from_string(private_key, curve=ecdsa.SECP256k1)
        vk = b'\x04' + sk.verifying_key.to_string()

        ek = hashlib.sha256(vk).digest()

        ripemd160 = hashlib.new('ripemd160')
        ripemd160.update(ek)
        rk = b'\x00' + ripemd160.digest()

        checksum = hashlib.sha256(hashlib.sha256(rk).digest()).digest()[0:4]
        public_key = rk + checksum

        wallet_address = base58.b58encode(public_key)

        return wallet_address

    @property
    def last_block(self) -> Dict[str, Any]:
        return self.main_chain[-1]

    @property
    def last_music_block(self) -> Dict[str, Any]:
        return self.music_chain[-1]

    @staticmethod
    def hash(block: Dict[str, Any]) -> str:
        """
        生成块的 SHA-256 hash值

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        block_string = json.dumps(block, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

    @staticmethod
    def hash(music_block: Dict[str, Any]) -> str:
        """
        生成块的 SHA-256 hash值

        :param block: Block
        """

        # We must make sure that the Dictionary is Ordered, or we'll have inconsistent hashes
        music_block_string = json.dumps(music_block, sort_keys=True).encode()
        return hashlib.sha256(music_block_string).hexdigest()

    def proof_of_work(self, last_proof: int) -> int:
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        """

        proof = 0
        while self.valid_proof(last_proof, proof) is False:
            proof += 1

        return proof

    def proof_of_music_work(self, last_music_proof: int) -> int:
        """
        简单的工作量证明:
         - 查找一个 p' 使得 hash(pp') 以4个0开头
         - p 是上一个块的证明,  p' 是当前的证明
        """

        music_proof = 0
        while self.valid_music_proof(last_music_proof, music_proof) is False:
            music_proof += 1

        return music_proof

    @staticmethod
    def valid_proof(last_proof: int, proof: int) -> bool:
        """
        验证证明: 是否hash(last_proof, proof)以4个0开头

        :param last_proof: Previous Proof
        :param proof: Current Proof
        :return: True if correct, False if not.
        """

        guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

    @staticmethod
    def valid_music_proof(last_music_proof: int, music_proof: int) -> bool:

        guess = f'{last_music_proof}{music_proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"



# Instantiate the Node
app = Flask(__name__)

UPLOAD_PATH = 'static/uploads'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_PATH)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

# 一般礦的的挖礦（交易區塊）music chain
@app.route('/<main_index>/mine', methods=['GET'])
def mine(main_index):
    # We run the proof of work algorithm to get the next proof...
    last_music_block = blockchain.last_music_block
    last_music_proof = last_music_block['music_proof']
    music_proof = blockchain.proof_of_music_work(last_music_proof)

    # 给工作量证明的節點提供獎勵.
    # 发送者为 "0" 表明是新挖出的币
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        amount=1,
    )

    # Forge the new Block by adding it to the main_chain
    music_block = blockchain.new_music_block(main_index, music_proof, None)

    response = {
        'message': "New Block Forged",
        'main_index':main_index,
        'index': music_block['index'],
        'transactions': music_block['transactions'],
        'music_proof': music_block['music_proof'],
        'previous_hash': music_block['previous_hash'],
    }
    return jsonify(response), 200

@app.route('/')
def index():
    mp3_file = []
    for filename in os.listdir(UPLOAD_FOLDER):
        if (filename.find('.mp3') > -1):
            mp3_file.append(filename)


# 音樂區塊（main chain
@app.route('/addmusic', methods=['GET', 'POST'])
def addmusic():
    if request.method == 'POST':
        file = request.files['file']
        upload_path = '{}/{}'.format(UPLOAT_FOLDER, file.filename)
        file.save(upload_path)
        
        block = blockchain.new_block(upload_path, proof, None)
        
        return 'OK'
    
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)
    
    
    response = {
        'message' : "New Music Add",
        'main_index' : block['main_index'],
        'proof' : block['proof'],
        'music_hash':block['music_hash'],
        'previous_hash' : block['previous_hash'],
    }


    return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # 檢查POST数据
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to Block {index}'}
    return jsonify(response), 201


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'main_chain': blockchain.main_chain,
        'music_chain':blockchain.music_chain,
        'mainlength': len(blockchain.main_chain),
        'musiclength':len(blockchain.music_chain),
    }
    return jsonify(response), 200



@app.route('/nodes/register', methods=['POST'])
def register_nodes():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return "Error: Please supply a valid list of nodes", 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes),
    }
    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()

    if replaced:
        response = {
            'message': 'Our main_chain was replaced',
            'new_chain': blockchain.main_chain
        }
    else:
        response = {
            'message': 'Our main_chain is authoritative',
            'main_chain': blockchain.main_chain
        }

    return jsonify(response), 200


@app.route('/wallet/create', methods=['POST'])
def create_wallet():
    values = request.get_json()

    # 檢查POST数据 (帳號；密碼；身分證)
    required = ['account ', 'password', 'identity']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a wallet
    wallet_address = blockchain.create_wallet(values['account'], values['password'], values['identity'])

    response = {'wallet_address': wallet_address}
    return jsonify(response), 201


if __name__ == '__main__':
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default=5000, type=int, help='port to listen on')
    args = parser.parse_args()
    port = args.port

    app.run(host='127.0.0.1', port=port)


