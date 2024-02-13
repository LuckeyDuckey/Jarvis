import pygame
from pygame.locals import *
from datetime import datetime
import math, random, os, time

pygame.init()

jarvis_font = pygame.font.Font("Azonix.otf", 30)
title_font = pygame.font.SysFont(None, 35)
body_font = pygame.font.SysFont(None, 20)

class Widget: #resize hover movement font
    def __init__(self, pos, title, text, timer):
        
        self.true_pos = [pos[0]-1,pos[1]-1]#[150,150]
        self.pos = [pos[0]-1,pos[1]-1]#[150,150]
        self.true_size = [425, 285]
        self.size = [425, 285]
        
        self.rect = pygame.Rect(self.pos[0],self.pos[1],self.size[0],self.size[1]) #x,y,width,height
        self.line = pygame.Rect(self.pos[0]+10,self.pos[1]+43,len(title)*10,5) #x,y,width,height
        
        self.text = body_font.render(text, True, (255, 255, 255))
        self.title = title_font.render(title, True, (255, 255, 255))

        self.lines = []
        self.offset = [50,1.1,0]
        self.size_offset = 0
        self.mouse_hold_offset = [0,0]
        self.time = [timer, time.time()]
        self.movement = False

        self.calculate_size(title, text)

    def main(self, mx, my, win, delta_time):

        #Scroll up when spawned -----
        if self.offset[2] < 51 and self.time[0] > (time.time() - self.time[1]):
            self.offset[0] = self.offset[0] / self.offset[1]
            self.offset[2] += 1
            
        self.pos[1] = self.true_pos[1] + self.offset[0]
        self.pos[0] = self.true_pos[0]
        #-----

        if self.movement == True and pygame.mouse.get_pressed(num_buttons=3)[0]: self.true_pos[0], self.true_pos[1] = mx+self.mouse_hold_offset[0], my+self.mouse_hold_offset[1]
        if not pygame.mouse.get_pressed(num_buttons=3)[0]: self.mouse_hold_offset, self.movement = [self.true_pos[0]-mx,self.true_pos[1]-my], False
        
        if self.rect.collidepoint((mx, my)) and self.size_offset < 15: self.size_offset += 1.25 * delta_time
        if not self.rect.collidepoint((mx, my)) and self.size_offset > 0: self.size_offset -= 1.25 * delta_time

        self.size[0] = self.true_size[0] + self.size_offset
        self.size[1] = self.true_size[1] + self.size_offset
        
        self.rect = pygame.Rect(self.pos[0]-self.size_offset/2,self.pos[1]-self.size_offset/2,self.size[0],self.size[1])
        self.line.x, self.line.y = self.pos[0]+10, self.pos[1]+43

        pygame.draw.rect(win, (255, 50, 50), self.line, 0, 3)
        pygame.draw.rect(win, (255, 255, 255), self.rect, 2)

        #write text -----
        win.blit(self.title, (self.pos[0]+10, self.pos[1]+10))

        for line in range(len(self.lines)):
            self.text = body_font.render(self.lines[line], True, (255, 255, 255))
            win.blit(self.text, (self.pos[0]+10, self.pos[1]+60+(18*line)))
            
        #-----

        if self.time[0] < (time.time() - self.time[1]) and self.offset[2] == 51: self.offset[2] = 0
        if self.time[0] < (time.time() - self.time[1]) and self.offset[2] == 50: return True

        if self.offset[2] < 51 and self.time[0] < (time.time() - self.time[1]):
            self.offset[0] = self.offset[0] * self.offset[1]
            self.offset[2] += 1

        #glow ----
        win.blit(self.glow([10,10,50]),(self.pos[0]-20-self.size_offset/2,self.pos[1]-20-self.size_offset/2),special_flags=BLEND_RGB_ADD)
        #-----

    def glow(self, color):
        surf = pygame.Surface((self.size[0]+41,self.size[1]+41))
        for i in range(10):
            pygame.draw.rect(surf,[0,8*(i+1),10*(i+1)],[0+(2*i),0+(2*i),self.size[0]+(40-4*i),self.size[1]+(40-4*i)],2)
        surf.set_colorkey((0,0,0))
        return surf

    def left_click(self, mx, my):
        if self.rect.collidepoint((mx, my)): self.movement = True

    def right_click(self, mx, my):
        if self.rect.collidepoint((mx, my)) and self.offset[2] == 51: self.time[0] = 1

    def calculate_size(self, title, text):
        
        self.size = [0, 0]

        #get title and body length -----
        self.size[0] = (title_font.render(title, True, (255, 255, 255))).get_rect()[2]
        self.size[1] = (body_font.render(text, True, (255, 255, 255))).get_rect()[2]
        #-----

        #decide x length -----
        if self.size[0] >= 500: self.max_len, self.size[0] = self.size[0], self.size[0]
        if self.size[0] > self.size[1] and self.size[0] <= 500: self.max_len, self.size[0] = self.size[0], self.size[0]
        if self.size[0] < self.size[1] and self.size[1] < 500: self.max_len, self.size[0] = self.size[1], self.size[1]
        if self.size[0] < self.size[1] and self.size[1] >= 500 and self.size[0] < 500: self.max_len, self.size[0] = 500, 500
        #-----

        self.size[0] += 20
        self.size[1] = 67 + 18

        #seperate text into lines -----

        if self.max_len >= 500:
            length, pos, words, prev_length = 0, 0, text.split(" "), 0

            for word in range(len(words)):

                prev_length = length
                
                for letter in words[word]:
                    length += body_font.size(letter)[0]
                    
                length += body_font.size(" ")[0]
                prev_length = length - prev_length
                
                if (length - body_font.size(" ")[0]) > self.max_len:
                    
                    self.lines.append(" ".join(words[pos:word]))
                    self.size[1] += 18
                    pos, length = word, prev_length

            self.lines.append(" ".join(words[pos:word+1]))

        else: self.lines.append(text)

        self.true_size[0], self.true_size[1] = self.size[0], self.size[1]
        #-----
        
