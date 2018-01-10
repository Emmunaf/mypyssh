#!/usr/bin/env python3

import socket
from Crypto.Cipher import PKCS1_OAEP
from Crypto.PublicKey import RSA
import os
import AESCipher
import threading
import Plugin

class Server(object):
    """A server class used to handle client connection and command execution.

    Internal attributes:
    host -- server host
    port -- port to use for listening and communication
    s -- the socket
    """

    def __init__(self, host, port=1604):
        """Initialize a Plugin class.

        Keyword arguments:
        host -- server host
        port -- used port [default: 1604]
        """

        self._host = host
        self._port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Creates an INET socket STREAM-type
        self.s.bind((host, port))  # Binds the socket to an host and a port
        self.plugin = Plugin.Plugin("Plugins")

    def wait_connection(self):
        """ Wait for a new connection and start a new thread to handle the connection."""

        self.s.listen(5)  # Starts listening with 5 max queued connections on the socket
        while True:
            try:
                sock_client, address = self.s.accept()
                sock_client.settimeout(1800)
                threading.Thread(target=self._listen_client, args=(sock_client, address)).start()
            except (KeyboardInterrupt, SystemExit):
                print("The server is shutdown")
                self.s.close()
                os._exit(0)

    def _listen_client(self, sock_client, address):
        """Called when a new thread starts the connection procedure.

        Starts the handshake to establish a secure connection through RSA and then AES.
        Keyword arguments:
        sock_client -- socket object returned by the socket.accept() method
        address -- address bound to the socket on the other side
        """

        print("Connected by ", address)
        pubkey = sock_client.recv(1024)  # Retrieve the RSA public key of the client
        print("Public key received.\n")
        AESkey = os.urandom(24)  # Generate a 'random' key for AES (16,24 or 32 bit)
        sock_client.sendall(
            self.RSAencrypt(pubkey, AESkey))  # Send the AES key to the client, in this way the communication
        print("AESKey was sent.\n")  # can go on with AES cryptography (better performance than RSA)
        # Now it should be possible to continue the communication with AES enc/dec
        aesc = AESCipher.AESCipher(AESkey)
        sock_client.sendall(aesc.encrypt("Server.... OK!"))
        while True:
            data = sock_client.recv(1024)
            if data:
                cmd = str(aesc.decrypt(data), 'utf-8')  # Casting needed because decrypt returns bytes not string
                result = self.plugin.run(cmd)  # HERE plugin
                sock_client.sendall(aesc.encrypt(result))
            else:
                print("Client with addr:", address, "went offline.")
                sock_client.close()
                return -1

    def get_host(self):
        """Return the host"""
        return self._host

    def get_port(self):
        """Return the port"""
        return self._port

    @staticmethod
    def RSAencrypt(pubkey, message):
        public_key = RSA.importKey(pubkey)
        cipher = PKCS1_OAEP.new(public_key)
        cipher_text = cipher.encrypt(message)
        return cipher_text

if __name__ == "__main__":
    port = int(input("Server port:"))
    Server('localhost',port).wait_connection()