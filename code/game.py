import pygame
from pygame.locals import *
from pygame import mixer
import threading
import time
pygame.mixer.pre_init(44100, -16, 2, 512) #加聲音
mixer.init()
jump_fx = pygame.mixer.Sound('./sounds/jump.mp3')
jump_fx.set_volume(0.5)





class World():
    def __init__(self,data,tile_size):
        
        self.tile_list = []
        #load images
        dirt_img = pygame.image.load("./images/dirt.jpg")
        self.dirt_height = dirt_img.get_height () #這個要給vel_y當作一個最大值 不然會穿牆
        print("障礙物厚度= {}".format(dirt_img.get_height ()))#看一下障礙物多厚

        # door_img = pygame.image.load("./images/exit.jpg")
        row_count = 0
        for row in data:
            col_count = 0
            for tile in row:
                if tile == 1: #1代表牆面或地面
                    img = pygame.transform.scale(dirt_img, (tile_size, tile_size))
                    img_rect = img.get_rect()
                    img_rect.x = col_count * tile_size
                    img_rect.y = row_count * tile_size
                    tile = (img, img_rect)
                    self.tile_list.append(tile)                     
                col_count += 1
            row_count += 1

class player(pygame.sprite.Sprite):

    #初始化 視窗大小(邊界條件用),該player出生位置,顏色,速度,P1orP2
    def __init__(self,Boundary,speed,is_P1,character,dirt_height):
        super(player,self).__init__()

        skin_height = 90#自己慢慢量測的
        if character == "Fire":
            Start_Pos = (100,Boundary[1]-skin_height) 
            
        else:#is Ice
            Start_Pos = (100,Boundary[1]-skin_height) 
            
        #loading skin   
        print("Loading skin....")
        
        try:
            path = "./images/" 
            self.jump = [pygame.image.load(path+character+"/Jump{}.png".format(i+1))for i in range(7)]
            self.walkRight = [pygame.image.load(path+character+"/R{}.png".format(i+1))for i in range(6)]
            self.walkLeft = [pygame.image.load(path+character+"/L{}.png".format(i+1))for i in range(6)]
            self.stand=  [pygame.image.load(path+character+"/stand{}.png".format(i+1))for i in range(5)]
            #變形
            for i in range(len(self.jump)):
                self.jump[i] = pygame.transform.scale(self.jump[i], (40, 80))
            for i in range(len(self.walkRight)):
                self.walkRight[i] = pygame.transform.scale(self.walkRight[i], (40, 80))
            for i in range(len(self.walkLeft)):
                self.walkLeft[i] = pygame.transform.scale(self.walkLeft[i], (40, 80))
            for i in range(len(self.stand)):
                self.stand[i] = pygame.transform.scale(self.stand[i], (40, 80))

            self.surf = self.stand[0]
            self.rect = self.surf.get_rect(center = Start_Pos)
        except:
            print("{} create error!".format(character))
            exit()
            
        print("{} create sucess!".format(character))

        print("init {}".format(character))
        #setting basic characteristic
        self.speed = speed
        self.is_P1 = is_P1#用來判斷是Player1 or Player2
        self.moving_state = 0
        #update animation
        self.air_count = 0
        self.stand_count = 0
        self.Left_count = 0
        self.Right_count = 0
        print("init {} sucess!".format(character))


        #gravity
        # self.jump_height = 22
        self.vel_y = 0 #初始化
        self.dirt_height = dirt_height
        self.jumped = False
        #self.is_run_count = 10

        self.delta_x = 0
        self.delta_y = 0
        
    def move(self,pressed_keys,MOV):

        ''' running or jumping action'''
        def running(Direction):
            self.delta_x = 0
            speed = self.speed
            #self.is_run_count = self.is_run_count-1
            #不是剛起跑,速度就要比較快
            # if(self.is_run_count<0):
            #     speed = self.speed*2
            if(Direction=="LEFT"):
                self.delta_x = -speed
            else:    
                self.delta_x = speed            

        if(self.is_P1):#player1
            #如果有奔跑
            if (pressed_keys[K_LEFT] or pressed_keys[K_RIGHT]):
                #左鍵/右鍵兩者可同時觸發,因此要使用if
                if(pressed_keys[K_LEFT]):
                    running("LEFT")
                    self.moving_state = 3
                
                if (pressed_keys[K_RIGHT]):
                    running("RIGHT")
                    self.moving_state = 4

            # # 如果有要觸發跳躍
            if(pressed_keys[K_UP]) and self.jumped==False:
                jump_fx.play()
                self.vel_y = -self.dirt_height
                self.jumped = True
                self.moving_state = 1
            

