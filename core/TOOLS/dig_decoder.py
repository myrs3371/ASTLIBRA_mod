'''
This file is part of FSMOD.

FSMOD is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

FSMOD is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with FSMOD. If not, see <https://www.gnu.org/licenses/>.

FSMOD AUTHOR: FORSAKENSILVER(遗忘的银灵)
'''

#dig decoder v1.1
#   v1.1 added 3 channel 2 channel 1 channel dig file support
from array import array
import time
import zlib
from PIL import Image
import sys
#Thx this for png filter !!!
##https://pyokagan.name/blog/2019-10-14-png/

data = array('B')
fix_data = None
file_name = 'open10.dig'
debug = True
if len(sys.argv) >= 2:
    file_name = sys.argv[1]

if len(sys.argv) >= 3:
    if sys.argv[2] != '-D': 
        debug = False

with open(file_name, 'rb') as f:
    fix_data = f.read()
    data = bytearray(fix_data)

#Convert little endian binary lists to int
def litInt(bts):
    if(isinstance(bts, list)):
        bts = b''.join(bts)
    return int.from_bytes(bts, byteorder='little') 

# a general int to binary lists convertion function
def litByte(i,size = 4, signed = False):  
    return i.to_bytes(size, byteorder='little', signed = signed)

mark_tag = litInt(data[4:8])

width = litInt(data[8:12])
height = litInt(data[12:16])

org_length = litInt(data[16:20])
compressed_length = litInt(data[20:24])

unknown_tail = litInt(data[24:28])

print('mark tag:', mark_tag)

print('width:', width)
print('height:', height)

print('org_length:', org_length)
print('compressed_length:', compressed_length)

uncompressed_data = zlib.decompress(data[28:], wbits=15)
print('My uncompressed length:', len(uncompressed_data))
#print(locals())
if debug:
    with open(file_name + ".raw", "wb") as binary_file:
        # Write bytes to file
        binary_file.write(uncompressed_data)

#Predict bpp:
one_bpp_size = 1 * (width) * height + height
two_bpp_size = 2 * (width) * height + height
three_bpp_size = 3 * (width) * height + height
four_bpp_size = 4 * (width) * height + height



img = Image.new('RGBA', (width, height), color = 'white')
pixels = img.load()
bpp = 4#bytesPerPixel



if one_bpp_size == len(uncompressed_data):
    print('!!! ONE CHANNEL BPP DETECTED, SWITCHING MODE--------')
    bpp = 1
elif two_bpp_size == len(uncompressed_data):
    print('!!! TWO CHANNEL BPP DETECTED, SWITCHING MODE--------')
    bpp = 2
elif three_bpp_size == len(uncompressed_data):
    print('!!! THREE CHANNEL BPP DETECTED, SWITCHING MODE--------')
    bpp = 3

#raw line width
line_width = bpp * width + 1 # 第一位是 Filter的byte
img_d = uncompressed_data

Recon = []

# filtered line width
stride = img.size[0] * bpp

def Recon_a(r, c):
    return Recon[r * stride + c - bpp] if c >= bpp else 0

def Recon_b(r, c):
    return Recon[(r-1) * stride + c] if r > 0 else 0

def Recon_c(r, c):
    return Recon[(r-1) * stride + c - bpp] if r > 0 and c >= bpp else 0

def PaethPredictor(a, b, c):
    p = a + b - c
    pa = abs(p - a)
    pb = abs(p - b)
    pc = abs(p - c)
    if pa <= pb and pa <= pc:
        Pr = a
    elif pb <= pc:
        Pr = b
    else:
        Pr = c
    return Pr

