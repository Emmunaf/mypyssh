#!/usr/bin/env python3



"""client.py: A client for *** that uses sockets and RSA/AES encrypted communication"""

__author__ = "Emanuele Munafò"
__version__ = "0.1.a"
__email__ = "ema.muna95@gmail.com"
__status__ = "Development"

import socket
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import AESCipher
import sys


class Client(object):
    """Just a client class.

    Internal attributes:
    prikey -- RSA private key
    s -- the socket
    """

    def __init__(self, host='localhost', port=1604):
        """Start a new encrypted connection.

        Arguments:

            host -- host to connect
            port -- used port for connection

        """

        # Generate a public and a private RSA key
        RSAkey = RSA.generate(1024)
        pubkey = RSAkey.publickey().exportKey()
        self.prikey = RSAkey.exportKey()
        # Now let's create a new socket
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Set 45secs timeout for connection, 120 by default
        self.s.settimeout(45.0)
        try:
            # Try to enstabilish connection to the server
            self.s.connect((host, port))
            # Sends the public RSA Key to the server
            self.s.sendall(pubkey)
            print("Public RSA key sended to the server!")
            # Receives the AES key ciphred with RSA from the server
            AESdata = self.s.recv(1024)
            # that can be decrypted just by the client with RSA private key
            AESkey = self.RSAdecrypt(AESdata)
            print("Received the AESkey.\n")
            self.aesc = AESCipher.AESCipher(AESkey)
            # Now client should be ready for AES encrypted communication
        except socket.error as exc:
            # socket.timeout is included here too
            print("Connection to the server failed:\nsocket.error : %s" % exc)
            return

        print("Connected to:\nHost: ", host, "\nPort: ", port, "\n")
        print("Now the client is ready for AES encrypted communication!\nChecking for server status...")
        while True:
            try:  # TODO better error handling!
                data = self.get()
                print(data, "\nEnter an input:")
                cmd = input()
                if cmd.strip() == '!q':
                    self.s.close()
                    sys.exit(1)
                self.send(cmd)
            except socket.error as err:
                print("Aborting...\nError on socket: ", err)
                self.s.close()
                sys.exit(1)
            except KeyboardInterrupt:
                print("Closing connection...")
                self.s.close()
                sys.exit(1)
            except Exception:
                print("Unknown error.\nClosing connection.")
                self.s.close()
                sys.exit(1)

    def RSAdecrypt(self, ciphertext):
        """Decrypt RSA ciphred text using the private key.

        Keyword arguments:
        ciphertext -- the RSA ciphred text
        """
        
        privatekey = RSA.importKey(self.prikey)
        cipher = PKCS1_OAEP.new(privatekey)
        message = cipher.decrypt(ciphertext)
        return message
    
    def get(self):
        """Receive data from socket and return the decrypted message"""
        data = self.s.recv(1024)
        return self.aesc.decrypt(data)
        
    def send(self, message):
        """Send message to server in encrypted form"""
        smessage = self.aesc.encrypt(message)
        self.s.sendall(smessage)
        # print "Encrypted message", smessage
        
    def close(self, exitmessage):
        """Close the socket"""
        self.s.shutdown(socket.SHUT_WR)
        self.s.close()

client = Client("localhost", 1604)
