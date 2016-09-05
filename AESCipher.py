import base64
from Crypto.Cipher import AES
from Crypto import Random
'''
Thanks to:
   http://stackoverflow.com/a/12525165
'''
'''
Using IV for having always a different output also for the same input.
The IV is also included in the output. In this way it can be used to decrypt the output.
Note: you can use os.urandom(24) for generating an enough good random string 

'''


class AESCipher:
    def __init__(self, key):
        self.key = key

    def pad(self, s):  # The lenght of an input have to be a multiple of BlockSize (16)
        return s + (16 - len(s) % 16) * chr(16 - len(s) % 16)

    def unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self.pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)  # One of the most secure of AES: CBC with IV
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):  # Simple decrypt function
        enc = base64.b64decode(enc)
        iv = enc[:16]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpad(cipher.decrypt(enc[16:]))
