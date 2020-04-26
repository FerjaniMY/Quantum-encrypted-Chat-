import pickle
import socket


def send_message(sender, receiver_name, msg):
    
    socket_info = sender._appNet.getStateFor(sender.name)['hostDict'][receiver_name]
    s = socket.socket()
    while True:
        try:
            s.connect((socket_info.hostname, socket_info.port))
            break
        except Exception as e:
            continue
    s.send(pickle.dumps(len(msg)))
    
    bytes_sent = 0
    while bytes_sent < len(msg):
        bytes_sent += s.send(msg[bytes_sent:])
    
    s.close()



def receive_message(receiver):
    socket_info = receiver._appNet.getStateFor(receiver.name)['hostDict'][receiver.name]
    s =socket.socket()
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((socket_info.hostname, socket_info.port))
    s.listen(1)
    c, addr = s.accept()
    len_msg = pickle.loads(c.recv(256)) 
    
    msg = b''
    while len(msg) < len_msg:
        msg += c.recv(4096)
    
    c.close()
    s.close()
    return msg.decode()
def encrypt(message, qkey,nonce):
    print("Encryption")
    box = secret.SecretBox(base64.decodebytes(bytes(qkey,encoding='utf-8')))
    encrypted = box.encrypt(bytes(message, encoding="utf-8"),nonce)
    ctext = encrypted.ciphertext
    return ctext


def decrypt(ctext, qkey, nonce):
    print("Decryption")
    box = secret.SecretBox(base64.decodebytes(bytes(qkey,encoding='utf-8')))
    print(type(ctext))
    plain = box.decrypt(bytes(ctext,encoding='utf-8'),nonce)
    return plain
 