class UI:
    def __init__(self):
        self.win = pygame.display.set_mode((1000,600))
        self.clock = pygame.time.Clock()

        pygame.display.set_caption("J.A.R.V.I.S")
        pygame.display.set_icon(pygame.image.load(os.path.join(os.getcwd(), "Icon.png")).convert_alpha())
        
        self.bg = pygame.transform.scale(pygame.image.load(os.path.join(os.getcwd(), "Bg.png")),(1000,600)).convert_alpha()
        self.logo = pygame.image.load(os.path.join(os.getcwd(), "Logo.png")).convert_alpha()

        self.logo_size = 200
        self.logo_angle = 0

        self.last_time = time.time()
        self.delta_time = 0

        self.widgets = []

    def main(self):
        while True:
            self.clock.tick(75)

            #pygame.display.set_caption("J.A.R.V.I.S "+str(int(self.clock.get_fps())))
            #self.win = pygame.display.set_mode((1000,600))

            self.delta_time = time.time() - self.last_time
            self.delta_time *= 60
            self.last_time = time.time()

            if len(self.widgets) > 0: self.widget_screen()
            else: self.logo_screen()

    def logo_screen(self):
        self.win.blit(pygame.transform.scale(self.bg,(1000,600)), (0, 0))

        self.logo_angle = (self.logo_angle + (0.5*self.delta_time)) if self.logo_angle < 360 else 1
        logo_copy = pygame.transform.rotate(pygame.transform.scale(self.logo,((int(self.logo_size)+29), (int(self.logo_size)+34))), self.logo_angle)
        self.win.blit(logo_copy, (500 - int(logo_copy.get_width() / 2), 300 - int(logo_copy.get_height() / 2)))

        if self.logo_size < 300: self.logo_size += (abs(self.logo_size - 300) / 10) * self.delta_time if abs(self.logo_size - 300) >= 10 else 1
        elif self.logo_size > 300: self.logo_size = 300

        text = jarvis_font.render(str(datetime.now().strftime("%I:%M")), True, (255, 255, 255))
        self.win.blit(text, text.get_rect(center=(500, 300)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 2:
                    self.widgets.append(Widget(pygame.mouse.get_pos(), "Title", "Large amount of text for the body i need for this demo so you can see it take up multiple lines this way i can get a understanding of how larger texts such as google searches will look when displayed on the screen as i will be using jarvis for such funtions.", 30))
                
        pygame.display.update()

    def widget_screen(self):
        self.win.blit(pygame.transform.scale(self.bg,(1000,600)), (0, 0))

        mx, my = pygame.mouse.get_pos()

        for i,widget in sorted(enumerate(self.widgets),reverse=True):
            try:
                if self.widgets[i].main(mx, my, self.win, self.delta_time) == True: del self.widgets[i]
            except:
                pass

        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit()
            if event.type == MOUSEBUTTONDOWN:
                if event.button == 1:
                    for i in range(len(self.widgets)):
                        self.widgets[i].left_click(mx,my)

                if event.button == 2:
                    self.widgets.append(Widget(pygame.mouse.get_pos(), "Title", "Large amount of text for the body i need for this demo so you can see it take up multiple lines this way i can get a understanding of how larger texts such as google searches will look when displayed on the screen as i will be using jarvis for such funtions.", 30))
                    
                if event.button == 3:
                    for i in range(len(self.widgets)):
                        self.widgets[i].right_click(mx,my)
        
        self.logo_size = 200
        pygame.display.update()

ui = UI()
ui.main()
