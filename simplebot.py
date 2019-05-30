import discord
from importlib import import_module, reload
import os 

class Bot(discord.Client):

    def __init__(self):
        self._bltList = {}
        self._builtin()
        self.pref = str()
        ModMgr.getInst()
        assert ModMgr is not None
        return super().__init__()
        

    async def on_ready(self):
        """
        before getting into main loop
        implement this function
        """
        print('Logged on as {0}!'.format(self.user))
        assert ModMgr.getInst() is not None

    async def on_message(self, msg):
        """
        if msg mentioned this bot,
            check if msg called builtin function
                if msg called builtin function
                     call the function here
        otherwise pass msg to mods through
        loop with msg through mod lists
            pass mod over msgs
            if mod returns true
                end this function here
        """
        #ignore bot msg
        if self.user == msg.author :
            return
        #check who mentioned this bot
        
        mention = str()
        if msg.guild.get_member(self.user.id).nick is None :
            mention = "<@{}>".format(self.user.id)
        else :
            mention = "<@!{}>".format(self.user.id)
        if msg.content.startswith(mention) :
            cmd = str.lstrip(msg.content[len(mention):]).split()[0]
            if cmd in self._bltList :
                await self._bltList[cmd](self,msg)
            return
        assert len(self.pref)>0 and self.pref != ' '
        #district channels
        if msg.content.startswith(self.pref) is False :
            return
        ModMgr.msgProc(self,msg)
        pass

    def getPref(self): return self.pref

    def _builtin(self):
        async def loadMod(bot, msg):
            mention = str()
            if msg.guild.get_member(self.user.id).nick is None :
                mention = "<@{}>".format(self.user.id)
            else :
                mention = "<@!{}>".format(self.user.id)
            line = msg.content[len(mention):].split()
            #cmd = line[0]
            args = line[1:]
            for i in args :
                if ModMgr._isloaded(i) :
                    await msg.channel.send("already loaded module {}".format(i))
                    return
                if ModMgr.loadMod(i):
                    await msg.channel.send("succeed to load {}".format(i))
                else :
                    await msg.channel.send("failed to load {}".format(i))
            pass
        self._bltList['load'] = loadMod

        async def unloadMod(bot,msg):
            #core Proc
            mention = '<@!{}>'.format(self.user.id)
            line = msg.content[len(mention):].split()
            #cmd = line[0]
            args = line[1:]
            #if msg had modname check if modlist has this name
            for i in args :
                if ModMgr.unloadMod(i) :
                    await msg.channel.send("unloaded Module:{}".format(i))
                else :
                    await msg.channel.send('i could not find module:{}'.format(i))
            pass
        self._bltList['unload'] = unloadMod

        async def setPref(bot,msg):
            pass

        async def debug(bot,msg):
            print(msg)
            print(msg.content)
        self._bltList['debug'] = debug

        async def show(bot,msg):
            async for i in msg.channel.history(limit=20):
                print(i.content)
                print(i.attachments)
                for a in i.attachments :
                    print(a.height , end = '\t')
                    print(a.width, end = '\t')
                    print(a.proxy_url)
        self._bltList['logs'] = show

        async def imgdown(bot,msg):
            async for m in msg.channel.history(limit=20):
                if len(m.attachments) > 0 :
                    for a in m.attachments :
                        if a.height is not None and a.width is not None :
                            ext = 0
                            for i in range(len(a.filename)) :
                                if a.filename[-(i)] == '.' :
                                    ext = i
                            fn = 'sample' + a.filename[-ext:]
                            file = os.path.join(os.getcwd(),'attach',fn)
                            os.access(file,mode = os.W_OK)
                            await a.save(file, use_cached=True)
                            return
        self._bltList['down'] = imgdown

        async def modList(bot,msg):
            moddir = os.path.join(os.getcwd(),'modules')
            files = []
            for f in os.listdir(moddir) :
                if f.startswith('__') is False and f.endswith('.py'):
                    files.append(f)
                    await msg.channel.send(f)
            await msg.channel.send(files) #fix with embed
            pass
        self._bltList['modfiles'] = modList
        
        async def modView(bot,msg):
            for mod in bot.mList :
                txt = mod.name + ' : '
                for i in mod.getEvents():
                    txt += i
                    txt += ', '
                txt = txt.rstrip(', ')
                await msg.channel.send(txt)
        #self._bltList['modlist'] = modView
        pass

class ModMgr:
    _instance = None
    mDir ='modules'

    def __init__(self):
        self.mods = []
        self.loaded = []

    @classmethod
    def getInst(cls):
        if cls._instance is None :
            cls._instance = ModMgr()
        return cls._instance

    @classmethod
    def loadMod(cls,modName):
        files = os.listdir( os.path.join(os.getcwd(),ModMgr.mDir))
        #if file exist, check this file has syntax error
        if '{}.py'.format(modName) in files :
            if not modName in ModMgr.getModList() :
                try :
                    mInst = import_module('.{}'.format(modName),ModMgr.mDir)
                    if ModMgr._isloaded(modName):
                        mInst = reload(mInst)
                    m = mInst.connect()
                    m.setModule(modName, mInst)
                    ModMgr._addMod(m)
                    return True
                except SyntaxError as e:
                    print("syntax")
                    print(e)
                    return False
                except :
                    print("unknown")
                    return False
            else : 
                print('already loaded module name')
                return False
        else :
            print('no file')
            return False

    @classmethod
    def unloadMod(cls,modName):
        for mod in cls.getModList() :
            try :
                if mod == modName :
                    ModMgr.getModList().remove(mod)
                    del mod
                    return True
            except ValueError as e:
                print('no value in list')
                print(e)
                return False
            except :
                print('unknown')
        print('have not loaded yet')
        return False

    @classmethod
    def getModList(cls):
        return cls._instance.mods

    @classmethod
    def _addMod(cls,module) : 
        assert module is not None
        cls._instance.mods.append(module)
        cls._instance.loaded.append(module.name)

    @classmethod
    def _isloaded(cls,modName) :
        if modName in cls._instance.loaded :
            return True
        else :
            return False

    @classmethod
    async def msgProc(cls,bot,msg):
        for mod in mods :
            result = await mod.modProc(bot,msg)
            if result is True :
                return mod
        return False