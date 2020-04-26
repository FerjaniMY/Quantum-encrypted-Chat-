from cqc.pythonLib import CQCConnection, qubit
import numpy as np
from BB84 import *
import time
import comm
from random import *
import onetimepad as otp
import json
import datetime
import classicalC as chat
#import socket



# Establish a connection  to  SimulaQron
with CQCConnection("Alice") as Alice:
 
 print("********BB84 protocol*******************")
 #Alice.closeClassicalServer() #if I want to use my socket functions
 m=[] 
 B=[]
 S=''
 n=20#number of qubits
 Alice.sendClassical("Bob",n)#send the number of qubits
 key= np.random.randint(0, high=2**n)#to replace with QRNG() function
 k=np.binary_repr(key,n) #binary representation
 #print("Alice's random key",key)
 print("Alice initial key :",k)
 #print("##########Send Qubits#############")
 for index, digit in enumerate(k):
    
  
  m.append(str(digit))
  s=prepare_qubits(Alice,"Bob",digit) #send BB84 states
  #receive a confirmation msg from Bob via the CAC
  B.append(s[1])
  S+=str(s[1])
 """
 #send Alice's basis to Bob 
 ff=S.encode()#conversion to byte
 Alice.sendClassical("Bob",ff)
 """
 
 print('Alice basis :',S)
 
 #received Bob's Basis
 
 x=Alice.recvClassical()
 B_basis=list(x.decode())
 #print("Bob basis received",B_basis)
 #print(B_basis.split(""))
 aa=sifted_key(B,B_basis,m)
 #print("##################Sifting#################################")
 print("Alice sifted key",aa[0])

 
 listToStr ="["+','.join(map(str, aa[1]))+"]"
 ff=listToStr.encode()
 Alice.sendClassical("Bob",ff)

 #####################TEST N RANDOM BITS################################
 
 test_key=[]
 test=list(range(0,len(aa[0])))
 
 test_indices=sample(test,len(aa[0])//2)
 print("test indices :",test_indices)
 for i in test_indices:
 	test_key.append(aa[0][i])
 print("Alice key for testing :",test_key)
 msg1=comm.list_to_bytes(test_key)
 Alice.sendClassical('Bob',msg1)
 time.sleep(1)
 test2=''
 
 msg2=comm.list_to_bytes(test_indices)
 Alice.sendClassical('Bob',msg2)

 #################### OTHER RECONCILIATION##########################

 #Later Alice will xor two from list indices, send indices and xor result to Bob
 """
 x=0
 f or i,j in enumerate(test_indices):
	x=(sifted_key[j]+sifted_key[j+1])%2
	print("positions",j)
	print("Xor result",x)
	del test_indices[0]
	del test_indices[1]

 #send(i,i+1),xor result  --> Send a -dict{tuple:XOR_value} , tuple(pos1,pos2)
 """
	
 #######################Seed################################################

 randBinList = lambda n: [randint(0,1) for b in range(1,n+1)] 
 kl=len(aa[0])#len of sifted key
 L=randBinList(kl)
 sifted_key=[]
 for i in aa[0]:
 	sifted_key.append(int(i))
 #print(sifted_key)
 #print(L)
 
 pk=comm.list_to_bytes(L)
 Alice.sendClassical("Bob",pk)
 private_key=''
 for i in range(len(sifted_key)):
 	private_key+=str(np.dot(sifted_key[i],L[i]) % 2)
 #private_key=np.dot(sifted_key,L)%2
 print("Alice private key :",private_key) 
 
 #########Storing keys in file#############
 """
 f = open("A_key.txt", "a")
 f.write(str(private_key))
 f.close()
 """
 now = datetime.datetime.now()
 person_dict = {"node": "Alice",
"Key":private_key,
"date":now.strftime("%m/%d/%Y, %H:%M:%S"),
 "Number of qubits":n}
 with open('A_key.json', 'a+') as json_file:
  #json_file.seek(0) 
  json.dump(person_dict, json_file,indent=2)


 ########################Encryption##########################
 """
 print("€€€€€€Encryptio###################")
 message='hi Quantum'
 cipher=otp.encrypt(message,str(aa[0]))
 print("cipher",cipher.encode())
 print("Alice->",message)
 Alice.sendClassical('Bob',cipher)
 """
 #IDEA : if length of the key == 10 -->encrypt
 """ 
 ff=open("A_key.txt", "r")
 pr_k=ff.read()
 if len(pr_k)>=8: # n run time
 	print('Private key = ',pr_k)
 	mss=input("Alice ..>")
 	cipher=otp.encrypt(mss,str(pr_k))
 	print("cipher",cipher)
 ff.close()
 """
 ############Socket#############################################
# print("Send message ? %n 1-> Yes %n 2-> Exit")

 #time.sleep(1)
 #Alice.closeClassicalServer()
 ###########"##########
 #print("*************Exchange messages******************")

 msq='Hello Bob!!!'
 print("Alice -> ",msq)
 cipher=otp.encrypt(msq,private_key)
 Alice.sendClassical("Bob",bytes(cipher.encode()))
 #chat.send_message(Alice,'Bob',bytes(msq.encode()))

  #Close  connection  to  SimulaQron
 Alice.close()


 

 
