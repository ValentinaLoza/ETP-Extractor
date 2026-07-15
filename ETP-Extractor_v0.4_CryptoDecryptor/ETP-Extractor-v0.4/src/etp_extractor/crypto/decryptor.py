from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding as asymmetric_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding as symmetric_padding


def decrypt_aes_passphrase(aes_record_content: str, private_key_path: Path) -> bytes:
    private_key = serialization.load_pem_private_key(
        private_key_path.read_bytes(), password=None
    )
    encrypted_key = bytes(ord(character) for character in aes_record_content)
    return private_key.decrypt(encrypted_key, asymmetric_padding.PKCS1v15())


def _evp_bytes_to_key(password: bytes, salt: bytes) -> tuple[bytes, bytes]:
    generated = b""
    previous = b""
    while len(generated) < 48:
        previous = hashlib.md5(previous + password + salt).digest()
        generated += previous
    return generated[:32], generated[32:48]


def decrypt_cryptojs_openssl(ciphertext: str, passphrase: bytes) -> bytes:
    raw = base64.b64decode(ciphertext)
    if raw[:8] != b"Salted__":
        raise ValueError("Content is not in CryptoJS/OpenSSL salted format")

    key, iv = _evp_bytes_to_key(passphrase, raw[8:16])
    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(raw[16:]) + decryptor.finalize()
    unpadder = symmetric_padding.PKCS7(128).unpadder()
    return unpadder.update(padded) + unpadder.finalize()


def find_aes_record(records: list[dict]) -> dict:
    for record in records:
        if record.get("title") == "aeskey":
            return record
    raise KeyError("RocksDB does not contain the aeskey record")
