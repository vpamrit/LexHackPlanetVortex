import pygame
from pygame.locals import *
import sys
import time
import math
import pyganim

pygame.init()


#--------Variable Declarations--------------#

MAX_X = 800
MAX_Y = 640
  
# set up the colors
BLACK = (  0,   0,   0)
WHITE = (255, 255, 255)
RED   = (255,   0,   0)
GREEN = (  0, 255,   0)
BLUE  = (  0,   0, 255)
mainClock = pygame.time.Clock()
BGCOLOR = (100, 50, 50)

beginning_time = time.time()
Surface = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption('Planet Vortex')
line_coords = [ [[0,0],[0,0],[0]] , [[0,0],[0,0],[0]] , [[0,0],[0,0],[0]] , [[0,0],[0,0],[0]] , [[0,0],[0,0],[0]] ]
#-------------------------------------------#


#---------Helper Functions -----------------#
def CoordtoDeg(x,y):
    if(x>0 and y<0):
         return 360.0 + math.degrees(math.atan(y/x))
    elif(x<0 and y>0):
         return 180.0 + math.degrees(math.atan(y/x))
    elif(x<0 and y<0):
         return 180.0 + math.degrees(math.atan(y/x))
    elif(x>0 and y>0):
         return  math.degrees(math.atan(y/x))
    elif(x==0 and y>0):
         return 90.0
    elif(x==0 and y<0):
         return 270.0
    elif(y==0 and x<0):
         return 180.0
    elif(y==0 and x>0):
         return 0.0

def returnSign(x):
    return x/abs(x+sys.float_info.epsilon)-sys.float_info.epsilon
def DegtoRad(angle):
    return angle/180.0*math.pi
def ConvertCoord(x,y):
    return [x+400, -1*y +320]
def rot_center(image, angle):
    """rotate an image while keeping its center and size"""
    orig_rect = image.get_rect()
    rot_image = pygame.transform.rotate(image, angle)
    rot_rect = orig_rect.copy()
    rot_rect.center = rot_image.get_rect().center
    rot_image = rot_image.subsurface(rot_rect).copy()
    return rot_image
def mag(x,y):
    return math.sqrt(x*x+y*y)
def dist(p1, p2):
    return math.sqrt( (p2[1]-p1[1])**2 + (p2[0]-p1[0])**2)
def findSlope(line):
    if((line[0][0]-line[1][0]) == 0):
        return 1000.0
    slope =  float(line[0][1]-line[1][1])/(line[0][0]-line[1][0])
    return slope
def keepAngleInRange(angle):
    return angle%360
#-------------------------------------------#
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, r, angle):
        pygame.sprite.Sprite.__init__(self)
        self.gaccel=0.05 #gravitational acceleration constant
        self.x = x
        self.y = y
        self.r = r
        self.dx = dx
        self.dy = dy
        self.totalr = earth.r + r
        self.FIRSTTOUCH=True
        self.angle = 20
        self.speed = 0
        self.gspeed=0
        self.draw_width = 4
        self.stop = 1
        self.Aangle = 0
        self.Vangle = 0
        self.collide =[False, 0]
        self.ddr = 0
        self.dr = -.1 #this is essentially gravity
    def draw(self):#WORKING
        pygame.draw.circle(Surface, BLACK, ConvertCoord((int)(self.x),(int)(self.y)), (int)(self.r),self.draw_width)
    def grav(self):#IMPLEMENT TAKE OFF
        if(self.totalr>160):
            self.totalr += self.dr
            self.ddr = -.0005
        else:
            self.ddr = 0
            self.dr = -.1
        self.dr+= self.ddr
    def move(self, earthobj, lines):
        self.clickRotate()
        #self.applyearthspeed()
        #print self.Aangle
        self.applyAndSlow(1.012, line_coords)
        self.grav()
        
        
            
    def clickRotate(self):
        key=pygame.key.get_pressed()
        if(self.totalr < earth.r + self.r+2):
            if(key[K_RIGHT] and self.Aangle >-0.05):
                self.Aangle -= 0.000035
            if(key[K_LEFT]and self.Aangle <0.05):
                self.Aangle += 0.000035
                
    def applyAndSlow(self, slow_constant, lines):
        if((self.Vangle>-0.5 and self.Aangle<0) or (self.Vangle<0.5 and self.Aangle>0)):
            self.Vangle+=self.Aangle
        
        self.barrierCollision(lines)#BARRIER COLLIDE PROBLEM
        self.angle += self.Vangle
        self.Vangle = self.Vangle/slow_constant
        self.Aangle = self.Aangle/slow_constant
        key=pygame.key.get_pressed()
        
        if(key[K_SPACE]):#works
            self.angle = CoordtoDeg(pygame.mouse.get_pos()[0]-400.0,-1.0*(pygame.mouse.get_pos()[1]-320.0))
            self.totalr = mag(pygame.mouse.get_pos()[0]-400.0,-1.0*(pygame.mouse.get_pos()[1]-320.0)  )
            
        self.x = self.totalr*math.cos(DegtoRad(self.angle)) #calculate coordinates using angles
        self.y = self.totalr*math.sin(DegtoRad(self.angle))

        self.angle = keepAngleInRange(self.angle)#keep angle from 0 - 360
        
        if(self.Vangle>2.0): #CAPPING STATEMENT ON SPEED OF THE BALL
            self.Vangle= 2.0
        elif(self.Vangle<-2.0):
            self.Vangle = 2
    
    def barrierCollision(self, lines):
        for n in range(len(lines)):
            difference = lines[n][2] - self.angle
            if(self.totalr < earth.r + earth.line_length + self.r):
                if(difference<= 7.5 and difference >0):#collision on right side
                    if(  returnSign(earth.speed) == returnSign(self.Vangle)  ):
                        self.Vangle = self.Vangle
                    else: 
                        self.Vangle = -1*self.Vangle
                        self.Aangle = -1*self.Aangle*0.05
                        self.angle = lines[n][2] -7.8 #this number was hand calculated
                       
                    self.Vangle*=0.001
                elif(difference>= -7.5 and difference <0):#collision on left side
                    if(  returnSign(earth.speed) == returnSign(self.Vangle)  ):
                        #self.Vangle = earth.speed
                        self.Vangle = self.Vangle
                    else: 
                        self.Vangle = -1*self.Vangle
                        self.Aangle = -1*self.Aangle*0.05
                        self.angle = lines[n][2] + 7.8
                    self.Vangle*=0.001
            
    def pointToLine(self,line):#[[400,500],[580,420]] WORKING
        mline = findSlope(line)#slope of the barrier line
        '''
        
        '''
        distance = 0
        if(self.Vangle!=0):
            self.dx = self.Vangle*math.cos(self.angle)
            self.dy = self.Vangle*math.sin(self.angle)
            if(self.dx ==0):
                if(self.dy<0):
                    mball = -1000
                elif(self.dy>0):
                    mball = 1000
                elif(self.dy==0):
                    mball = 0
            else:
                mball = self.dy/self.dx
            if(mline==0):
                distance = abs(line[0][1] - self.y)
            else:
                x = (mball*(self.x) - self.y + line[1][1] - mline*line[1][0])/(mball-mline)
                y = mline*x+(line[1][1] - mline*line[1][0])
                distance = dist([self.x,self.y],[x,y])
        return distance
    def between(self, lines):
        for n in range(len(lines)):
            #[ [[0,0],[0,0]] , [[0,0],[0,0]] , [[0,0],[0,0]] , [[0,0],[0,0]] , [[0,0],[0,0]] ]
            center = [  (lines[n][0][0] +lines[n][1][0])/2 , (lines[n][0][1] + lines[n][1][1])/2  ]
            if( dist(center, [self.x,self.y]) < 2*self.r ):
                if(self.r>=self.pointToLine(lines[n])):
                    self.collide = [True, lines[n][2]]
                else:
                    self.collide = [False, lines[n][2]]
    

      
    
        
        
            


