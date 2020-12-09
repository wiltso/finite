from django.conf import settings
from Crypto.Cipher import AES
from Crypto import Random
import hashlib
import base64
import uuid


# The encrypting function for the server
def encrypt(text, password):
    CRYPT_BLOCK_SIZE = settings.CRYPT_BLOCK_SIZE

    # Make the string the correct length
    def pad(text):
        amount = (CRYPT_BLOCK_SIZE - len(text) % CRYPT_BLOCK_SIZE)
        pading = amount * chr(CRYPT_BLOCK_SIZE - len(text) % CRYPT_BLOCK_SIZE)
        return text + pading.encode()

    textPadded = pad(text.encode())
    # Generates the salt
    salt = uuid.uuid4().hex

    # Creates the key that is used in the encrypting
    # Joins together the salt and the password
    private_key = hashlib.sha256(password.encode("utf-8") + salt.encode("utf-8")).digest()

    # Encrypts the data
    iv = Random.new().read(AES.block_size)
    cipher = AES.new(private_key, AES.MODE_CBC, iv)

    # Returns as a string that has the salt added to the end
    return (base64.b64encode(iv + cipher.encrypt(textPadded))).decode("utf-8") + salt


# The decrypting function that can decrypt the encrypted stuff created above
def decrypt(text, password) -> str:
    # Gets the salt and takes away the salt from the text
    salt, text = text[-32:], text[:-32]

    # Creates the private key with the salt
    private_key = hashlib.sha256(password.encode("utf-8") + salt.encode("utf-8")).digest()

    # Makes it back to base64
    text = base64.b64decode(text.encode('utf-8'))

    # Make it into a aes object that can be decrypted
    cipher = AES.new(private_key, AES.MODE_CBC, text[:16])

    # Make the function that takes away the padding
    def removePad(text):
        return text[:-ord(text[len(text) - 1:])]

    # Returns the decrypted and un padded text as a string
    return (removePad(cipher.decrypt(text[16:]))).decode()
