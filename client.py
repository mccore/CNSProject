from socket import *
from threading import Thread
import sys
import os
import hashlib
import sha3
import ssl

#This whole thing needs to use encryption and probably certs

class Server(Thread):
  def __init__(self, port, hash_list):
    Thread.__init__(self)
    self.hash_list = hash_list
    self.bufsize = 65535

    self.socket = socket(AF_INET, SOCK_STREAM)
    self.socket.setsockopt(SOL_SOCKET, SO_REUSEPORT, 1)
    self.socket.bind(('', int(port)))

  def run(self):
    self.socket.listen(5)
    while True:
      print ('Waiting for connection..')
      client, caddr = self.socket.accept()
      print ('Connected To', caddr)
      print('Sending hash list')
      #If we can't straight up send a list then we may need to turn this into a for loop
      client.send(self.hash_list)


class Client(Thread):
  def __init__(self,host,port, hash_list):
    Thread.__init__(self)
    self.port = port
    self.host = host
    self.bufsize = 1024
    self.addr = (host,port)
    self.hash_list = hash_list
    self.socket = socket(AF_INET , SOCK_STREAM)

  def run(self):
    invalid = True
    while invalid:
      try:
        invalid = False
        self.socket.connect(self.addr)
      except:
        invalid = True

    #This needs to change. We should be receiving the hash list from the other side which may need to be in a recv loop.
    while True:
      data = raw_input('> ')
      if not data:
        continue
      data = name+' said : '+data
      tcpClient.send(data)

    #We now need to compare the hash_list we received to the hash_list that we already have. Then print out the common hashes and their total number.

def main():
  print(sys.argv)
  if len(sys.argv) != 5:
    print ('usage: python3 client.py <destination IP> <destination port> <source port> <directory of files>')
  destIP = sys.argv[1]
  destPORT = sys.argv[2]
  sourcePORT = sys.argv[3]
  directory = sys.argv[4]

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


  server = Server(sourcePORT, hash_list)
  client = Client(destIP, destPORT, hash_list)

  server.start()
  client.start()

  #No idea what this is for
  server.join()

if __name__ == "__main__":
  main()