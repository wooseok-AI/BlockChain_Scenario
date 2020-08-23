import random
from blockchain import Block, BlockChain
from User import Account, PrivateChannel, Miner, Transaction
import json
import hashlib
import time
import numpy as np
random.seed(123)
"""
AdminID : When the game starts, possess all the properties(tokens and equipment)
        게임 시작시 서버내에 존재하는 초기 재화의 양, 아이템의 종류, 양 모두 가지고있음
MinerID : Mining Node sitting outside of the game, only does Mining
        게임 외부의 채굴 노드, 거래 데이터의 갱신이 일정길이를 넘기면 블록을 추가함
UserID_DATA: Assume we have 10 users in the Scenerio, ID is <int>
    현재 시나리오에서는 사용자가 10명으로 가정, 사용자 10명의 ID를 세자리수 <int>로 생성
"""
AdminID = 999
MinerID = 111

UserID = [random.randint(200,800) for i in range(10)] #Create  10 Users randomly
Users = {} #Store User object Userid : <class>account
size = 10
PC = {} #Store every Private channel in storage

#Total Property in Server
Total_Token = 10000000 # 10000000 tokens
Total_Equipment = 1000  # 1000 equipments
# Total_ETC = 10000  

#Creating Admin account, Setting primary numbers of Tokens and Equipments
Admin = Account(AdminID)
Admin.save_Equipment(1000)
# Admin.save_ETC(10000)
Admin.save_Balance(10000000) 


Transactions_que = [] #Temporary Storage for new transactions
# Temporary_que = [] #The transaction will wait till six blocks added 


PrivateChannel_Network = np.zeros((size,size)) #Graph of PrivateChannel among users
PrivateChannel_Network[:][:] = 999
for i in range(size):
    PrivateChannel_Network[i][i] = 0
    
    
#First Transaction of the server is setting the primary properties in Admin account
Base_Trx = Transaction(sender = 000, receiver = AdminID,
                       amount = Total_Token, obj = ['Equipment', Total_Equipment])
Transactions_que.append(Base_Trx)
Transactions_que.append(Admin)
#Block's default setting [Genesis] <- [Admin data]
GameData = BlockChain()
GameData.addBlock(data = Transactions_que)

Transactions_que = []
#Create Miner
Miner = Miner(MinerID, GameData)

def MakeUserAccount(UserID, Users):
    """
    UserID : <int>
    Users : <dict> 
    Returns account (Account object)
    """
    #Make a Account and for the scenario, 
    #Assume every User has 10 equipment and 10000 tokens
    user = Account(UserID)
    user.save_Equipment(100)
    user.save_Balance(10000)
    #stor user object in 'Users' dictionary 
    Users[UserID] = user
    #create Transaction data to store in the block
    trx = Transaction(sender = AdminID,receiver = UserID,amount = 10000, 
                      obj =['Equipment', 10])
    
    return user, trx

def CreatePrivateChannel(Users,u1, u2, a1, a2, i1, i2 ,PrivateChannel_Network,UserID):
    """
    Users : dictionary storing account object
    u1 : UserID of user1
    u2 : UserID of user2
    a1 : User1 amount
    a2 : User2 amount
    i1 : User1 equipment quantity
    i2 : USer2 equipment quantity   """

    
    user1, user2 = Users[u1] , Users[u2] #load user data from User dict
    #if user's properties are not bigger than their comand, block it
    if a1 > user1.balance or a2 > user2.balance or i1 > user1.inventory['Equipment'] or i2 > user2.inventory['Equipment']:
        print('Not enough properties. Not available')
        return None
    
    #data = {'USERID' : AMOUNT of TOKENS,'USERID' : AMOUNT of TOKENS}
    #inventroy ={'USERID' : Quantity of Object, 'USERID' : Quantity of Object}
    data = {u1 : a1, u2 : a2}
    inventory = {u1 : i1, u2: i2}
    #Account.createPC return Private Channel and transaction record
    PC, trx1, trx2 = user1.createPC(data, inventory, user2)
    #If PC already exist, return PC and PCID with empty transactions
    if trx1 ==None and trx2 == None :
        if PC != None:
            return PC, trx1, trx2, PC.id
        else:
            return PC, trx1, trx2, None
    
    PCID = PC.id    
    user1.PC[PCID] = PC
    user2.PC[PCID] = PC
    
    u1_index, u2_index = UserID.index(u1), UserID.index(u2)
    PrivateChannel_Network[u1_index][u2_index] = 1
    PrivateChannel_Network[u2_index][u1_index] = 1

    
    return PC, trx1, trx2, PCID
    
    # if PC1.id == PC2.id:
    #     print('Verified')
    #     return trx1, trx2, PC1.id
    # else:
    #     print('Verification Error')
    #     return False
    
