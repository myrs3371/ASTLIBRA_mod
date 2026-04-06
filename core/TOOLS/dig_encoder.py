'''
This file is part of FSMOD.

FSMOD is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

FSMOD is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with FSMOD. If not, see <https://www.gnu.org/licenses/>.

FSMOD AUTHOR: FORSAKENSILVER(遗忘的银灵)
'''
#dig encoder v1.1
#   v1.1 added 3 channel 2 channel 1 channel dig file support
from array import array
import time
import zlib
from PIL import Image
import sys
import os
data = array('B')
fix_data = None
file_name = 'wpn02.dig'
png_file_name = 'wpn02.dig.png'
out_file_name = 'wpn02.dig'
if len(sys.argv) >= 2:
    if sys.argv[1].endswith('.dig.png'): 
        png_file_name = sys.argv[1]
        file_name = png_file_name[:-4]
        out_file_name = file_name
    else:
        print('wrong extension image need to end with .dig.png !!!')
        sys.exit()

with open(file_name, 'rb') as f:
    fix_data = f.read()
    data = bytearray(fix_data)

bak_file = file_name + '.bak'
if not os.path.exists(bak_file):
    with open(bak_file, "wb") as binary_file:
        # Write bytes to BAKE UP FILE
        binary_file.write(data)

#Convert little endian binary lists to int
def litInt(bts):
    if(isinstance(bts, list)):
        bts = b''.join(bts)
    return int.from_bytes(bts, byteorder='little') 

# a general int to binary lists convertion function
def litByte(i,size = 4, signed = False):  
    return i.to_bytes(size, byteorder='little', signed = signed)

width = litInt(data[8:12])
height = litInt(data[12:16])

org_length = litInt(data[16:20])
compressed_length = litInt(data[20:24])

unknown_tail = litInt(data[24:28])

print('width:', width)
print('height:', height)

print('org_length:', org_length)
print('compressed_length:', compressed_length)

one_bpp_size = 1 * (width) * height + height
two_bpp_size = 2 * (width) * height + height
three_bpp_size = 3 * (width) * height + height
four_bpp_size = 4 * (width) * height + height

bpp = 4
if one_bpp_size == org_length:
    print('!!! ONE CHANNEL BPP DETECTED, SWITCHING MODE--------')
    bpp = 1
elif two_bpp_size == org_length:
    print('!!! TWO CHANNEL BPP DETECTED, SWITCHING MODE--------')
    bpp = 2
elif three_bpp_size == org_length:
    print('!!! THREE CHANNEL BPP DETECTED, SWITCHING MODE--------')
    bpp = 3

# open image
im = Image.open(png_file_name)
rgb_im = im.convert('RGBA')
raw_in_data = bytearray()
for y in range(height):
    raw_in_data += bytearray([0])
    for x in range(width):
        r, g, b, a = rgb_im.getpixel((x, y))
        if bpp == 4:
            raw_in_data += bytearray([b, g, r, a])
        elif bpp == 3:
            raw_in_data += bytearray([b, g, r])
        elif bpp == 2:
            raw_in_data += bytearray([r, a])
        elif bpp == 1:
            raw_in_data += bytearray([r])
        else:
            raise ValueError('Invalid Bytes per pixel!!!')
    

print('IN- uncompressed size', len(raw_in_data))
# convert image to A B G R + 0 per line
compressed_in = zlib.compress(raw_in_data)
# get final length
final_length = len(raw_in_data)
# get final compressed length
final_compressed_length = len(compressed_in)
print('IN- compressed size', final_compressed_length)
print('IN- channel count:', bpp)
# combine write to out.file
out_data = bytearray()
out_data += data[0:16]
out_data += litByte(final_length)
out_data += litByte(final_compressed_length)
out_data += data[24:28]
out_data += compressed_in


with open(out_file_name, "wb") as binary_file:
   
    # Write bytes to file
    binary_file.write(out_data)

