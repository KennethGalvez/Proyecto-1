import struct
from collections import namedtuple
import numpy as np

from math import cos, sin, tan, pi

import random

from obj import Obj

V2 = namedtuple('Point2', ['x', 'y'])
V3 = namedtuple('Point3', ['x', 'y', 'z'])
V4 = namedtuple('Point4', ['x', 'y', 'z', 'w'])

def char(c):
    #1 byte
    return struct.pack('=c', c.encode('ascii'))

def word(w):
    #2 bytes
    return struct.pack('=h', w)

def dword(d):
    #4 bytes
    return struct.pack('=l', d)

def color(r, g, b):
    return bytes([int(b * 255),
                  int(g * 255),
                  int(r * 255)] )

def baryCoords(A, B, C, P):

    areaPBC = (B.y - C.y) * (P.x - C.x) + (C.x - B.x) * (P.y - C.y)
    areaPAC = (C.y - A.y) * (P.x - C.x) + (A.x - C.x) * (P.y - C.y)
    areaABC = (B.y - C.y) * (A.x - C.x) + (C.x - B.x) * (A.y - C.y)

    try:
        # PBC / ABC
        u = areaPBC / areaABC
        # PAC / ABC
        v = areaPAC / areaABC
        # 1 - u - v
        w = 1 - u - v
    except:
        return -1, -1, -1
    else:
        return u, v, w

