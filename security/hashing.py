import hashlib


# Hashes the string
# Uses salt for even better security
def hashing(string, salt):
    hashingStr = str(string) + str(salt)
    test = hashlib.sha1(hashingStr.encode()).hexdigest()
    return test


# Same as the one above just using sha512
def strongHashing(string, salt):
    hashingStr = str(string) + str(salt)
    return hashlib.sha512(hashingStr.encode()).hexdigest()
