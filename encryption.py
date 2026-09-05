from phe import paillier

public_key, private_key = paillier.generate_paillier_keypair()

def encrypt_record(value: float):
    return public_key.encrypt(value)

def decrypt_record(encrypted_value):
    return private_key.decrypt(encrypted_value)