class Renderer(object):
    def __init__(self, width, height):

        self.width = width
        self.height = height

        self.clearColor = color(0,0,0)
        self.currColor = color(1,1,1)

        self.active_shader = None
        self.active_texture = None
        self.active_texture2 = None

        self.normal_map = None

        self.background = None

        self.dirLight = V3(0,0,-1)

        self.glViewMatrix()
        self.glViewport(0,0,self.width, self.height)
        
        self.glClear()

    def glViewport(self, posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height

        self.viewportMatrix = np.matrix([[width/2,0,0,posX+width/2],
                                         [0,height/2,0,posY+height/2],
                                         [0,0,0.5,0.5],
                                         [0,0,0,1]])

        self.glProjectionMatrix()

    def glViewMatrix(self, translate = V3(0,0,0), rotate = V3(0,0,0)):
        self.camMatrix = self.glCreateObjectMatrix(translate, rotate)
        self.viewMatrix = np.linalg.inv(self.camMatrix)

    def glLookAt(self, eye, camPosition = V3(0,0,0)):
        forward = np.subtract(camPosition, eye)
        forward = forward / np.linalg.norm(forward)

        right = np.cross(V3(0,1,0), forward)
        right = right / np.linalg.norm(right)

        up = np.cross(forward, right)
        up = up / np.linalg.norm(up)

        self.camMatrix = np.matrix([[right[0],up[0],forward[0],camPosition[0]],
                                    [right[1],up[1],forward[1],camPosition[1]],
                                    [right[2],up[2],forward[2],camPosition[2]],
                                    [0,0,0,1]])

        self.viewMatrix = np.linalg.inv(self.camMatrix)

    def glProjectionMatrix(self, n = 0.1, f = 1000, fov = 60):
        aspectRatio = self.vpWidth / self.vpHeight
        t = tan( (fov * pi / 180) / 2) * n
        r = t * aspectRatio

        self.projectionMatrix = np.matrix([[n/r,0,0,0],
                                           [0,n/t,0,0],
                                           [0,0,-(f+n)/(f-n),-(2*f*n)/(f-n)],
                                           [0,0,-1,0]])



    def glClearColor(self, r, g, b):
        self.clearColor = color(r,g,b)

    def glColor(self, r, g, b):
        self.currColor = color(r,g,b)

    def glClear(self):
        self.pixels = [[ self.clearColor for y in range(self.height)]
                         for x in range(self.width)]

        self.zbuffer = [[ float('inf') for y in range(self.height)]
                          for x in range(self.width)]



    def glClearBackground(self):
        if self.background:
            for x in range(self.vpX, self.vpX + self.vpWidth + 1):
                for y in range(self.vpY, self.vpY + self.vpHeight + 1):

                    tU = (x - self.vpX) / self.vpWidth
                    tV = (y - self.vpY) / self.vpHeight

                    texColor = self.background.getColor(tU, tV)

                    if texColor:
                        self.glPoint(x,y, color(texColor[0], texColor[1], texColor[2]))





    def glClearViewport(self, clr = None):
        for x in range(self.vpX, self.vpX + self.vpWidth):
            for y in range(self.vpY, self.vpY + self.vpHeight):
                self.glPoint(x,y,clr)


    def glPoint(self, x, y, clr = None): # Window Coordinates
        if (0 <= x < self.width) and (0 <= y < self.height):
            self.pixels[x][y] = clr or self.currColor

    def glPoint_vp(self, ndcX, ndcY, clr = None): # NDC
        if ndcX < -1 or ndcX > 1 or ndcY < -1 or ndcY > 1:
            return

        x = (ndcX + 1) * (self.vpWidth / 2) + self.vpX
        y = (ndcY + 1) * (self.vpHeight / 2) + self.vpY

        x = int(x)
        y = int(y)

        self.glPoint(x,y,clr)


    def glCreateRotationMatrix(self, pitch = 0, yaw = 0, roll = 0):
        
        pitch *= pi/180
        yaw   *= pi/180
        roll  *= pi/180

        pitchMat = np.matrix([[1, 0, 0, 0],
                              [0, cos(pitch),-sin(pitch), 0],
                              [0, sin(pitch), cos(pitch), 0],
                              [0, 0, 0, 1]])

        yawMat = np.matrix([[cos(yaw), 0, sin(yaw), 0],
                            [0, 1, 0, 0],
                            [-sin(yaw), 0, cos(yaw), 0],
                            [0, 0, 0, 1]])

        rollMat = np.matrix([[cos(roll),-sin(roll), 0, 0],
                             [sin(roll), cos(roll), 0, 0],
                             [0, 0, 1, 0],
                             [0, 0, 0, 1]])

        return pitchMat * yawMat * rollMat


    def glCreateObjectMatrix(self, translate = V3(0,0,0), rotate = V3(0,0,0), scale = V3(1,1,1)):

        translation = np.matrix([[1, 0, 0, translate.x],
                                 [0, 1, 0, translate.y],
                                 [0, 0, 1, translate.z],
                                 [0, 0, 0, 1]])

        rotation = self.glCreateRotationMatrix(rotate.x, rotate.y, rotate.z)

        scaleMat = np.matrix([[scale.x, 0, 0, 0],
                              [0, scale.y, 0, 0],
                              [0, 0, scale.z, 0],
                              [0, 0, 0, 1]])

        return translation * rotation * scaleMat

    def glTransform(self, vertex, matrix):
        v = V4(vertex[0], vertex[1], vertex[2], 1)
        vt = matrix @ v
        vt = vt.tolist()[0]
        vf = V3(vt[0] / vt[3],
                vt[1] / vt[3],
                vt[2] / vt[3])

        return vf

    def glDirTransform(self, dirVector, rotMatrix):
        v = V4(dirVector[0], dirVector[1], dirVector[2], 0)
        vt = rotMatrix @ v
        vt = vt.tolist()[0]
        vf = V3(vt[0],
                vt[1],
                vt[2])

        return vf

    def glCamTransform(self, vertex):
        v = V4(vertex[0], vertex[1], vertex[2], 1)
        vt = self.viewportMatrix @ self.projectionMatrix @ self.viewMatrix @ v
        vt = vt.tolist()[0]
        vf = V3(vt[0] / vt[3],
                vt[1] / vt[3],
                vt[2] / vt[3])

        return vf


    def glLoadModel(self, filename, translate = V3(0,0,0), rotate = V3(0,0,0), scale = V3(1,1,1)):
        model = Obj(filename)
        modelMatrix = self.glCreateObjectMatrix(translate, rotate, scale)
        rotationMatrix = self.glCreateRotationMatrix(rotate[0], rotate[1], rotate[2])

        for face in model.faces:
            vertCount = len(face)

            v0 = model.vertices[ face[0][0] - 1]
            v1 = model.vertices[ face[1][0] - 1]
            v2 = model.vertices[ face[2][0] - 1]

            v0 = self.glTransform(v0, modelMatrix)
            v1 = self.glTransform(v1, modelMatrix)
            v2 = self.glTransform(v2, modelMatrix)

            A = self.glCamTransform(v0)
            B = self.glCamTransform(v1)
            C = self.glCamTransform(v2)

            vt0 = model.texcoords[face[0][1] - 1]
            vt1 = model.texcoords[face[1][1] - 1]
            vt2 = model.texcoords[face[2][1] - 1]

            vn0 = model.normals[face[0][2] - 1]
            vn1 = model.normals[face[1][2] - 1]
            vn2 = model.normals[face[2][2] - 1]
            vn0 = self.glDirTransform(vn0, rotationMatrix)
            vn1 = self.glDirTransform(vn1, rotationMatrix)
            vn2 = self.glDirTransform(vn2, rotationMatrix)

            self.glTriangle_bc(A, B, C,
                               verts = (v0, v1, v2),
                               texCoords = (vt0, vt1, vt2),
                               normals = (vn0, vn1, vn2))

            if vertCount == 4:
                v3 = model.vertices[ face[3][0] - 1]
                v3 = self.glTransform(v3, modelMatrix)
                D = self.glCamTransform(v3)
                vt3 = model.texcoords[face[3][1] - 1]
                vn3 = model.normals[face[3][2] - 1]
                vn3 = self.glDirTransform(vn3, rotationMatrix)

                self.glTriangle_bc(A, C, D,
                                   verts = (v0, v2, v3),
                                   texCoords = (vt0, vt2, vt3),
                                   normals = (vn0, vn2, vn3))




    def glLine(self, v0, v1, clr = None):
        # Bresenham line algorithm
        # y = m * x + b
        x0 = int(v0.x)
        x1 = int(v1.x)
        y0 = int(v0.y)
        y1 = int(v1.y)

        # Si el punto0 es igual al punto 1, dibujar solamente un punto
        if x0 == x1 and y0 == y1:
            self.glPoint(x0,y0,clr)
            return

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        steep = dy > dx

        # Si la linea tiene pendiente mayor a 1 o menor a -1
        # intercambio las x por las y, y se dibuja la linea
        # de manera vertical
        if steep:
            x0, y0 = y0, x0
            x1, y1 = y1, x1

        # Si el punto inicial X es mayor que el punto final X,
        # intercambio los puntos para siempre dibujar de 
        # izquierda a derecha       
        if x0 > x1:
            x0, x1 = x1, x0
            y0, y1 = y1, y0

        dy = abs(y1 - y0)
        dx = abs(x1 - x0)

        offset = 0
        limit = 0.5
        m = dy / dx
        y = y0

        for x in range(x0, x1 + 1):
            if steep:
                # Dibujar de manera vertical
                self.glPoint(y, x, clr)
            else:
                # Dibujar de manera horizontal
                self.glPoint(x, y, clr)

            offset += m

            if offset >= limit:
                if y0 < y1:
                    y += 1
                else:
                    y -= 1
                
                limit += 1


    def glTriangle_std(self, A, B, C, clr = None):
        
        if A.y < B.y:
            A, B = B, A
        if A.y < C.y:
            A, C = C, A
        if B.y < C.y:
            B, C = C, B

        self.glLine(A,B, clr)
        self.glLine(B,C, clr)
        self.glLine(C,A, clr)

        def flatBottom(vA,vB,vC):
            try:
                mBA = (vB.x - vA.x) / (vB.y - vA.y)
                mCA = (vC.x - vA.x) / (vC.y - vA.y)
            except:
                pass
            else:
                x0 = vB.x
                x1 = vC.x
                for y in range(int(vB.y), int(vA.y)):
                    self.glLine(V2(x0, y), V2(x1, y), clr)
                    x0 += mBA
                    x1 += mCA

        def flatTop(vA,vB,vC):
            try:
                mCA = (vC.x - vA.x) / (vC.y - vA.y)
                mCB = (vC.x - vB.x) / (vC.y - vB.y)
            except:
                pass
            else:
                x0 = vA.x
                x1 = vB.x
                for y in range(int(vA.y), int(vC.y), -1):
                    self.glLine(V2(x0, y), V2(x1, y), clr)
                    x0 -= mCA
                    x1 -= mCB

        if B.y == C.y:
            # Parte plana abajo
            flatBottom(A,B,C)
        elif A.y == B.y:
            # Parte plana arriba
            flatTop(A,B,C)
        else:
            # Dibujo ambos tipos de triangulos
            # Teorema de intercepto
            D = V2( A.x + ((B.y - A.y) / (C.y - A.y)) * (C.x - A.x), B.y)
            flatBottom(A,B,D)
            flatTop(B,D,C)


    def glTriangle_bc(self, A, B, C, verts = (), texCoords = (), normals = (), clr = None):
        # bounding box
        minX = round(min(A.x, B.x, C.x))
        minY = round(min(A.y, B.y, C.y))
        maxX = round(max(A.x, B.x, C.x))
        maxY = round(max(A.y, B.y, C.y))

        edge1 = np.subtract(verts[1], verts[0])
        edge2 = np.subtract(verts[2], verts[0])

        triangleNormal = np.cross( edge1, edge2)
        triangleNormal = triangleNormal / np.linalg.norm(triangleNormal)

        deltaUV1 = np.subtract(texCoords[1], texCoords[0])
        deltaUV2 = np.subtract(texCoords[2], texCoords[0])
        f = 1 / (deltaUV1[0]* deltaUV2[1] - deltaUV2[0] * deltaUV1[1])

        tangent = [f * (deltaUV2[1] * edge1[0] - deltaUV1[1] * edge2[0]),
                   f * (deltaUV2[1] * edge1[1] - deltaUV1[1] * edge2[1]),
                   f * (deltaUV2[1] * edge1[2] - deltaUV1[1] * edge2[2])]
        tangent = tangent / np.linalg.norm(tangent)

        bitangent = np.cross(triangleNormal, tangent)
        bitangent = bitangent / np.linalg.norm(bitangent)

        for x in range(minX, maxX + 1):
            for y in range(minY, maxY + 1):


                u, v, w = baryCoords(A, B, C, V2(x, y))

                if 0<=u and 0<=v and 0<=w:

                    z = A.z * u + B.z * v + C.z * w

                    if 0<=x<self.width and 0<=y<self.height:
                        if z < self.zbuffer[x][y] and -1<=z<= 1:
                            self.zbuffer[x][y] = z

                            if self.active_shader:
                                r, g, b = self.active_shader(self,
                                                             baryCoords=(u,v,w),
                                                             vColor = clr or self.currColor,
                                                             texCoords = texCoords,
                                                             normals = normals,
                                                             triangleNormal = triangleNormal,
                                                             tangent = tangent,
                                                             bitangent = bitangent)



                                self.glPoint(x, y, color(r,g,b))
                            else:
                                self.glPoint(x,y, clr)



    def glFinish(self, filename):
        with open(filename, "wb") as file:
            # Header
            file.write(bytes('B'.encode('ascii')))
            file.write(bytes('M'.encode('ascii')))
            file.write(dword(14 + 40 + (self.width * self.height * 3)))
            file.write(dword(0))
            file.write(dword(14 + 40))

            #InfoHeader
            file.write(dword(40))
            file.write(dword(self.width))
            file.write(dword(self.height))
            file.write(word(1))
            file.write(word(24))
            file.write(dword(0))
            file.write(dword(self.width * self.height * 3))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))
            file.write(dword(0))

            #Color table
            for y in range(self.height):
                for x in range(self.width):
                    file.write(self.pixels[x][y])






