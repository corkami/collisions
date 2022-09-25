#!/usr/bin/env python3

# flip or reset collision blocks

# Ange Albertini 2022

import sys
import hashlib

BLOCK_SIZE = 0x40

def read_dword(d, offset):
	return int.from_bytes(d[offset:offset + 4], "little")


def write_dword(d, val, offset):
	for i in range(4):
		d[offset + i] = (val >> (i*8)) & 0xFF
	return d


def swap_fccoll(d, i, side=None):
	# get FastColl other side of the collision
	# return a specific side if requested
	idx = i * BLOCK_SIZE
	oldmd5 = hashlib.md5(d).hexdigest()
	old = bytearray([el for el in d])

	for off in [0x13, 0x3b]:
		d[idx + off] = 0x80 ^ d[idx  + off]
		off += BLOCK_SIZE
		d[idx + off] = 0x80 ^ d[idx  + off]
	
	dw1_1 = read_dword(d, idx + 0x2c)
	dw1_2 = read_dword(d, idx + 0x6c)

  # from File2 to File1
	dw2_1 = dw1_1 + 0x8000
	dw2_2 = dw1_2 - 0x8000
	d = write_dword(d, dw2_1, 0x2c + idx)
	d = write_dword(d, dw2_2, 0x6c + idx)
	if hashlib.md5(d).hexdigest() == oldmd5:
		d_1 = d
		d_2 = old
	else:
		# didn't work? Confirm was the other way around
		dw2_1 = dw1_1 - 0x8000
		dw2_2 = dw1_2 + 0x8000
		d = write_dword(d, dw2_1, 0x2c + idx)
		d = write_dword(d, dw2_2, 0x6c + idx)
		d_1 = old
		d_2 = d

	assert hashlib.md5(d).hexdigest() == oldmd5

	# return the specified side
	if side == 1:
		return d_1
	elif side == 2:
		return d_2
	return d
