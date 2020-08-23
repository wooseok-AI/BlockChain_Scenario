import blockchain


class Account():
    def __init__(self, Userid):
        
        self.Userid = Userid
        self.inventory = {'Equipment' : 0} #, 'ETC' : None}
        self.balance = 0        
        self.PC = {}
        
    def save_Equipment(self, quantity):
        """
        quantity : <int> quantity of 'Equipment'
        """
        # Change value of Equipment stored in self.inventory
        self.inventory['Equipment'] += quantity
        
    def save_Balance(self, amount):
        """
        amount : <int> amount of Tokens
        """
        # Change value of balance stored in self.balance
        self.balance += amount
    
    def createPC(self, data, inventory, u2_account): #Create Private Channel
        """
        data = {user1_id : balance, user2_id : balance}
        inventory = {user1id : quantity, user2id : quantity}
        u2_account : <object> u2 account
        """
        #Generate the ID of PC : PCID = (small value id)999(bigger balue id)
        #Needed to be encrypted but for Scenario, Made manually.
        temp = sorted(list(data.keys()))
        PCID = int(str(temp[0]) + '999' + str(temp[1]))
        
        #Check if Private Channel is exist or invalid
        if PCID in self.PC.keys():
            
            #if PC has been closed by 'Emergency Closing' Cannot be created anymore between users
            if self.PC[PCID].record[-1] == 'Executed':
                print("Not availble to create Private Channel : Banned")
                return None, None, None
            
            #if PC already exists, return PC object
            else:
                print('The Channel is already exist')
                return self.PC[PCID], None, None
            
        channel = PrivateChannel(data, inventory)
        
        # Update teh PC data
        self.PC[channel.id] = channel
        u2_account.PC[channel.id] = channel
        
        #When making Channel, changing account's balance and item quantity 
        self.save_Balance(-data[self.Userid]) 
        self.save_Equipment(-inventory[self.Userid])
        u2_account.save_Balance(-data[u2_account.Userid]) 
        u2_account.save_Equipment(-inventory[u2_account.Userid])
        
        #record the initiation situation as record[0]
        #counterparty : player who makes PC with User
        [counterparty] = [counterparty for counterparty in data.keys() if counterparty != self.Userid]
        #counterparty = u2_account.Userid
        
        #Store the log of initiation
        channel.record.append({'id' : len(channel.record),
                              'u1' : self.Userid,
                              'u2' : counterparty,
                              'amount' : data.copy(),
                              'object' : inventory.copy()})
        #To Store in Block Chain, save the transaction log
        Trx1 = Transaction(sender = self.Userid,
                          receiver = channel.id,
                          amount = data[self.Userid],
                          obj = ['Equipment', inventory[self.Userid]])
        
        Trx2 = Transaction(sender = counterparty,
                           receiver = channel.id,
                           amount = data[counterparty],
                           obj = ['Equipment', inventory[counterparty]])
        
        return channel, Trx1, Trx2
    
    def closePC(self, PCID, u2_account, etc = 'Closing'):
        """
        PCID : <int>
        u2_account : <object> 
        etc : The default is 'Closing'.
        """
        #load Private Channel reference
        PC = self.PC[PCID]
        Trx_User1, Trx_User2, trx1, trx2 = PC.CloseChannel(etc)
        #Update user's properties
        if Trx_User1['receiver'] == self.Userid:
            self.balance += Trx_User1['amount']
            self.inventory['Equipment'] += Trx_User1['quantity']
            u2_account.balance += Trx_User2['amount']
            u2_account.inventory['Equipment'] += Trx_User2['quantity']
        #Udate counterparty's properties
        else:
            self.balance += Trx_User2['amount']
            self.inventory['Equipment'] += Trx_User2['quantity']
            u2_account.balance += Trx_User1['amount']
            u2_account.inventory['Equipment'] += Trx_User1['quantity']
        return trx1, trx2
        
    def executePC(self,PCID, u2_account):
        #For Emergency Closing
        PC = self.PC[PCID]
        #Ban the PCID and cannot create anymore
        PC.Execution()
        trx1, trx2 = self.closePC(PCID, u2_account, 'Emergency Closing')
        return trx1, trx2
  
    def accessPC(self, PCID):
        return self.PC[PCID]
    
    
