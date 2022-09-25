#!/usr/bin/env python3

# Change the displayed MD5 of the NES hashquine without changing its MD5.

# Ange Albertini 2022

import sys
import hashlib

from collisions import *

def get_bits(s):
	return '{md5:0>128b}'.format(md5 = int("0x" + s, 16))


def flip_bits(d, bits):
	for i, j in enumerate(bits):
		if j == "1":
			d = swap_fccoll(d, 134 + i*2)
	return d


fn = sys.argv[1]

with open(fn, "rb") as f:
	d = bytearray(f.read())
old_md5 = hashlib.md5(d).digest()

# check we have the right file
assert hashlib.md5(d[:0x6180]).hexdigest() == "5ec939f775d49bff5fbb3b1e7f9de1c2"
print('Original nes hashquine file found')
print('Resetting Fastcoll blocks')
for i in range(128):
	d = swap_fccoll(d, 134+i*2, side=2)


# set the actual value
if len(sys.argv) > 2:
	print("Encoding requested value.")
	md5 = sys.argv[2]
else:
	print("Encoding value of the file")
	md5 = hashlib.md5(d).hexdigest()
md5 = sys.argv[2] if len(sys.argv) > 2 else hashlib.md5(d).hexdigest()
reset_bits = get_bits(md5)
d = flip_bits(d, reset_bits)

assert old_md5 == hashlib.md5(d).digest()
with open("output.nes", "wb") as f:
	f.write(d)	
