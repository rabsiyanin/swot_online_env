from Cryptodome.Cipher import AES
from Cryptodome import Random
import hashlib
import base64
import ast

class AESCipher(object):
    def __init__(self, key):
        self.bs = AES.block_size
        self.key = hashlib.sha256(key.encode()).digest()

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw.encode()))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return AESCipher._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

def encode_token(field, key):
    cipher = AESCipher(key)
    message_bytes = field.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    base64_message = base64_bytes.decode('utf-8')
    token = cipher.encrypt(base64_message)
    return str(token)

def decode_token(token, key):
    value=ast.literal_eval(token)
    cipher = AESCipher(key)
    decrypted_message = cipher.decrypt(value)
    base64_bytes = decrypted_message.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    decrypted_message = message_bytes.decode('utf-8')
    return str(decrypted_message)

def concat_strings(string_list):
    return '|'.join(string_list)

def split_string(input_string):
    return input_string.split('|')