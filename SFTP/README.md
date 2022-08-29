## Requirements 

`pip install paramiko`

`pip install sftpserver`

Create an SSL Certificate

`openssl req -out CSR.csr -new -newkey rsa:2048 -nodes -keyout /tmp/test_rsa.key`

Python Code

```
import paramiko
pkey = paramiko.RSAKey.from_private_key_file('/tmp/test_rsa.key')
transport = paramiko.Transport(('localhost', 3373))
transport.connect(username='admin', password='password', pkey=pkey)
sftp = paramiko.SFTPClient.from_transport(transport)
sftp.listdir('.')
```