class PrivateChannel():
    """
    need input as dictionary for initiation
    data = {user1id:balance, user2id:balance}
    inventory = {user1id : quantity, user2id : quantity}
    """
    def __init__(self, data, inventory):
        self.data = data
        self.inventory = inventory
        self.id = self.createid()        
        self.record = []
        
    def createid(self):
        #Create PCID 
        temp = sorted(list(self.data.keys()))
        PCID = int(str(temp[0]) + '999' + str(temp[1]))
        return PCID
        
    def CheckBalance(self, Userid):
        return self.data[Userid]    
    
    
    def CheckInventory(self, Userid):
        return self.inventory[Userid]
    
    def showRecord(self):
        return self.record
    
    def Transaction(self, sender, receiver, amount, obj=None, quantity = 0):
        """
        sender : <int> userid : user who sending 'Tokens'
        receiver : <int> userid : user who receiving 'Tokens'
        quantity has to be calculated reversly
        """
        #If there is record The PC has been Executed, no longer available
        if self.record[-1] == 'Executed':
            print('This Private Channel is no longer available')
            return False
        
        #Change the amount of data
        self.data[sender] -= amount
        self.data[receiver] += amount
        
        #Change the quantity of Inventory
        if obj != None:
            self.inventory[sender] += quantity
            self.inventory[receiver] -= quantity
        
        #Status after Transaction
        status = {'id' : len(self.record),
                  'u1' : self.record[0]['u1'],
                  'u2' : self.record[0]['u2'],
                  'amount' : self.data.copy(),
                  'object' : self.inventory.copy()}
        #transaction data occured status change
        trx_record = {len(self.record) : 'transaction_record',
                  'sender' : sender,
                  'receiver' : receiver,
                  'amount' : amount,
                  'object' : [obj,quantity]}
        
        #update PC record
        self.record.append([status, trx_record])
        
        
    def CloseChannel(self, etc = None):
        #PCID = (small value id)999(bigger balue id)
        User1 = self.id//1000000
        User2 = self.id%1000
        
        #Create Transaction data to empty PC
        Trx_User1 = Transaction(sender=self.id, 
                                receiver = User1,
                                amount = self.data[User1],
                                obj = ['Equipment', self.inventory[User1]],
                                etc = etc)
        Trx_User2 = Transaction(sender = self.id,
                                receiver = User2,
                                amount = self.data[User2],
                                obj = ['Equipment', self.inventory[User2]],
                                etc = etc)
        
        self.data[User1] = 0
        self.data[User2] = 0
        self.inventory[User1] = 0
        self.inventory[User2] = 0
        
        return vars(Trx_User1), vars(Trx_User2), Trx_User1, Trx_User2
    
    def Execution(self):
        #Roll back to initiation data
        initiation_log = self.record[0]
        self.data = initiation_log['amount']
        self.inventory = initiation_log['object']
        
        execution_log = self.record[0].copy()
        execution_log['id'] = len(self.record)
        
        self.record.append(execution_log)
        self.record.append('Executed')
        

class Miner():
    """
    miner does the adding blocks
    
    """
    def __init__(self, Userid, BlockChain):
        self.Userid = Userid
        self.chain = BlockChain
        
    def mining(self, transactions):
        proof, block = self.chain.addBlock(data = transactions)
        transactions = []
        if self.chain.isValid():
            return self.spread(self.chain) , transactions
        else:
            return False    
    def spread(self, new_chain):
        print('-------------------')
        print('Spreading New Chain')
        print('-------------------')

        return new_chain
       
"""
transaction = {'sender' : <int> userid1,
               'receiver' : <int> userid2,
               'amount' : <int>,
               'object' : [item, quantity]}
"""
class Transaction():
    def __init__(self, sender, receiver, amount = None, obj = [None, None], etc = None):
        self.sender = sender
        self.receiver = receiver
        self.amount = amount
        self.object = obj[0]
        self.quantity = obj[1]      
        self.etc = etc
        

class key():
    def __init__(self):
        pass
    
    
if __name__ == '__main__':
    u1 = Account(123)
    u2 = Account(456)
    u1.save_Equipment(10)
    u2.save_Equipment(10)
    u1.save_Balance(1000)
    u2.save_Balance(1000)
    data = {u1.Userid :  250, u2.Userid :  500}
    inventory = {u1.Userid : 2 , u2.Userid : 5}
    u1_u2_pc, tx1, tx2 = u1.createPC(data, inventory)
    PC = {}
    PC[u1_u2_pc.id] = u1_u2_pc