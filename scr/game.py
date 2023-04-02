import pyxel
from os import getcwd
from os.path import join, pardir

'''
States
0 : Title Screen
1 : Game
2 : Game Over Screen
3 : Wining Screen
4 : How To Play
'''

class Player:
    def __init__(self, x, y) -> None:
        self.x = x*8
        self.y = y*8
        self.vel = 0.5
        self.w = 8
        self.h = 8
        self.u = 8
        self.v = 0
        self.img = 0
        self.alpha = 0
        self.hold = 1# Hold button event is apply after n frames
        self.repeat = 1# Hold button event is repeated after n frames
        self.imgs = [1*8, 2*8]
        self.walking = False
        self.water = 10
        self.waterMax = 10
        self.loseRate = 100
        self.heat = 0
        self.win = False
        self.map = 2

    def checkCollitions(self, newX, newY, tiles):
        left = newX // 8
        right = (newX + self.w) // 8
        up = newY // 8
        down = (newY + self.h) // 8
        
        if pyxel.tilemap(self.map).pget(left, up) in tiles:
            return True
        if pyxel.tilemap(self.map).pget(right, up) in tiles:
            return True
        if pyxel.tilemap(self.map).pget(left, down) in tiles:
            return True
        if pyxel.tilemap(self.map).pget(right, down) in tiles:
            return True
        
        return False
    
    def update(self):
        if self.heat >= self.loseRate:
            self.water -= 1
            self.heat = 0

        if self.checkCollitions(self.x, self.y, [(3,0), (3,1)]):
            self.win = True

        elif self.checkCollitions(self.x, self.y, [(0,4)]):
            self.heat += 2

        elif self.checkCollitions(self.x, self.y, [(1,3)]):
            self.heat -= 0.9

        newY = self.y
        newX = self.x
        self.walking = False

        if pyxel.btnp(pyxel.KEY_UP, hold=self.hold, repeat=self.repeat):
            newY -= self.vel
            self.walking = True
        if pyxel.btnp(pyxel.KEY_DOWN, hold=self.hold, repeat=self.repeat):
            newY += self.vel
            self.walking = True
        
        if not self.checkCollitions(self.x, newY, [(0,2), (1,2), (2,2), (3,2), (4,2), (5,2), (6,2), (7,2)]):
            self.y = newY

        if pyxel.btnp(pyxel.KEY_LEFT, hold=self.hold, repeat=self.repeat):
            newX -= self.vel
            self.walking = True
        if pyxel.btnp(pyxel.KEY_RIGHT, hold=self.hold, repeat=self.repeat):
            newX += self.vel
            self.walking = True
        
        if not self.checkCollitions(newX, self.y, [(0,2), (1,2), (2,2), (3,2), (4,2), (5,2), (6,2), (7,2)]):
            self.x = newX
        
        self.heat += 1

    def draw(self):
        # Animate
        if self.walking:
            self.u = self.imgs[(pyxel.frame_count//10)%2]

        # Draw Player
        pyxel.blt(round(self.x), round(self.y),# Pos x, y
                  self.img,# Img
                  self.u, self.v,# x, y relative to Img
                  self.w, self.h,# w, h
                  self.alpha)#Color key

class Water:
    def __init__(self, x, y) -> None:
        self.x = x*8
        self.y = y*8
        self.w = 8
        self.h = 8
        self.u = 0
        self.v = 1*8
        self.img = 0
        self.imgs = [0, 1*8]
        self.alpha = 0
        self.tile = (x, y)

    def checkCollitions(self, pX, pY, pW, pH):
        left = pX // 8
        right = (pX + pW) // 8
        up = pY // 8
        down = (pY + pH) // 8
        
        if (left, up) == self.tile:
            return True
        if (right, up) == self.tile:
            return True
        if (left, down) == self.tile:
            return True
        if (right, down) == self.tile:
            return True
        
        return False
    
    def draw(self):
        # Animate
        self.u = self.imgs[(pyxel.frame_count//20)%2]

        # Draw Water
        pyxel.blt(round(self.x), round(self.y),# Pos x, y
                  self.img,# Img
                  self.u, self.v,# x, y relative to Img
                  self.w, self.h,# w, h
                  self.alpha)#Color key

class Game:
    def __init__(self) -> None:
        
        sw, sh = 1920, 1080
        scale = 10
        w, h = sw//scale, sh//scale
        #w, h = 192, 108
        
        self.state = 0
        self.ix = 59
        self.iy = 43
        self.player = Player(self.ix, self.iy)
        self.hold = 1# Hold button event is apply after n frames
        self.repeat = 1# Hold button event is repeated after n frames
        self.camX = self.player.x - w//2
        self.camY = self.player.y - h//2
        self.camV = 1
        self.map = 2
        self.sunState = 0
        self.sunStateMax = 500
        self.water = []
        self.mapW = 96
        self.mapH = 80
        self.waterMax = 50

        pyxel.init(w, h, title="The Almighty Sun", fps=60, display_scale=7, capture_scale=1, capture_sec=5)
        
        assetsPath = join(getcwd(), pardir, "assets", "assets.pyxres")
        pyxel.load(assetsPath)
        pyxel.playm(0, loop=True)
        self.modMap()

    def modMap(self):
        [self.createMap(0, i+1) for i in range(7)]
        self.addShadows(4, 5, 2, 1)
        self.addShadows(4, 6, 4, 1)
        self.addShadows(4, 7, 6, 1)
        self.addShadows(4, 3, 2, -1)
        self.addShadows(4, 2, 4, -1)
        self.addShadows(4, 1, 6, -1)
        
    def addShadows(self, tileMapScr, tileMapDest, level, side):
        w = self.mapW
        h = self.mapH

        for x in range(w):
            for y in range(h):
                tile = pyxel.tilemap(tileMapScr).pget(x, y)
                self.createShadow(tile, level, side, tileMapDest, x, y)

    def createShadow(self, tile, n, side, tileMap,x ,y):
        walls = {(0,2), (2,2)}
        if tile in walls:
            for i in range(n):
                xx, yy = x+(i + 1)*side, y
                otherTile = pyxel.tilemap(tileMap).pget(xx, yy)
                #if otherTile not in walls:
                shadowTile = self.getShadowTile(otherTile)
                pyxel.tilemap(tileMap).pset(xx, yy, shadowTile)

    def getShadowTile(self, tile):
        re = tile
        if tile == (0, 4):
            re = (1,4)
        elif tile == (0, 3):
            re = (1,3)
        elif tile == (0, 2):
            re = (1,2)
        elif tile == (2, 2):
            re = (3,2)
        elif tile == (3, 0):
            re = (3,1)
        
        return re

    def getLightTile(self, tile):
        re = tile
        if tile == (1, 4):
            re = (0,4)
        elif tile == (1, 3):
            re = (0,3)
        elif tile == (1, 2):
            re = (0,2)
        elif tile == (3, 2):
            re = (2,2)
        elif tile == (3, 1):
            re = (3,0)
        
        return re

    def createMap(self, tileMapScr, tileMapDest):
        w = self.mapW
        h = self.mapH

        for x in range(w):
            for y in range(h):
                tile = pyxel.tilemap(tileMapScr).pget(x, y)
                newTile = self.getLightTile(tile)
                pyxel.tilemap(tileMapDest).pset(x, y, newTile)

    def run(self):
        pyxel.run(self.update, self.draw)

    def addWater(self, n, tol = 1000):
        self.water = []
        posL = set()
        posiblePos = [(0,3),(0,4),(1,3),(1,4)]
        i = 0
        #for i in range(n):
        while len(posL) < n and i < tol:
            i += 1
            posX = pyxel.rndi(0, self.mapW)
            posY = pyxel.rndi(0, self.mapH)
            posM = pyxel.tilemap(0).pget(posX,posY)

            if (posX, posY) not in posL and posM in posiblePos:
                self.water.append(Water(posX, posY))
                posL.add((posX, posY))

    def drawTitle(self):
        pyxel.camera()
        pyxel.cls(0)
        pyxel.blt(0, 0,# Pos x, y
                   1,# Img
                   0, 0,#  x, y relative to Tile
                   192, 108)# w, h
        pyxel.rect(6,79,69,20,5)
        pyxel.text(7,80, "Press:\nSPACE to play\nUP to How to Play", 0)

    def updateTitle(self):
        if pyxel.btnr(pyxel.KEY_SPACE):
            self.state = 1
            self.player.water = self.player.waterMax
            self.player.x = self.ix*8
            self.player.y = self.iy*8
            self.camX = self.player.x - pyxel.width//2
            self.camY = self.player.y - pyxel.height//2
            if self.player.win:
                pyxel.stop(3)
                pyxel.playm(0, loop=True)
            self.player.win = False
            self.sunState = 0
            self.map = 0
            self.player.map = 0
            self.addWater(self.waterMax)

        elif pyxel.btnr(pyxel.KEY_UP):
            self.state = 4
   
    def drawHowToPlay(self):
        pyxel.camera()
        pyxel.cls(0)
        pyxel.blt(0, 0,# Pos x, y
                   2,# Img
                   0, 0,#  x, y relative to Tile
                   192, 108)# w, h
        text = ["Move with the arrows",
                "Find the RADIO to escape the desert",
                "Watch your WATER LEVEL",
                "It will drop down with time",
                "Stay in the shadows to slow it down",
                "Drink WATER will raise it",
                "\nPress DOWN to return"]
        pyxel.text(25,10, "\n\n".join(text), 0)
        #Water
        pyxel.blt(130, 69,# Pos x, y
                   0,# Img
                   0, 8,#  x, y relative to Tile
                   8, 8,
                   0)
        #WinCon
        pyxel.blt(170, 21,# Pos x, y
                   0,# Img
                   3*8, 0,#  x, y relative to Tile
                   8, 8, 15)# w, h
        #Water bar
        pyxel.blt(115, 32,# Pos x, y
                   0,# Img
                   4*8, 0,#  x, y relative to Tile
                   3*8, 8,# w, h
                   0)

    def updateHowToPlay(self):
        if pyxel.btnr(pyxel.KEY_DOWN):
            self.state = 0

    def drawGameOver(self):
        pyxel.camera()
        pyxel.cls(0)
        pyxel.camera()
        pyxel.cls(0)
        pyxel.blt(0, 0,# Pos x, y
                   2,# Img
                   0, 0,#  x, y relative to Tile
                   192, 108)# w, h
        text = "The Almighty Sun has\nclaimed another victim.\n\nPress SPACE to Restart"
        pyxel.text(40, 20, text, 0)
    
    def updateGameOver(self):
        if pyxel.btnr(pyxel.KEY_SPACE):
            self.state = 0
    
    def drawGameWin(self):
        pyxel.camera()
        pyxel.cls(0)
        pyxel.blt(0, 0,# Pos x, y
                   2,# Img
                   0, 0,#  x, y relative to Tile
                   192, 108)# w, h
        text = "Congratulations.\n\nYou have escaped from\nThe Almighty Sun.\n\nPress SPACE to Restart"
        pyxel.text(40, 20, text, 0)
    
    def updateGameWin(self):
        if pyxel.btnr(pyxel.KEY_SPACE):
            self.state = 0
    
    def moveCam(self):
        # Move the Camera
        limX = 8*5
        limY = 8*2

        dx = round(self.player.x) + self.player.w//2 - pyxel.width//2 - self.camX
        dy = round(self.player.y) + self.player.h//2 - pyxel.height//2 - self.camY
        if abs(dx) > limX:
            self.camX += self.camV * dx/abs(dx)

        if abs(dy) > limY:
            self.camY += self.camV * dy/abs(dy)
        
        pyxel.camera(round(self.camX), round(self.camY))

    def drawWaterLevel(self, level, state):
        # Draw Water Level
        pyxel.blt(self.camX + 4 + 8*level, self.camY + 4,# Pos x, y
                  0,# Img
                  (4 + state)*8, 0,# x, y relative to Img
                  8, 8,# w, h
                  0)#Color key  

    def drawGame(self):
        self.moveCam()
        pyxel.cls(0)
        
        pyxel.bltm(0, 0,# Pos x, y
                   self.map,# Tile
                   0, 0,#  x, y relative to Tile
                   8*self.mapW, 8*self.mapH,# w, h
                   0)#Color key
        
        for w in self.water:
            w.draw()
        
        # Draw Player
        self.player.draw()

        for i in range(self.player.waterMax//2):
            if self.player.water/2 > i:
                if self.player.water/2 >= i + 1:
                    self.drawWaterLevel(i, 0)
                else:
                    self.drawWaterLevel(i, 1)
            else:
                self.drawWaterLevel(i, 2)

    def updateGame(self):     
        if self.sunState >= self.sunStateMax:
            newMap = (self.map + 1)%8
            self.map = newMap
            self.player.map = newMap
            self.sunState = 0
        
        for w in self.water[:]:
            if w.checkCollitions(self.player.x, self.player.y, self.player.w, self.player.h):
                if self.player.water < self.player.waterMax:
                    self.player.water += 1
                    self.player.heat = 0
                    self.water.remove(w)
                    pyxel.play(3, 5)

        #Update Player
        self.player.update()

        if self.player.water < 0:
            self.state = 2
            pyxel.play(3, 7)
        
        if self.player.win:
            self.state = 3
            pyxel.stop(0)
            pyxel.stop(1)
            pyxel.play(3, 6)
        
        self.sunState += 1

    def draw(self):
        match self.state:
            case 0:
                self.drawTitle()
            case 1:
                self.drawGame()
            case 2:
                self.drawGameOver()
            case 3:
                self.drawGameWin()
            case 4:
                self.drawHowToPlay()

    def update(self):
        match self.state:
            case 0:
                self.updateTitle()
            case 1:
                self.updateGame()
            case 2:
                self.updateGameOver()
            case 3:
                self.updateGameWin()
            case 4:
                self.updateHowToPlay()


if __name__ == "__main__":
    myGame = Game()
    myGame.run()
