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

Surface = pygame.display.set_mode((MAX_X, MAX_Y))
pygame.display.set_caption('Planet Vortex')
line_coords = [ [[0,0],[0,0]] , [[0,0],[0,0]] , [[0,0],[0,0]] , [[0,0],[0,0]] , [[0,0],[0,0]] ]
#-------------------------------------------#


#---------Helper Functions -----------------#
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
#-------------------------------------------#
class Ball(pygame.sprite.Sprite):
    def __init__(self, x, y, dx, dy, r, angle):
        pygame.sprite.Sprite.__init__(self)
        self.gaccel=0.05 #gravitational acceleration constant
        self.dx= 0
        self.dy= 0
        self.x = x
        self.y = y
        self.r = r
        self.forcedx = 0
        self.forcedy = 0
        self.FIRSTTOUCH=True
        self.angle = angle
        self.speed = 0
        self.gspeed=0
        self.draw_width = 4
        self.stop = 1
    def draw(self):#WORKING
        pygame.draw.circle(Surface, BLACK, ConvertCoord((int)(self.x),(int)(self.y)), self.r, self.draw_width)
    def boundary(self, earth_radius):#WORKING
        cur_r = mag(self.x,self.y)
        if( cur_r< earth_radius+self.r):
            self.x = self.x/cur_r *(self.r+earth_radius)
            self.y = self.y/cur_r *(self.r+earth_radius)
    def touchvector(self, speed, earth_radius):
        self.dx = -1*self.y/mag(self.x, self.y)#*earth.speed#*earth.accel
        self.dy = self.x/mag(self.x, self.y)#*earth.speed#*earth.accel
        
    def applyearthspeed(self):
        self.dx *= earth.speed
        self.dy *= earth.speed
    def grav(self, earth_radius):
        magnit = mag(self.x, self.y)
        self.gspeed+=self.gaccel
        #print self.gspeed;
        if(self.r+earth_radius>mag(self.x, self.y)):
           self.gspeed=0.05
        self.x+= -1*self.x/magnit*self.gspeed
        self.y+= -1*self.y/magnit*self.gspeed
    def move(self, earthobj, lines):
        self.touchvector(mag(self.dx, self.dy), earthobj.r)
        self.grav(earthobj.r)
        print self.dx, " " , self.dy
        self.between(lines)
        self.applyearthspeed()
        if(self.stop ==0):
            self.dy = earthobj.speed*2000
            self.dx = earthobj.speed*2000
        else:
            self.x+=self.dx #add velocity to dx and dy
            self.y+=self.dy
        if(mag(self.dx, self.dy)>10): #CAPPING STATEMENT ON SPEED OF THE BALL
            self.dx=self.dx/mag(self.dx, self.dy)*10
            self.dy=self.dy/mag(self.dx, self.dy)*10
    def pointToLine(self,line):#[[400,500],[580,420]] WORKING
        mline = findSlope(line)#slope of the barrier line
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
                if(self.r>=self.pointToLine(lines[n])):#THIS WORKS (SAYS IF BALL IS HITTING LINE)
                    self.stop = 0
                elif(self.r+2<=self.pointToLine(lines[n])):
                    self.stop = 1
        
        
        
            


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
        pygame.draw.circle(Surface, BLACK, ConvertCoord(self.x,self.y), self.r, self.draw_width)
    def lines(self, num_lines):#WORKS
        total_degrees = 360.0
        section_degrees = total_degrees/num_lines
        for n in range(num_lines):
            line_coords[n][0][0]= self.r * math.cos( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][0][1] = self.r * math.sin( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][1][0] = (self.r+self.line_length) * math.cos( DegtoRad(self.rotangle + n*section_degrees) )
            line_coords[n][1][1] = (self.r+self.line_length) * math.sin( DegtoRad(self.rotangle + n*section_degrees) )
            self.draw_lines(ConvertCoord(line_coords[n][0][0],line_coords[n][0][1]),ConvertCoord(line_coords[n][1][0],line_coords[n][1][1]))
            
    def draw_lines(self, p1, p2):#WORKS
        pygame.draw.line(Surface, BLACK, p1, p2, self.draw_width)
    def rotation(self, slow_constant):
        key=pygame.key.get_pressed()
        if(key[K_SPACE]):
            ball1.x = pygame.mouse.get_pos()[0]-400
            ball1.y = -1*(pygame.mouse.get_pos()[1]-320)  
        if(abs(self.accel)<0.05):
            if(key[K_RIGHT]):
                self.accel-=0.00005
            elif(key[K_LEFT]):
                self.accel+=0.00005
        self.speed = self.speed/slow_constant
        self.accel = self.accel/slow_constant
        if((self.speed>-0.5 and self.accel<0) or (self.speed<0.5 and self.accel>0)):
            self.speed+=self.accel
        self.incrementAngle(self.speed)
  
                
    def incrementAngle(self, angle):
        self.rotangle+=angle
    def applygrav(self, obj):                           #junk
        obj.dx -=  0.2/(obj.x/abs(obj.x))
        obj.dy -=  0.2/(obj.y/abs(obj.y))
        
#---Initialize objects---#
planet_radius = 140
ball_radius = 20
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
    ball1.boundary(earth.r)
    #ball1.between(line_coords)
    #earth.applygrav(ball1)
    pygame.display.update()
