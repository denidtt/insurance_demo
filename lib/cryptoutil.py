import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os
import base64
import secretsutil

AWS_SECRET_NAME = 'example-secret-here'

secrets = secretsutil.get_secret(AWS_SECRET_NAME)
data = json.loads(secrets)

en_key = data['T2_Key']
en_iv = data['T2_IV']



def encrypt_string(input_string,key,iv):
 key = os.urandom(16) # AES-128
 iv = os.urandom(16) # Initialization vector

 cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
 padder = padding.PKCS7(algorithms.AES.block_size).padder()
 padded_data = padder.update(input_string.encode()) + padder.finalize()

 encryptor = cipher.encryptor()
 encrypted_data = encryptor.update(padded_data) + encryptor.finalize()


 return {
  'ciphertext': base64.b64encode(encrypted_data).decode('utf-8'),
  'iv': base64.b64encode(iv).decode('utf-8')
 }



print(encrypt_string("deni",en_key,en_iv))
