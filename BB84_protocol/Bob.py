from cqc.pythonLib import CQCConnection, qubit
import numpy as np
from BB84 import *
import time
import comm
import ast
import sys
import onetimepad as otp
import datetime
import json

"""
class Sender():
	def __init__(self,name):
		self.name=name
		self.raw_key=raw_key
		self.sifted_key=sifted_key
		self.tested_key=tested_key
		self.basis=basis
		self.sifted_basis=sifted_basis
"""



# Establish  connection  to  SimulaQron
with CQCConnection("Bob") as Bob:
 #Bob.closeClassicalServer() #if I want to use my socket functions
 n=Bob.recvClassical()[0] #number of qubits given by Alice("Eve")
 key=[]
 B=''
 skey=''
 for i in range(0,n):
  c=receive_qubits(Bob)
  #send confirmation to Alice via CAC
  #print("out meas.",c[0])
  key.append(c[0])
  B+=str(c[1]) #Bob basis
  skey+=str(c[0])
 
 #send Basis to Alice
 print("bob key before sifting :",skey)
 print("Bob basis choice",B)
 ff=B.encode()#conversion to byte
 Bob.sendClassical("Alice",ff)
 
 #receive Alice's basis
 msg=Bob.recvClassical()

 res =comm.bytes_to_list(msg)
 #print("Alice's Basis received",res)
 key_s=''
 
 for c in res:
  key_s+=str(key[c])
  
 print("Bob sifted key",key_s)
 
 time.sleep(1)
 msg1=Bob.recvClassical()
 tested_key_A=comm.bytes_to_list(msg1)
 #print("Alice's tested key received",tested_key_A)
 time.sleep(1)
 msg2=Bob.recvClassical()
 test_indices_A=comm.bytes_to_list(msg2)#test_indices from Alice

 #print("Test indices received",test_indices_A)
  
 test_key_B='' 
 for i in test_indices_A:
  test_key_B+=key_s[i]
  
 print("Bob key for testing",test_key_B) 
 ########################"Error Rate in tested keys####################################################
 x=0

 for i in range(len(tested_key_A)):
 	if int(test_key_B[i])!=int(tested_key_A[i]):
 	 x=x+1
 
 error_rate=(x/len(test_key_B))*100
 #print("#############Check Error rate in tested bits############")
 
 
 
 if error_rate!=0:#because qubits are not noisy
  print("Error rate in tested bits: {:.2f}%  ------> Eve Detected | Protocol Aborted.".format(error_rate))
  exit()
 else:
 	print("error_rate {:.2f}%".format(error_rate))
 ###################Privacy Amplification#####################################
 #print("################Privacy Amplification##################")
 sifted_key=[]
 pk=Bob.recvClassical()
 L=comm.bytes_to_list(pk)
 
 private_key=''
 for i in key_s:
 	sifted_key.append(int(i))
    #private_key=np.dot(sifted_key,L)%2#key_s is the sifted key
 for i in range(len(sifted_key)):
    private_key+=str(np.dot(sifted_key[i],L[i])%2)
 print("Bob private key :",private_key) 
 """
 f = open("B_key.txt", "a")
 f.write(str(private_key))
 f.close()
 """
 now = datetime.datetime.now()
 person_dict = {"node": "Bob",
"Key":private_key,
"date":now.strftime("%m/%d/%Y, %H:%M:%S"),
 "Number of qubits":n}
 with open('B_key.json', 'a+') as json_file:
  #json_file.seek(0) 
  json.dump(person_dict, json_file,indent=2)
 

 #############################################################################
 """
 message=Bob.recvClassical()
 cipher=otp.decrypt(messag,str(key_s))
 print("Bob ->",cipher)
 """
 ##################Socket##############################################
 time.sleep(1)
 #Bob.closeClassicalServer()
 #rec=chat.receive_message(Bob)
 cipher=Bob.recvClassical()
 print("cipher received ",cipher)
 plain=otp.decrypt(cipher.decode(),private_key)
 print("Msg Received from Alice-> ",plain)
 Bob.close()

