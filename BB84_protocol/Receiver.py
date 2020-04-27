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



class BB84_Receiver():
    """
    Author : Mohamed Yassine EL-Ferjani
    All copyrights reserved
    """

    def __init__(self,cqc_receiver,sender,nb_qubits=20):
        self.sender=sender      
        self.raw_key=[]
        self.basis=''
        self.sifted_key=[]
        self.test_indices=[]
        self.test_key=''
        
        #self.error_rate=calcul_error()
        self.nb_qubits=nb_qubits
        
        self.cqc_receiver=cqc_receiver
        self.sender=sender
        

    
    def receive_qubits(self):
        
        for i in range(0,self.nb_qubits):
         c=receive_qubits(self.cqc_receiver)
         #send confirmation to Alice via CAC
         #print("out meas.",c[0])
         self.raw_key.append(c[0])
         self.basis+=str(c[1]) #Bob basis

        self.cqc_receiver.sendClassical(self.sender,len(self.raw_key))
        print("Bob raw key",self.raw_key)
        print("Bob basis",self.basis)
 

        

    

    def sifting(self):
        msg=self.basis.encode()#conversion to byte
        self.cqc_receiver.sendClassical(self.sender,msg)#send basis to Alice
        time.sleep(1)
        rec=self.cqc_receiver.recvClassical()  #receive Alice's sifted basis 
        a_sbasis=comm.bytes_to_list(rec)
    
                
        for i in a_sbasis:
         self.sifted_key.append(int(self.raw_key[i]))
  
        print("Bob sifted key",self.sifted_key)
 
 
    

    def testing(self):
        #time.sleep(1)
        msg1=self.cqc_receiver.recvClassical()
        tested_key_A=comm.bytes_to_list(msg1)
        #print("Alice's tested key received",tested_key_A)
        time.sleep(1)
        msg2=self.cqc_receiver.recvClassical()
        test_indices_A=comm.bytes_to_list(msg2)#test_indices from Alice
        for i in test_indices_A:
         self.test_key+=str(self.sifted_key[i])
  
        print("Bob key for testing",self.test_key)
 

    #def error_correction():

    def privacy_amplification(self):
        self.private_key=''
        
        pk=self.cqc_receiver.recvClassical()
        L=comm.bytes_to_list(pk)
        for i in range(len(L)):
         self.private_key+=str(np.dot(self.sifted_key[i],L[i])%2)
        print("Bob private key :",self.private_key) 
        return self.private_key
    #def calcul_error(self):

    def BB84_key(self):
        self.receive_qubits()
        self.sifting()
        self.testing()
        """
        if self.error_rate >= threshhold:
            print("Error rate {}% | Protocol Aborted!! ".format(self.error_rate))
            exit()
        """ 
        self.privacy_amplification()
        return self.private_key
    """
 
    def receive_QOTP_msg(self):
        time.sleep(1)
        cipher=self.cqc_receiver.recvClassical()
        print("cipher received ",cipher)
        plain=otp.decrypt(cipher.decode(),self.private_key)
        print("Msg Received from Alice-> ",plain)

    def send_QOTP_msg(self,msg):
        cipher=otp.encrypt(msg,self.private_key)
        self.cqc_receiver.sendClassical(self.sender,bytes(cipher.encode()))
     """  

def main():
    with CQCConnection("Bob") as Bob:
        
        
        

        #live encrypted chat
        
      while True:
          
        time.sleep(3)
        print("*******BB84 Protocol***********")
        Bo=BB84_Receiver(cqc_receiver=Bob,sender="Alice")
        key=Bo.BB84_key()
        print("key",key)
        cipher=Bob.recvClassical()
        time.sleep(1)
        print("cipher received ",cipher)
        plain=otp.decrypt(cipher.decode(),key)
        print("Msg Received from Alice-> ",plain)
        msq=input('Bob ->')

        cipher=otp.encrypt(msq,key)
        Bob.sendClassical("Alice",bytes(cipher.encode()))


        


           
            
            
         
    Bob.close()
main()