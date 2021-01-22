import threading
import socket
import sys
import pygame
import time
def wait_send(sock,MOV,STATE):
    
    while(STATE[0]!="RUNNING"):#防止占用CPU
        print("state = {} ".format(STATE[0]))
        time.sleep(3)
        
    print("state = {} ".format(STATE[0]))
    while(STATE[0]!="EXIT"):
        try:
            #這邊幾乎是一次送一筆(因為Player1的進行速度很快)
            
            if(MOV[0]!=[]):#這拿掉絕對出事 電腦直接毀滅(收方扛不住)
                sock.send("".join(MOV[0]).encode())
                #print("".join(MOV[0]))
                #print("sender send {} ".format("".join(MOV[0])))
                MOV[0] = []  #由sender清空
                
        except:
            #print("WAIT RECVER")
            pass
            
            



#這邊特別難
def wait_rec(sock,MOV,STATE):
    
    while(STATE[0]!="RUNNING"):#防止占用CPU
        #print("state = {} ".format(STATE[0]))
        time.sleep(3)
        
    
    print("state = {} ".format(STATE[0]))
    while(STATE[0]!="EXIT"):
        try:
            if  MOV[1]==[]:#lock機制 一定要等player2的掃描過了才讀 盡量錯開
                MOV[1] = sock.recv(4096).decode('utf-8').split(",")
                #print("recv : {}".format(MOV[1]))
           
        except:
            #print("WAIT SENDER")
            pass
         
         

def get_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect( ( "www.google.com", 80 ) )
    #把這個PORT設定為可以重複用
    s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
    (IP,PORT) = s.getsockname()
    s.close()
    return (IP,PORT)

def get_socket(is_server):
    socket_obj = None
    S = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if (is_server):
        (HOST,PORT) = get_port()
        print("server's ip : {}  Port : {}".format(HOST,PORT))
        print("copy this to client : {},{}".format(HOST,PORT))
        S.bind((HOST, PORT))
        S.listen(1)
        conn, addr = S.accept()
        socket_obj = conn
    else:
        addr = input("enter HOST,PORT").split(",")
        HOST = addr[0]
        PORT = int(addr[1])
        S.connect((HOST,PORT))
        socket_obj = S

    print("successfully connect to {}".format(socket_obj.getpeername()))
    
    socket_obj.settimeout(1)#設定time out 才不會看不到STATE[0] = "EXIT"

    return socket_obj
