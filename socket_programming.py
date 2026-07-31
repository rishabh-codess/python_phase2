import socket 
s= socket.socket()
print ('socket created:')
s.bind(('localhost', 9999))
s.listen(3)
print ('waiting for connection')
while True:
    c, addr =s.accept()
    print("connected to server", addr)
    c.send(bytes('welcome to home','utf-8'))
    c.close()