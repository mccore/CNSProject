# CNSProject
At least two clients, say Alice and Bob, want to find out how many files they have in
common. Alice and Bob do not deviate from their protocol but might try to analyze what they see to get more information (semi-honest behavior). The objective of this project is to make sure that Alice and Bob get what they want without learning more than they should.

## Dependencies
The program requires that at least `Python 3.5` be used.    
Additionally, the module `pysha3` must be installed. On Ubuntu this can be done with the command `sudo pip3 install pysha3`. If pip3 is not installed please use the command `sudo apt-get install python3-pip`.
Also, `openssl` is required for the cert and key generation but this is commonly installed on most systems.

## Usage
The program requires a couple of things to work properly.
First, the arguments work like so: `python3 client.py <destination IP> <destination port> <source port> <directory of files>`.
Second, the program should be run in two separate folders. This is to properly organize things so that it is clear that two separate clients are being launched. Do this by copying `client.py` into two different folders. Each folder should contain a `cert.pem` and a `key.pem`, two sub-folders of >=1000 random files of size of >=10Mb. However, the separate folders aren't absolutely necessary. One client can be used with one set of `cert.pem` and `key.pem` files. The folders of files can be everywhere as well as long as the path is properly specified to to the client. We generated the files using the command `for i in {1..5}; do head -c 10M </dev/urandom > randfile_$i; done`.
Third, the cert and key combo must be generated and shared. This is done using the command `openssl req -x509 -nodes -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -subj '/CN=localhost'`.
Fourth, keep in mind that in order to start the client receiving one must hit `enter`.

## Example
![Program in action](https://github.com/mccore/CNSProject/blob/master/example.gif)

## Assumptions
Our first assumption is that >=1000 files of size >=10Mb are used. We assume this to prevent an attacker from simply using one or a few files to compare to a different client. If this were allowed then an adversary could know everything about a specific file if the other client also has it.
Our second assumption is that the certificate and key are disseminated to all the clients by some other mechanism outside the scope of the project.
Our third assumption is that the files that are in common are *exactly* the same, byte for byte. Otherwise, the hashes will be different and the program will miss common files.

## Collision resistant hash function
We chose sha-3 (Keccak) with 512 bits as our hash function so that nothing can be learned about a file even when a client gets the hash. Furthermore, collisions have not been found in sha-3. This can be seen in [this presentation](https://csrc.nist.gov/CSRC/media/Events/ISPAB-DECEMBER-2013-MEETING/documents/new_sha3_functions.pdf) from NIST as well as [this cryptanalysis](http://christina-boura.info/sites/default/files/presentation_5.pdf) of the hash scheme. In addition, we found [this](https://crypto.stackexchange.com/questions/45377/why-cant-we-reverse-hashes) stack exchange answer useful in explaining why we can't invert the hashes to gain information about the files.

## CPA secure public-key and symmetric-key encryption and Existentially unforgeable MACs and signatures
CPA security is guaranteed by our usage of TLSv1.2. Please refer to [this article](https://blog.cryptographyengineering.com/2012/09/28/on-provable-security-of-tls-part-2/) for a simple explanation of the security proof and [this paper](https://blog.cryptographyengineering.com/2012/09/28/on-provable-security-of-tls-part-2/) for the full security proof. These same two links also include explanations for the MACs and signatures as well. However more details can be found in [RFC 5246](https://tools.ietf.org/html/rfc5246) which provides specifications for TLSv1.2 as well as [RFC 6066](https://tools.ietf.org/html/rfc6066) which provides specifications for TLS extensions.

## Security/Tests
One piece of evidence for the security of the program can be seen in this [zipped sample capture from Wireshark](https://www.dropbox.com/s/5xo37gr07b14q4e/Sample_Capture.pcapng.zip?dl=0). In order to replicate the test one can choose the `loopback` interface in Wireshark and begin capturing packets while specifying the filter `(tcp.port == 6666) or (tcp.port == 8888)` where the ports are the source and destination port specified to the clients. Additionally [this](https://osqa-ask.wireshark.org/questions/34075/why-wireshark-cannot-display-tlsssl) link shows how to add ports to a protocol's filter so that the actual SSL/TLS packets can be seen. 

## References
https://docs.python.org/3/installing/index.html

http://www.bearcave.com/software/python/SSLClientServer.py
