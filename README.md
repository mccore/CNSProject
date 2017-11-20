# CNSProject
## Dependencies
The program requires that at least `Python 3.5` be used.
Additionally, the module `pysha3` must be installed. On Ubuntu this can be done with the command `sudo pip3 install pysha3`.
Also, `openssl` is required for the cert and key generation but this is commonly installed on most systems.

## Usage
The program requires a couple of things to work properly.
Firstly, the arguments work like so: `python3 client.py <destination IP> <destination port> <source port> <directory of files>`.
Secondly, the program should be run in two separate folders. This is to properly organize things so that it is clear that two separate clients are being launched. Do this by copying `client.py` into two different folders. Each folder should contain a `cert.pem` and a `key.pem`, two sub-folders of >=1000 random files of size of >=10Mb. However, the separate folders aren't absolutely necessary. One client can be used with one set of `cert.pem` and `key.pem` files. The folders of files can be everywhere as well as long as the path is properly specified to to the client. We generated the files using the command `for i in {1..5}; do head -c 10M </dev/urandom > randfile_$i; done`.
Thirdly, the cert and key combo must be generated and shared. This is done using the command `openssl req -x509 -nodes -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -subj '/CN=localhost'`

## Assumptions
Our first assumption is that >=1000 files of size >=10Mb are used. We assume this to prevent an attacker from simply using one or a few files to compare to a different client. If this were allowed then an adversary could know everything about a specific file if the other client also has it.

## Collision resistant hash function

## Existentially unforgeable MACs and signatures

## CPA secure public-key and symmetric-key encryption

## Security