# build png filter!!!
for j in range(img.size[1]): # j is y
    idx = j * line_width
    filter_type = img_d[idx]
    print('L[', j , '] Filter:[', filter_type, '] ', end = '')
    #https://pyokagan.name/blog/2019-10-14-png/
    #for i in range(img.size[0]): # i is x
    #    idx = j * line_width + i * bpp + 1
    #    a0 = int(img_d[idx])

    for c in range(stride): # for each byte in scanline
        Filt_x = img_d[j * line_width + 1 + c]

        if filter_type == 0: # None
            Recon_x = Filt_x
        elif filter_type == 1: # Sub
            Recon_x = Filt_x + Recon_a(j, c)
        elif filter_type == 2: # Up
            Recon_x = Filt_x + Recon_b(j, c)
        elif filter_type == 3: # Average
            Recon_x = Filt_x + (Recon_a(j, c) + Recon_b(j, c)) // 2
        elif filter_type == 4: # Paeth
            Recon_x = Filt_x + PaethPredictor(Recon_a(j, c), Recon_b(j, c), Recon_c(j, c))
        else:
            raise Exception('unknown filter type: ' + str(filter_type))
        Recon.append(Recon_x & 0xff) # truncation to byte

img_d = Recon # 去掉了filter的那个bytes

if debug and bpp == 4:
    for i in range(img.size[0]): # i is x
        for j in range(img.size[1]): # j is y
            idx = j * stride + i * bpp 
            a0 = int(img_d[idx])
            a1 = int(img_d[idx+1])
            a2 = int(img_d[idx+2])
            a3 = int(img_d[idx+3])
            pixels[i,j] = (a0, 0, 0, 255)

    img.save(file_name + 'a0.bmp')

    for i in range(img.size[0]): # i is x
        for j in range(img.size[1]): # j is y
            idx = j * stride + i * bpp 
            a0 = int(img_d[idx])
            a1 = int(img_d[idx+1])
            a2 = int(img_d[idx+2])
            a3 = int(img_d[idx+3])
            pixels[i,j] = (0, a1, 0, 255)

    img.save(file_name + 'a1.bmp')

    for i in range(img.size[0]): # i is x
        for j in range(img.size[1]): # j is y
            idx = j * stride + i * bpp 
            a0 = int(img_d[idx])
            a1 = int(img_d[idx+1])
            a2 = int(img_d[idx+2])
            a3 = int(img_d[idx+3])
            pixels[i,j] = (0, 0, a2, 255)

    img.save(file_name + 'a2.bmp')

    for i in range(img.size[0]): # i is x
        for j in range(img.size[1]): # j is y
            idx = j * stride + i * bpp 
            a0 = int(img_d[idx])
            a1 = int(img_d[idx+1])
            a2 = int(img_d[idx+2])
            a3 = int(img_d[idx+3])
            pixels[i,j] = (a3, a3, a3, 255)

    img.save(file_name + 'a3.bmp')


for i in range(img.size[0]): # i is x
    for j in range(img.size[1]): # j is y
        idx = j * stride + i * bpp 
       
        if bpp == 4:
            a0 = int(img_d[idx]) #B
            a1 = int(img_d[idx+1]) #G
            a2 = int(img_d[idx+2]) #R
            a3 = int(img_d[idx+3]) #A
            pixels[i,j] = (a2, a1, a0,a3) #(a3,a2,a1,a0)
        elif bpp == 3:
            a0 = int(img_d[idx]) #B
            a1 = int(img_d[idx+1]) #G
            a2 = int(img_d[idx+2]) #R
            pixels[i,j] = (a2, a1, a0, 255)
        elif bpp == 2:
            a0 = int(img_d[idx]) #B
            a1 = int(img_d[idx+1]) #G
            pixels[i,j] = (a0, a0, a0, a1)
        elif bpp == 1:
            a0 = int(img_d[idx]) #B
            pixels[i,j] = (a0, a0, a0, 255)
print('')
print('--PNG file exported, final channel count:', bpp, '--')

if debug:
    img.save(file_name + 'comp.png')
    img.save(file_name + 'comp.bmp')
else:
    img.save(file_name + '.png')