from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import base64


def encrypt_string(input_string, key, iv):
    key = key.encode("utf-8")
    iv = iv.encode("utf-8")

    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    padder = padding.PKCS7(algorithms.AES.block_size).padder()
    padded_data = padder.update(input_string.encode()) + padder.finalize()

    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(padded_data) + encryptor.finalize()

    return {
        'ciphertext': base64.b64encode(encrypted_data).decode('utf-8')
    }
