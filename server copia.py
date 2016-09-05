#!/usr/bin/env python3

import socket
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import os
import AESCipher

serversock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates an INET socket STREAM-type
serversock.bind(('localhost', 1604))  # Binds the socket to an host and a port
serversock.listen(5)  # Starts listening with 5 max connections on the socket


def RSAencrypt(pubkey, message):
    publickey = RSA.importKey(pubkey)
    cipher = PKCS1_OAEP.new(publickey)
    ciphertext = cipher.encrypt(message)
    return ciphertext


while 1:
    (SocketClient, address) = serversock.accept()  # Accepting the new connection
    print("Connected by", address)
    pubkey = SocketClient.recv(1024)  # Retrieve the RSA public key of the client
    print("Public key received.\n")
    # if not data: break# Data = 0, il socket ha finito la trasmissione.
    AESkey = os.urandom(24)  # Generate a 'random' key for AES (16,24 or 32 bit)
    SocketClient.sendall(RSAencrypt(pubkey, AESkey))  # Send the AES key to the client, in this way the communication
    print("AESKey was sent.\n")  # can continue with AES crypthography (better performace then RSA)
    # Now it should be possible to continue the communication with AES enc/dec
    aesc = AESCipher.AESCipher(AESkey)
    SocketClient.sendall(aesc.encrypt("Server.... OK!"))
    while 1:
        data = SocketClient.recv(1024)
        if data:
            # print "Encrypted data: ", data
            print(aesc.decrypt(data))
        SocketClient.sendall(aesc.encrypt("Server.... pong!"))
serversock.close()
