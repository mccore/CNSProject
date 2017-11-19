from socket import *
from threading import Thread
import sys
import os
import hashlib
import sha3
import ssl
import time

#This whole thing needs to use encryption and probably certs

class Server(Thread):
  def __init__(self, port, hash_list, ssl_certfile, ssl_keyfile):
    Thread.__init__(self)
    self.hash_list = hash_list
    self.bufsize = 65535
    self.ssl_certfile = ssl_certfile
    self.ssl_keyfile = ssl_keyfile

    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    self.socket.bind(('', int(port)))

  msg = None
  def run(self):
    self.socket.listen(5)
    while True:
      print ('Waiting for connection..')
      client, caddr = self.socket.accept()
      print ('Connected To', caddr)
      #try wrapping the connection with SSL (Protocol TLSv2)
      try:
      	self.connstream = ssl.wrap_socket(self.conn, serverSide=True, 
      									  certfile=ssl_certfile, keyfile=ssl_keyfile,
      									  ssl_version=ssl.PROTOCOL_TLSv2)
      	print "SSL wrap succeeded for server"
      except socket.error, msg:
      	print "SSL wrap failed for server"

      print('Sending hash list')
      #If we can't straight up send a list then we may need to turn this into a for loop
      client.send(self.hash_list)


class Client(Thread):
  def __init__(self,host,port, hash_list, ssl_certfile):
    Thread.__init__(self)
    self.port = port
    self.host = host
    self.bufsize = 1024
    self.addr = (host,port)
    self.hash_list = hash_list
    self.ssl_certfile = ssl_certfile
    self.socket = socket(AF_INET , SOCK_STREAM)

  def run(self):
    while invalid:
      try:
        self.ssl_sock = ssl.wrap_socket(self.socket, ca_certs=self.ssl_certfile, cert_reqs=ssl.CERT_REQUIRED)
        print("Wrapped client socket for SSL")
      except socket.error:
        print("Error wrapping SSL socket")
        exit(1)

      try:
        self.ssl_sock.connect(self.addr)
        print("Client socket connected")
      except socket.error, msg:
        print("Error on client socket connect")
        exit(1)

    #We should be receiving the hash list from the other side which may need to be in a recv loop.
    new_hash_list = []
    while True:
      try:
        new_hash_list.append(self.ssl_sock.recv(1024))
      except:
        print("Error on recv()")
        exit(1)

    self.socket.close()
    self.ssl_sock.close()

    #We now need to compare the hash_list we received to the hash_list that we already have. Then print out the common hashes and their total number.

def main():
  if len(sys.argv) != 5:
    print ('usage: python3 client.py <destination IP> <destination port> <source port> <directory of files>')

  destIP = sys.argv[1]
  destPORT = sys.argv[2]
  sourcePORT = sys.argv[3]
  directory = sys.argv[4]

  os.system("openssl req -x509 -nodes -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -subj '/CN=localhost'")
  ssl_certfile = "./cert.pem"
  ssl_keyfile = "./key.pem"

  BLOCKSIZE = 65536
  hash_list = []
  for filename in os.listdir(directory):
    hasher = hashlib.sha3_512()
    with open(filename, 'rb') as afile:
      buf = afile.read(BLOCKSIZE)
      while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(BLOCKSIZE)
      print(hasher.hexdigest())
      hash_list.append(hasher)


  server = Server(sourcePORT, hash_list, ssl_certfile, ssl_keyfile)
  client = Client(destIP, destPORT, hash_list, ssl_certfile)

  server.start()
  client.start()

  while client.isAlive() and server.isAlive():
    time.sleep(0.100)
  #No idea what this is for
  #server.join()


if __name__ == "__main__":
  main()