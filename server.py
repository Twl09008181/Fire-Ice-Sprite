from socket_function import*
from game import*
#server process
if __name__=='__main__':
    is_server = True
    socket_obj = get_socket(is_server)
    MAP = 1
    #MOV[0] 是 p1現在的方向,用來給sender傳給對方
    #MOV[1] 是 對方傳來的資料  有可能是連續的值,像是連續[1,1,1,1,1,1] 因此用list存下
    MOV = [["100","710"],[]]#初始位置 
    STATE = ["LOADING"]
    

    #讓每個thread都使用MOV去做溝通
    t1 = threading.Thread(target = wait_send,args=(socket_obj,MOV,STATE))
    t2 = threading.Thread(target = wait_rec,args=(socket_obj,MOV,STATE))
    t3 = threading.Thread(target = game_logging,args=(is_server,MOV,MAP,STATE))
   
    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    print("end")

