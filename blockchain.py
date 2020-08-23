import hashlib
import time
import json

class Block():
    def __init__(self, index, timestamp, data, previousHash = None):
        self.index = index #블록의 인덱스
        self.timestamp = timestamp 
        self.data = data #data contain in Block(이경우에는 Transaction과 유저데이터)
        self.previousHash = previousHash #previous Hash
        self.nonce = 0 #Nonce
        self.hash = self.generate_hash() 
        
    def generate_hash(self):
        #making hash
        return hashlib.sha256(str(self.index).encode() + 
                              str(self.data).encode() + 
                              str(self.timestamp).encode() + 
                              str(self.nonce).encode() +
                              str(self.previousHash).encode()).hexdigest()
    
    def POW(self, difficulty): #Proof of Work
        target = '0' * difficulty 
        proof = self.generate_hash()
        
        while (proof[:difficulty] != target):
            self.nonce +=1
            proof = self.generate_hash()
        
        return proof
            
        
class BlockChain:
    def __init__(self, difficulty = 3):
        self.chain = [] 
        self.difficulty = difficulty
        self.createGenesis() #When initiate, Create first block as Genesis Block
        
        
    def createGenesis(self):
        self.chain.append(Block(0,time.time(), 'Genesis'))
        
    def addBlock(self, data):
        #Add block with POW
        previous_block_hash = self.chain[len(self.chain)-1].hash
        #Create New Block
        new_block = Block(index = len(self.chain), previousHash=previous_block_hash,
                          timestamp= time.time(),data = data)  
        #By POW find previous hash by inserting nonce value
        proof = new_block.POW(self.difficulty)
        new_block.hash = new_block.generate_hash()
        self.chain.append(new_block)
        return proof, new_block
    
    def isValid(self):
        #Find out whether BlockChain is valid
        #If the data has been changed, return False, otherwise return True
        i = 1
        while(i < len(self.chain)):
            if(self.chain[i].hash != self.chain[i].generate_hash()):
                return False
            if(self.chain[i].previousHash != self.chain[i-1].hash):
                return False
            i+=1
        return True
    
    
    
if __name__ == "__main__":
    onion = BlockChain()
    onion.addBlock(data = "WOW")
    print(json.dumps(vars(onion.chain[0]), indent = 4))
    print(json.dumps(vars(onion.chain[1]), indent = 4))
    print(onion.isValid())
    
