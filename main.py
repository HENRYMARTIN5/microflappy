from machine import Pin,SPI,PWM
import framebuf
import time
import random

BL = 13
DC = 8
RST = 12
MOSI = 11
SCK = 10
CS = 9


class LCDdisplay(framebuf.FrameBuffer):
    def __init__(self):
        self.width = 240
        self.height = 135
        
        self.cs = Pin(CS,Pin.OUT)
        self.rst = Pin(RST,Pin.OUT)
        
        self.cs(1)
        self.spi = SPI(1)
        self.spi = SPI(1,1000_000)
        self.spi = SPI(1,10000_000,polarity=0, phase=0,sck=Pin(SCK),mosi=Pin(MOSI),miso=None)
        self.dc = Pin(DC,Pin.OUT)
        self.dc(1)
        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()
        
        self.red   =   0x07E0
        self.green =   0x001f
        self.blue  =   0xf800
        self.white =   0xffff
        self.black =   0x0000
        
    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""  
        self.rst(1)
        self.rst(0)
        self.rst(1)
        
        self.write_cmd(0x36)
        self.write_data(0x70)

        self.write_cmd(0x3A) 
        self.write_data(0x05)

        self.write_cmd(0xB2)
        self.write_data(0x0C)
        self.write_data(0x0C)
        self.write_data(0x00)
        self.write_data(0x33)
        self.write_data(0x33)

        self.write_cmd(0xB7)
        self.write_data(0x35) 

        self.write_cmd(0xBB)
        self.write_data(0x19)

        self.write_cmd(0xC0)
        self.write_data(0x2C)

        self.write_cmd(0xC2)
        self.write_data(0x01)

        self.write_cmd(0xC3)
        self.write_data(0x12)   

        self.write_cmd(0xC4)
        self.write_data(0x20)

        self.write_cmd(0xC6)
        self.write_data(0x0F) 

        self.write_cmd(0xD0)
        self.write_data(0xA4)
        self.write_data(0xA1)

        self.write_cmd(0xE0)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0D)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2B)
        self.write_data(0x3F)
        self.write_data(0x54)
        self.write_data(0x4C)
        self.write_data(0x18)
        self.write_data(0x0D)
        self.write_data(0x0B)
        self.write_data(0x1F)
        self.write_data(0x23)

        self.write_cmd(0xE1)
        self.write_data(0xD0)
        self.write_data(0x04)
        self.write_data(0x0C)
        self.write_data(0x11)
        self.write_data(0x13)
        self.write_data(0x2C)
        self.write_data(0x3F)
        self.write_data(0x44)
        self.write_data(0x51)
        self.write_data(0x2F)
        self.write_data(0x1F)
        self.write_data(0x1F)
        self.write_data(0x20)
        self.write_data(0x23)
        
        self.write_cmd(0x21)

        self.write_cmd(0x11)

        self.write_cmd(0x29)

    def show(self):
        self.write_cmd(0x2A)
        self.write_data(0x00)
        self.write_data(0x28)
        self.write_data(0x01)
        self.write_data(0x17)
        
        self.write_cmd(0x2B)
        self.write_data(0x00)
        self.write_data(0x35)
        self.write_data(0x00)
        self.write_data(0xBB)
        
        self.write_cmd(0x2C)
        
        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(self.buffer)
        self.cs(1)

class Pipe():
    def __init__(self, length, screenSide):
        self.length = length
        self.screenside = screenSide
        self.posX = 240
        self.active = True
        self.hasBeenPassed = False
        
    def tick(self):
        self.posX -= 10
        if self.posX <= 0 - self.length:
            self.active = False
        
    def checkcollision(self, birdx, birdy, playerScore):
        pipex = self.posX
        pipey = 0
        if self.screenside == 1:
            pipey = 135-self.length
        elif self.screenside == 0:
            pipey = 0
        
        # Get center of bird
        hitX = birdx + 10
        hitY = birdy + 10
        
        # Check if the bird X is within range of the pipe
        if hitX >= pipex and hitX <= (pipex + 40):
            if not self.hasBeenPassed:
                self.hasBeenPassed = True
                playerScore += 1
                
                
            if self.screenside == 0:
                if hitY >= pipey and hitY <= self.length:
                    return [True, playerScore]
            elif self.screenside == 1:
                if hitY >= pipey:
                    return [True, playerScore]
            
        return [False, playerScore]
        
        
        
    def draw(self, LCD):
        if self.screenside == 1:
            LCD.fill_rect(self.posX, 135-self.length, 40, self.length, LCD.green)
        elif self.screenside == 0:
            LCD.fill_rect(self.posX, 0, 40, self.length, LCD.green)
    
def gamefunc(LCD):
    keyA = Pin(15,Pin.IN,Pin.PULL_UP)
    keyB = Pin(17,Pin.IN,Pin.PULL_UP)
    
    key2 = Pin(2 ,Pin.IN,Pin.PULL_UP)
    key3 = Pin(3 ,Pin.IN,Pin.PULL_UP)
    key4 = Pin(16 ,Pin.IN,Pin.PULL_UP)
    key5 = Pin(18 ,Pin.IN,Pin.PULL_UP)
    key6 = Pin(20 ,Pin.IN,Pin.PULL_UP)
    
    playerx=10
    playery=70
    lastInput = False
    pipes = [Pipe(50, 1)]
    game = True
    upGravityFrameCount = 0
    score = 0
    currentGenerationFrame = 0
    createPipeOn = 15
    
    while game:
        LCD.fill(LCD.black)
        
        if currentGenerationFrame >= createPipeOn:
            pipes.append(Pipe(random.randint(25, 50), random.randint(0, 1)))
            currentGenerationFrame = 0
            createPipeOn = random.randint(6, 15)
        else:
            currentGenerationFrame += 1
        
        # Draw player
        if upGravityFrameCount >= 0:
            upGravityFrameCount -= 0.5
            
            playery -= 13 
        else:
            playery += 10
        LCD.fill_rect(playerx,playery,20,20,LCD.red)
        
        # Draw pipes
        i = 0
        for pipe in pipes:
            if pipe.active:
                pipe.tick()
                pipescore = pipe.checkcollision(playerx, playery, score)
                score = pipescore[1]
                if pipescore[0]:
                    game = False
                pipe.draw(LCD)
            else:
                del pipes[i]
            
            i += 1
        
        # Draw Score
        LCD.text('Score: ' + str(score), 10, 10, LCD.white)
        
        LCD.show()
        
        
        if keyA.value() == 0:
            if lastInput == False:
                upGravityFrameCount = 1
            lastInput = True
        else:
            lastInput = False
            
        if playery >= 120:
            game = False
        elif playery <= 0:
            game = False
            

    LCD.text('G A M E   O V E R', 50, 50, LCD.white)
    LCD.text(' imagine losing', 50, 59, LCD.white)
    LCD.text('    Score: ' + str(score), 50, 68, LCD.blue)
    LCD.text('  A to Restart', 50, 90, LCD.white)
    LCD.show()
    
    while 1:
        if keyA.value() == 0:
            break
    gamefunc(LCD)
    

if __name__=='__main__':
    pwm = PWM(Pin(BL))
    pwm.freq(2000)
    pwm.duty_u16(32768)#max 65535

    LCD = LCDdisplay()
    #color BRG
    LCD.fill(LCD.black)
 
    LCD.show()

    gamefunc(LCD)