# on(u1, u2, amount, 'Equipment', quantity)
        
        
def ClosePC(Users, u1, PCID, Transactions_que,PrivateChannel_Network,UserID):
    """
    Users : <dict> UserID : Account object
    u1 : userid
    PCID : Private channel ID
    """
    user_account = Users[u1]
    id1, id2 = user_account.PC[PCID].record[0]['u1'] , user_account.PC[PCID].record[0]['u2']
    if id1 == u1:
        partnerid = id2
    else:
        partnerid = id1        
    
    trx1, trx2 = user_account.closePC(PCID, Users[partnerid])
    
    userindex = UserID.index(u1)
    partnerindex = UserID.index(partnerid)
    
    PrivateChannel_Network[userindex][partnerindex] = 999
    PrivateChannel_Network[partnerindex][userindex] = 999
    
    Transactions_que.append(trx1)
    Transactions_que.append(trx2)
    
    

def EmergencyClosing(Users, ExecutorID, OpponentID, Transactions_que,PrivateChannel_Network,UserID):
    temp = sorted([ExecutorID, OpponentID])
    PCID = int(str(temp[0]) + '999' + str(temp[1]))
    executor_index, opponent_index = UserID.index(u1), UserID.index(u2)
    
    PrivateChannel_Network[executor_index][opponent_index] = 999
    PrivateChannel_Network[opponent_index][executor_index] = 999

    Executer, Opponent = Users[ExecutorID], Users[OpponentID]
    trx1, trx2 = Executer.executePC(PCID, Opponent)
    Transactions_que.append(trx1)
    Transactions_que.append(trx2)
    
    
# if Transaction Through the Blockchain used,
# Create Temporary     

def dijkstra(start, size, weight):
    visited = [False]*size
    distance = weight[start]
    visited[start] = True
    
    
    while False in visited:
        
        mindist = float('inf')
        minpos = -1
        
        for i in range(size):
            if visited[i] == False and distance[i] < mindist:
                mindist = distance[i]
                minpos = i
                
        visited[minpos] = True
        
        for j in range(size):
            if visited[j] == False and distance[j] > mindist + weight[minpos][j]:
                distance[j] = mindist + weight[minpos][j]
    
    return distance
       

def ConstructPath(p, i, j):
    i,j = int(i), int(j)
    if(i==j):
      print (i)
    elif(p[i,j] == -30000):
      print (i,'-',j)
    else:
      ConstructPath(p, i, p[i,j]);
      print(j,)


def floyd(a, v, p, start, end):
    for i in range(0,v):
        for j in range(0,v):
            p[i,j] = i
            if (i != j and a[i,j] == 0): 
                p[i,j] = -30000 
                a[i,j] = 30000 # set zeros to any large number which is bigger then the longest way
    
    for k in range(0,v):
        for i in range(0,v):
            for j in range(0,v):
                if a[i,j] > a[i,k] + a[k,j]:
                    a[i,j] = a[i,k] + a[k,j]
                    p[i,j] = p[k,j]
    ConstructPath(p,start,end)
    return p

# p = floyd(PrivateChannel_Network, len(PrivateChannel_Network), np.zeros(PrivateChannel_Network.shape),0,1)
# # show p matrix
# print(p)  

def Scenario1(Users, UserID, u1, u2, amount, obj, quantity, Transactions_que, PrivateChannel_Network, PC):
    """
    Users : <dict> UserID : account object
    UserID : <list> UserID
    u1 : user1 id,     u2 : user2 id
    Transactions_que : <Que> to storage Transactions
    PrivateCahnnel_Network : Status of network of users
    PC: <dict> Public Channel data
    ------------------------------
    if user want low fee transaction, create private channel
    if there is connect lightening network, user can make a deal through it
    in this scenerio, if the distance is 4 (4 channel needed for transaction)
    they will use Lightening network, if longer, they will create new chanel
    """
    
    temp = sorted([u1, u2])
    PCID = PCID = int(str(temp[0]) + '999' + str(temp[1]))
    
    if PCID in Users[u1].PC.keys():
        Users[u1].PC[PCID].Transaction(u1, u2, amount, 'Equipment', quantity)
    else: #최단거리 알고리즘
        u1_index = UserID.index(u1)
        u2_index = UserID.index(u2)
        network = PrivateChannel_Network.copy()
        distance = dijkstra(u1_index, len(UserID),  network)[u2_index]
        print('distance :', distance)
        
        if distance < 4:
            network = PrivateChannel_Network.copy()            
            p = floyd(network, len(PrivateChannel_Network), np.zeros(PrivateChannel_Network.shape),u1_index, u2_index)
            # print(p)
            
            
        else:
            print('making new channel')
            u1_u2_PC, trx1, trx2, PCID = CreatePrivateChannel(Users, u1, u2, 1000, 1000, 5, 5, PrivateChannel_Network,UserID)
            Transactions_que.append(trx1)
            Transactions_que.append(trx2)
            PC[PCID] = u1_u2_PC
            u1_u2_PC.Transaction(u1, u2, amount, 'Equipment', quantity)    
    
        return distance
    