class GAME():


    def __init__(self,is_server,MOV,Map,data):
        '''初始化才用得到的變數 start'''

        pygame.init()
        Boundary = None   
        map_picture = None
        ''' 聲音'''
        pygame.mixer.music.load('./sounds/BGM.mp3')
        pygame.mixer.music.play(-1, 0.0, 5000)


        print("Map setting.....")
        if(Map==1):#地圖功能,用來配置障礙物跟起始位置 到時候要改這
            map_picture = pygame.image.load("./images/map.jpg")
            Boundary = map_picture.get_size()#根據地圖大小調整
            speed = 8
        Map = pygame.display.set_mode(Boundary)#這邊要先設定mode,不然等等讀取skin會error

        self.tile_size = 50 #一格邊長是50
        self.Boundary = Boundary
        #產生地圖
        self.World = World(data,self.tile_size)
        dirt_height = self.World.dirt_height


        print("player setting.....")
        character1 = "Fire"
        character2 = "Ice"
        if(is_server):
            TITLE = "Fire sprite"
        else:
            TITLE ="Ice sprite"
            character1, character2 = character2, character1
        pygame.display.set_caption(TITLE)
    
        print("player setting.....")
        player1  = None
        player2  = None
        try:    
            player1 = player(Boundary,speed,True,character1,dirt_height)
            player2 = player(Boundary,speed,False,character2,dirt_height)
            #障礙物1 = 障礙物()
        except:
            print("player create error1!")
            exit()
        '''初始化才用得到的變數 end'''



        '''member function要用到的'''
        self.MOV = MOV
        self.MAP = Map
        self.Player = [player1,player2]
        self.map_picture = map_picture
        '''member function要用到的'''

        '''同步p2'''
        self.p2_stand_counter = 0










        self.update_screen()#刷新遊戲畫面

    def update_screen(self):
        self.MAP.fill((255,255,255))
        self.MAP.blit(self.map_picture,(0,0))#載入背景
        
        for tile in self.World.tile_list:
            self.MAP.blit(tile[0], tile[1])

        # #劃格線
        # for line in range(0, 24):
        #     pygame.draw.line(self.MAP, (255, 255, 255), (0, line * self.tile_size), (self.Boundary[0], line * self.tile_size))
        #     pygame.draw.line(self.MAP, (255, 255, 255), (line * self.tile_size, 0), (line * self.tile_size, self.Boundary[1]))





        #重力,會不斷增加p.vel_y的值
        for p in self.Player:
            if p.is_P1 is False:
                p.delta_x = 0
                p.delta_y = 0
                if (self.MOV[1]!=[]):
                    new_pos_x = 0
                    new_pos_y = 0

                    data_length = len(self.MOV[1])//2
                    #print(data_length)
                    
                    i = 0
                    while i < data_length*2:
                        new_pos_x+=int(self.MOV[1][i])
                        new_pos_y+=int(self.MOV[1][i+1])
                        i+=2
                    
                    
                    new_pos_x = new_pos_x//data_length
                    new_pos_y = new_pos_y//data_length
                    #print("new x {} new y{} ".format(new_pos_x,new_pos_y))
                    # if new_pos_x > self.Boundary[0] or  new_pos_x < 0 or y>self.Boundary[1] or y < 0:
                    #     break
                    #print(new_pos)
                    p.delta_x = new_pos_x - p.rect.x
                    p.delta_y = new_pos_y - p.rect.y

                    if p.delta_x > 0:
                        p.moving_state = 4
                    elif p.delta_x <0:
                        p.moving_state = 3 
                    #0由start_game裡面的p.stand_count
                    if p.delta_y != 0:
                        p.moving_state = 1

            p.vel_y += 1
            p.jumped = True #跳躍期間不管怎樣都不給連跳

            if p.vel_y > p.dirt_height:  #vel_y不能無限增長,如果大於障礙物厚度 會直接穿過障礙物往下跑 導致偵測不到碰撞,就會消失在視窗當中,所以這邊設為最大是障礙物厚度
                 p.vel_y = p.dirt_height 
            p.delta_y+= p.vel_y  #y的重力   要靠碰撞偵測才不會往下掉

            #同理 因為按上會跳躍,也不能讓他跳超過障礙物厚度,p.vel_y就會是-dirt_height
            #所以範圍變為-dirt_height(往上最高) ~ dirt_height(往下最高) 
            
            for tile in self.World.tile_list:
                    if tile[1].colliderect(p.rect.x+p.delta_x,p.rect.y,p.surf.get_width(),p.surf.get_height()):
                        p.delta_x = 0

                    #這個if一定會"一直"進去 因為p.vel_y 一定會掃到正的值 導致一直碰撞地板,也因此p.jumped設為False的狀態可以常駐 
                    #進去這裡的兩個原因:1.往上跳撞到天花板  2.站著不動p.vel會一直增加為正值
                    if tile[1].colliderect(p.rect.x,p.rect.y+p.delta_y,p.surf.get_width(),p.surf.get_height()):
                        if  p.vel_y  < 0: #p.vel < 0 若是撞到天花板  不給連跳
                            p.delta_y = tile[1].bottom - p.rect.top     
                            p.vel_y = 0 #其實不加通常不會出事 但為了讓他快速反射 設為0可以幫助加速掉落 取消往上延遲的效果
                        elif p.vel_y>=0: #p.vel >= 0 若是落地,可再次起跳
                            p.delta_y = tile[1].top - p.rect.bottom  
                            '''關鍵是這個p.jump=False'''   
                            p.jumped = False 
                            p.vel_y = 0 #這要不要p.vel_y = 0 跟從高處掉下來的速度多快有關 幾乎沒差


            p.rect.x += p.delta_x
            p.rect.y += p.delta_y


           



            if p.stand_count +1 >=20:
                p.stand_count = 0
            if p.Left_count +1 >=24:
                p.Left_count = 0
            if p.Right_count+1>=24:
                p.Right_count = 0

            if p.air_count+1>=70:#70的配置不錯
                p.air_count = 0
            
            #往上跳
            if p.moving_state == 1:
                self.MAP.blit(p.jump[p.air_count//10],p.rect)
                p.air_count+=1
                p.stand_count = 0
                p.Left_count = 0
                p.Right_count = 0
            #STATE:Left
            elif p.moving_state == 3:
                self.MAP.blit(p.walkLeft[p.Left_count//4],p.rect)
                p.Left_count+=1
                p.stand_count = 0
                p.air_count = 0
                p.Right_count = 0

            #STATE:right
            elif p.moving_state==4:
                self.MAP.blit(p.walkRight[p.Right_count//4],p.rect)
                p.Right_count+=1
                p.stand_count = 0
                p.air_count = 0
                p.Left_count = 0
            #STATE:stand   
            elif p.moving_state==0:
                self.MAP.blit(p.stand[p.stand_count//4],p.rect)
                p.stand_count+=1
                p.air_count = 0
                p.Left_count = 0
                p.Right_count = 0

            

            #pygame.draw.rect(self.MAP, (255, 255, 255), p.rect, 2)  #框線測試用

        if (self.Player[0].delta_x!=0 or self.Player[0].delta_y!=0):
            self.MOV[0] = str(self.Player[0].rect.x)+","+str(self.Player[0].rect.y)+"," 
        else:
            self.MOV[0] = []
        
                  
        self.Player[0].delta_x = 0
        self.Player[0].delta_y = 0 #
        self.Player[1].delta_x = 0
        self.Player[1].delta_y = 0 #
        pygame.display.flip()
         

    def start_game(self,STATE):
        running = True
        pressed_keys = []

     
        while(running):
           
            pygame.time.delay(10)
            for event in pygame.event.get():
                if event.type == QUIT:#這就用滑鼠去關閉視窗
                    running = False
                    STATE[0] = "EXIT"
                    print("quit")
                    print("STATE = {}".format(STATE[0]))
                
               


            pressed_keys = pygame.key.get_pressed()#這個可以讀到鍵盤的值,1是按下去 0是沒按下去

           
            if self.MOV[1]==[]:
                # self.Player[1].moving_state = 0
                if self.p2_stand_counter < 5:#5是手調的
                    self.p2_stand_counter+=1
                else:
                    self.p2_stand_counter = 0
                    self.Player[1].moving_state = 0
                self.update_screen()
            else:
                self.update_screen()
                self.MOV[1] = []
                self.p2_stand_counter = 0


            '''player1的更新'''            
            if(pressed_keys[K_LEFT] or pressed_keys[K_RIGHT] or pressed_keys[K_UP]):
                #pygame.time.delay(10)#delay 0.1秒 這邊可以調到最佳delay
                self.Player[0].move(pressed_keys,self.MOV)
                self.update_screen()
            else:
                self.Player[0].moving_state = 0
                self.MOV[0] = []
                self.update_screen()

  


#其他py檔案要call這個就可以直接用了
def game_logging(is_server,MOV,Map,STATE):

    world_data = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,1,1,1,0,0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1],
    [1,0,0,0,0,0,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,1,1,0,0,0,0,0,0,1,1,1,1,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,1,1,1,1,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1],
    [1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,1,1,1,1,1,1,1,1,1],
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
]


    print("Loading the game setting.....")
    Game = GAME(is_server,MOV,1,world_data)
    print("Loading successful! ")

    #這時候才將STATE打開
    STATE[0] = "RUNNING"
    
    #這邊可以改炫炮一點
    T = 3
    for i in range(T):
        print("倒數{}秒".format(T-i))
        time.sleep(1)
    
    print("start the game!")
    Game.start_game(STATE)



#測試模式
if __name__=='__main__':
    MOV = [["100","710"],["100","710"]]
    STATE = ["LOADING"]
    
    choose = input("enter 1 to choose Fire , 2 to choose Ice\n")

    if(choose=='1'):
        Fireboy = True
    elif(choose=='2'):
        Fireboy = False
    else:
        print("error input ")
        exit()

    game_logging(Fireboy,MOV,1,STATE)



