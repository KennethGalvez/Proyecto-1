from gl import Renderer, color, V3, V2
from texture import Texture
from shaders import *

width = 1980
height = 1275

rend = Renderer(width, height)

rend.dirLight = V3(1,0,0)

rend.background = Texture("models/mar.bmp")

rend.glClearBackground()

rend.active_texture = Texture("models/yellow.bmp")
rend.active_shader = sombra
rend.glLoadModel("models/tuna.obj",
                 translate = V3(-10, 0, -10),
                 scale = V3(1,1,1),
                 rotate = V3(0,0,0)) 

rend.active_texture = Texture("models/metalica.bmp")
rend.active_shader = metal
rend.glLoadModel("models/submarine.obj",
                 translate = V3(2, 0, -15),
                 scale = V3(0.5,0.5,0.5),
                 rotate = V3(0,-40,0)) 

rend.active_texture = Texture("models/oro.bmp")
rend.active_shader = metal
rend.glLoadModel("models/mlrs.obj",
                 translate = V3(-1, 0, -5),
                 scale = V3(0.1,0.1,0.1),
                 rotate = V3(0,0,90)) 

rend.active_texture = Texture("models/rojo.bmp")
rend.active_shader = erizo
rend.glLoadModel("models/AquaRail.obj",
                 translate = V3(1.7, -2, -5),
                 scale = V3(0.1,0.1,0.1),
                 rotate = V3(-85,70,80)) 


""" #Sonic parado
rend.active_texture = Texture("models/Sonic.bmp")
rend.active_shader = erizo
rend.glLoadModel("models/parado.obj",
                 translate = V3(-4, 0, -10),
                 scale = V3(4,4,4),
                 rotate = V3(0,0,0)) 
#Sonic corriendo
rend.active_texture = Texture("models/Sonic.bmp")
rend.active_shader = erizo
rend.glLoadModel("models/sonic2.obj",
                 translate = V3(-1, 0, -10),
                 scale = V3(4,4,4),
                 rotate = V3(0,0,0))

#Rings
rend.active_texture = Texture("models/ring.bmp")
rend.active_shader = metal
rend.glLoadModel("models/ring.obj",
                 translate = V3(1, 0, -10),
                 scale = V3(1,1,1),
                 rotate = V3(0,0,0))

rend.active_texture = Texture("models/ring.bmp")
rend.active_shader = metal
rend.glLoadModel("models/ring.obj",
                 translate = V3(2, 0, -10),
                 scale = V3(1,1,1),
                 rotate = V3(0,0,0))

rend.active_texture = Texture("models/ring.bmp")
rend.active_shader = metal
rend.glLoadModel("models/ring.obj",
                 translate = V3(3, 0, -10),
                 scale = V3(1,1,1),
                 rotate = V3(0,0,0))

#Shadow
rend.active_texture = Texture("models/shadow.bmp")
rend.active_shader = sombra
rend.glLoadModel("models/shadow.obj",
                 translate = V3(6, 0, -5),
                 scale = V3(4,4,4),
                 rotate = V3(0,0,0))

#Super
rend.active_texture = Texture("models/Sonic.bmp")
rend.active_shader = erizo
rend.glLoadModel("models/super.obj",
                 translate = V3(5, 0, -10),
                 scale = V3(4,4,4),
                 rotate = V3(0,0,0)) """



rend.glFinish("output.bmp")
