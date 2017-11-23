#!/usr/bin/env python 3.5
from socket import *
from threading import Thread
import sys
import os
import hashlib
import sha3
import ssl
import time

#The server thread is responsible for responding to client connections and sending them all of the hashes required for calculating common files
class Server(Thread):
  #The thread is initialized with its own versions of some variables as well as creating the socket and setting some options on it.
  def __init__(self, port, hash_list, ssl_certfile, ssl_keyfile):
    Thread.__init__(self)
    self.hash_list = hash_list
    self.bufsize = 65535
    self.ssl_certfile = ssl_certfile
    self.ssl_keyfile = ssl_keyfile

    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    self.socket.bind(('', int(port)))

  #The run method is what actually does the wrapping of the socket into an encrypted socket and then sends all of the hashes
  def run(self):
    self.socket.listen(5)
    while True:
      print ('SERVER: Waiting for connection')
      self.client, caddr = self.socket.accept()
      print ('SERVER: Connected to', caddr)

      #try wrapping the connection with SSL (Protocol TLSv1.2) and load up the cert and key. Also make sure to set the option to do the handshake on connect to ensure proper authentication.
      try:
        self.connstream = ssl.wrap_socket(self.client, server_side=True, certfile=self.ssl_certfile, keyfile=self.ssl_keyfile, ssl_version=ssl.PROTOCOL_TLSv1_2, do_handshake_on_connect=True)
        print("SERVER: SSL wrap succeeded for server")
      except:
        print("SERVER: SSL wrap failed for server")
        sys.exit(1)

      print('SERVER: Sending hash list')

      #Do the actual send
      for aHash in self.hash_list:
        self.connstream.send(aHash.hexdigest().encode())

    #We could just close the SSL socket but it is just a better practice to close the inner socket and then the wrapper.
    print("SERVER: Closing client connection")
    self.socket.close()
    self.connstream.close()

#The client thread is responsible for receiving the hashes from the server, computing/calculating the common ones, and printing them
class Client(Thread):
  #The thread is initialized with its own versions of some variables as well as creating the socket and setting a timeout so that we can exit the recv() loop when we stop receiving data.
  def __init__(self, host, port, hash_list, ssl_certfile):
    Thread.__init__(self)
    self.port = port
    self.host = host
    self.bufsize = 1024
    self.addr = (host, int(port))
    self.hash_list = hash_list
    self.ssl_certfile = ssl_certfile
    self.socket = socket(AF_INET , SOCK_STREAM)
    self.socket.settimeout(5)

  #Again, run is where wrapping happens and where the recv loop happens. The recv() is in a try-except block in order to break when the timeout is reached.
  def run(self):
    try:
      self.ssl_sock = ssl.wrap_socket(self.socket, ca_certs=self.ssl_certfile, cert_reqs=ssl.CERT_REQUIRED, do_handshake_on_connect=True)
      print("CLIENT: Wrapped client socket for SSL")
    except:
      print("CLIENT: Error wrapping SSL socket")
      sys.exit(1)

    try:
      self.ssl_sock.connect(self.addr)
      print("CLIENT: Client socket connected")
    except:
      print("CLIENT: Error on client socket connect")
      sys.exit(1)

    new_hash_list = []
    try:
      data = self.ssl_sock.recv(1024).decode()
      while data:
        new_hash_list.append(data)
        #print(data)
        try:
          data = self.ssl_sock.recv(1024).decode()
        except timeout:
          break
    except:
      print("CLIENT: Error on recv()")
      sys.exit(1)

    print("CLIENT: Closing server connection")
    self.socket.close()
    self.ssl_sock.close()

    #We now need to compare the hash_list we received to the hash_list that we already have. Then print out the common hashes and their total number.
    common_count = 0
    for a in new_hash_list:
      for b in self.hash_list:
        if a == b.hexdigest():
          print(a)
          common_count += 1
    print("Common file count: ", common_count)


def main():
  #Check the version info so that the program can actually be run. Technically, it should run into an error before this when checking things like "print" which would be different on 2.7. However, checking for 3.5 makes sure the crypto modules will work too.
  if sys.version_info < (3, 5):
    print("Python 3.5 or above must be used for this program")
    sys.exit(1)

  if len(sys.argv) != 5:
    print ('usage: python3 client.py <destination IP> <destination port> <source port> <directory of files>')
    sys.exit(1)

  destIP = sys.argv[1]
  destPORT = sys.argv[2]
  sourcePORT = sys.argv[3]
  directory = sys.argv[4]

  #os.system("openssl req -x509 -nodes -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -subj '/CN=localhost'")
  ssl_certfile = "./cert.pem"
  ssl_keyfile = "./key.pem"

  #Here is where we actually hash the files. I chose a rather large block size because most computers should be able to use it and still produce a hash quickly. Basically, for every file in a directory we read the block size and update the hash until the entire file is hashed. Then we store the hash and move to the next file.
  BLOCKSIZE = 65536
  hash_list = []
  for filename in os.listdir(directory):
    hasher = hashlib.sha3_512()
    fullpath = directory + "/" + filename
    with open(fullpath, 'rb') as afile:
      buf = afile.read(BLOCKSIZE)
      while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(BLOCKSIZE)
      print(hasher.hexdigest())
      hash_list.append(hasher)

  #Start the threads
  server = Server(sourcePORT, hash_list, ssl_certfile, ssl_keyfile)
  client = Client(destIP, destPORT, hash_list, ssl_certfile)

  server.start()

  input("Press ENTER to launch client\n")
  client.start()

  #Busy loop while the threds are doing their thing
  while client.isAlive() and server.isAlive():
    time.sleep(0.100)

  client.join()
  print("CLIENT: Thread joined to main")
  server.join()
  print("SERVER: Thread joined to main")

if __name__ == "__main__":
  main()