class Planet(pygame.sprite.Sprite):
    def __init__(self, x, y, r, rotation, line_length, speed, accel):
        pygame.sprite.Sprite.__init__(self)
        self.x = x
        self.y = y
        self.r = r
        self.rotangle = rotation
        self.line_length = line_length
        self.draw_width = 10
        self.speed = speed
        self.accel = accel
    def draw(self):#WORKS
        pygame.draw.circle(Surface, BLACK, ConvertCoord((int)(self.x),(int)(self.y)), (int)(self.r), self.draw_width)
    def lines(self, num_lines):#WORKS
        total_degrees = 360.0
        section_degrees = total_degrees/num_lines
        for n in range(num_lines):
            line_coords[n][0][0]= self.r * math.cos( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][0][1] = self.r * math.sin( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][1][0] = (self.r+self.line_length) * math.cos( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][1][1] = (self.r+self.line_length) * math.sin( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][2] = (self.rotangle%360 + n*section_degrees)%360
            self.draw_lines(ConvertCoord(line_coords[n][0][0],line_coords[n][0][1]),ConvertCoord(line_coords[n][1][0],line_coords[n][1][1]))
            
    def draw_lines(self, p1, p2):#WORKS
        pygame.draw.line(Surface, BLACK, p1, p2, self.draw_width)
    def rotation(self, slow_constant):
        key=pygame.key.get_pressed()
        
        if(abs(self.accel)<0.05):
            if(key[K_RIGHT]):
                self.accel-=0.00003
            elif(key[K_LEFT]):
                self.accel+=0.00003
        self.speed = self.speed/slow_constant
        self.accel = self.accel/slow_constant
        if((self.speed>-0.5 and self.accel<0) or (self.speed<0.5 and self.accel>0)):
            self.speed+=self.accel
        self.incrementAngle(self.speed)
  
                
    def incrementAngle(self, angle):
        self.rotangle+=angle
    
        
#---Initialize objects---#
planet_radius = 140.0
ball_radius = 20.0
earth = Planet(0,0, planet_radius,0, 55, 0,0)
ball1 = Ball(planet_radius + ball_radius, 0, 0, 0, ball_radius, 0)

while True:
    Surface.fill(BGCOLOR)
    for event in pygame.event.get():
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            pygame.quit()
            sys.exit()
#--drawings--#
    #print ball1.x , " ", ball1.y
    earth.lines(5)
    earth.draw()
    ball1.draw()
#------------#
    

#----Calculations---#
    earth.rotation(1.012)
    
    #ball1.x = pygame.mouse.get_pos()[0]-400
    #ball1.y = -1*(pygame.mouse.get_pos()[1]-320)
    ball1.move(earth, line_coords)
    #ball1.boundary()
    #ball1.between(line_coords)
    #earth.applygrav(ball1)
    pygame.display.update()
    
