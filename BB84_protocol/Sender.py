from cqc.pythonLib import CQCConnection, qubit
import numpy as np
from BB84 import *
import time
import comm
from random import *
import onetimepad as otp
import json
import datetime






class BB84_Sender():
	"""
	Author : Mohamed Yassine EL-Ferjani
	All copyrights reserved
	"""

	def __init__(self,cqc_sender,receiver,sender="Alice",nb_qubits=20,hacker=None):
		self.sender=sender      
		self.raw_key=''
		self.basis=''
		self.sifted_key=[]
		self.test_indices=[]
		self.test_key=[]
		
		
		#self.error_rate=calcul_error()
		self.nb_qubits=nb_qubits
		self.receiver=receiver
		self.cqc_sender=cqc_sender
		#self.random_key=self.generate_random_key()
		#self.random_key=QRNG()
		self.initial_k=[]#initial random key
		self.hacker=hacker

	#def generate_random_key(self):
	#def recv_auth_channel(self,msg,receiver):
	#def send_auth_channel(self,msg):
	def send_qubits(self):
		key= np.random.randint(0, high=2**self.nb_qubits)#to replace with QRNG() function
		k=np.binary_repr(key,self.nb_qubits) #binary representation
		print("Alice initial key :",k)
		for index, digit in enumerate(k):
		 self.initial_k.append(str(digit))
		 if self.hacker=="Eve":
		  s=prepare_qubits(self.cqc_sender,self.hacker,digit) #send BB84 states
		  self.basis+=(s[1])
		 else:
		  s=prepare_qubits(self.cqc_sender,self.receiver,digit) #send BB84 states
		  self.basis+=(s[1])

		print("Alice basis",self.basis)
		

		#receive ACK from Bob
		x=self.cqc_sender.recvClassical()[0]
		if x==self.nb_qubits:
		 print("Bob ACK (All qubit received) ")
		else:
		  print("Error , protocol Aborted")
		  exit()

	

	def sifting(self):
		x=self.cqc_sender.recvClassical()
		B_basis=x.decode()
		k=sifted_key(self.basis,B_basis,self.initial_k)
		for i in k[0]:
			self.sifted_key.append(int(i))
		self.sifted_basis=k[1]
		print("Alice sifted key",self.sifted_key)
		msg=comm.list_to_bytes(self.sifted_basis)
		self.cqc_sender.sendClassical(self.receiver,msg)
	

	def testing(self):      
		test=list(range(0,len(self.sifted_key)))
		self.test_indices=sample(test,len(self.sifted_key)//2)
		print("test indices :",self.test_indices)
		for i in self.test_indices:
			self.test_key.append(self.sifted_key[i])
		print("Alice key for testing :",self.test_key)
		msg1=comm.list_to_bytes(self.test_key)
		self.cqc_sender.sendClassical(self.receiver,msg1)
		time.sleep(1)
		msg2=comm.list_to_bytes(self.test_indices)
		self.cqc_sender.sendClassical(self.receiver,msg2)
	


	#def error_correction():

	def privacy_amplification(self):
		self.private_key=''
		
		randBinList = lambda n: [randint(0,1) for b in range(1,n+1)] 
		kl=len(self.sifted_key)#len of sifted key
		L=randBinList(kl)
		sifted_key=[]
		
		msg=comm.list_to_bytes(L)
		self.cqc_sender.sendClassical(self.receiver,msg)
		
		for i in range(len(L)):
		 self.private_key+=str(np.dot(self.sifted_key[i],L[i]) % 2)
		
		print("Alice private key :",self.private_key) 
		#return self.private_key
	#def calcul_error(self):

	def BB84_key(self):
		self.send_qubits()
		self.sifting()
		self.testing()
		#self.error_correction()
		"""
		if self.error_rate >= threshhold:
			print("Error rate {}% | Protocol Aborted!! ".format(self.error_rate))
			exit()
		""" 
		self.privacy_amplification()
		return self.private_key
	"""	
 
	def send_QOTP_msg(self,msg):
		cipher=otp.encrypt(msg,self.BB84_key())
		self.cqc_sender.sendClassical(self.receiver,bytes(cipher.encode()))

	def receive_QOTP_msg(self):
		time.sleep(1)
		cipher=cqc_sender.recvClassical()
		print("cipher received ",cipher)
		plain=otp.decrypt(cipher.decode(),self.private_key)
		print("Msg Received from Bob-> ",plain)
	"""	

def main():
	with CQCConnection("Alice") as Alice:
		
		#msg="Hello"
		#alic.send_QOTP_msg(msg)
		#k=alic.BB84_key()
		
		#log keys 
		while True:
			#alic=BB84_Sender(cqc_sender=Alice,receiver="Bob",hacker="Eve")
			alic=BB84_Sender(cqc_sender=Alice,receiver="Bob")
			key=alic.BB84_key()
		
			msq=input('Alice ->')
			if msq=="exit":
				exit()
 
			cipher=otp.encrypt(msq,key)
			Alice.sendClassical("Bob",bytes(cipher.encode()))

			cipher2=Alice.recvClassical()
			print("cipher received ",cipher2)
			plain=otp.decrypt(cipher2.decode(),key)
			print("Msg Received from Bob-> ",plain)
			time.sleep(5)

		   
	Alice.close()
main()







