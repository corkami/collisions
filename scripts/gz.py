#!/usr/bin/env python3

# Reusable MD5 collision for .GZ
#  via pre-computed UniColl prefixes

# Ange Albertini 2021

# A (Archive) = T (Trampoline header) + [XtraField] + LP (LandingPad)

#    000: Aalign
#   ----  ---------
#    03E: Tunicoll (so that SuLen_h is at 0x49)
# Enforced by UniColl:
#    0C0: LPs [0xA]
#   ----  ---------
#    0CA: Ta (jumps to LPa, from 0xDA to 0x1DA) 
# Enforced by UniColl:
#    1C0: LPl [0xA]
#   ----  ---------
#    1CA: Tb  (jumps to LPb) [0x10 (minimal size)]
#    1DA: LPa [0xA]
#   ----  ---------
#    1E4: Aa [Sa]
# Sa+1E4: Boom (non-null non-sig bytes forces Gzip parsing to stop)
# Sa+1E5: LPb [0xA]
#   ----  ---------
# Sa+1EF: Ab

# Tunicoll jumps short to LPs, long to LPl.
# Ta jumps to LPa, but is truncated at LPl.
# Tb jumps to LPb, over LPa+A+Boom.
# Archive A has to fit in a gzip extra subfield.
#  workaround: split gzip in gzip streams.
# Size of Archive B doesn't matter.

# Acknowledgment:
# Yann Droneaud - https://twitter.com/ydroneaud/status/1449079965853573127

import hashlib
import sys


def makeHeader(length, mtime=b"Ange",subfieldID=b"cb"):

# 0  1  2  3  4  5  6  7  8  9  A  B  C  D  E  F 10          -A -9 -8 -7 -6 -5 -4 -3 -2 -1 EOF
# Sig  |CM|Fl|Mtime      |XF|OS|Len  |SuID |SuLen|  SubData |Body |CRC32      |Size32     |
# 1F 8B|08|04|.A .n .g .e|02|FF|LL LL|Id Id|Sl Sl|   ...    |03 00|00 00 00 00|00 00 00 00|
#                                              ^^
#                                              \- Unicoll applied here
	result = b"".join([
		b"\x1f\x8b", # Signature
		b"\x08",     # Compression Method = Deflate
		b"\4",       # Flags = Extra Field
		mtime,
		b"\2",       # Extra flags: compression max
		b"\xFF",     # OS: Unknown
		(length+4).to_bytes(2, "little"),
		subfieldID,
		(length).to_bytes(2, "little"),
		])
	assert len(result) == 16
	return result


# All landing pads are identical.
lp = b"".join([
	b"\3\0",     # Body [empty data]
	b"\0\0\0\0", # CRC32
	b"\0\0\0\0", # USize32
])

# Gzip terminates when indicating 2 characters - since Gzip signature is 2 bytes
# should be non null, should not be 1F 8B
boom = b"AA"

filename_a = sys.argv[1]
filename_b = sys.argv[2]

with open(filename_a, "rb") as f:
	contents_a = f.read()
data_a = lp + contents_a + boom
size_a = len(data_a)

with open(filename_b, "rb") as f:
	contents_b = f.read()
data_b = lp + contents_b


suffix = lp
suffix += makeHeader(0x1DA - 0xDA, mtime=b"JMPa")

def deco(s, c=b"|"):
	"""align a string on 16 bytes"""
	return c + s[:16].center(16 - 2) + c


suffix += b"".join([
	b"\1\2\3\4\5\6",
	b"+--------------+",
	deco(b"reusable"),
	deco(b""),
	deco(b"GZIP"),
	deco(b""),
	deco(b"collision"),
	deco(b""),
	deco(b"for MD5"),
	deco(b""),
	deco(b"2021"),
	deco(b""),
	deco(b"Ange"),
	deco(b"Albertini"),
	b"+______________+",
	])
# suffix += (0x100 - len(suffix)) * b"\0"
assert len(suffix) == 0x100
suffix += lp
suffix += makeHeader(size_a, mtime=b"JMPb")
suffix += data_a
suffix += data_b


with open("prefix1.gz", "rb") as f:
	prefix1 = f.read()
with open("prefix2.gz", "rb") as f:
	prefix2 = f.read()

def check(d1, d2):
	assert prefix1 != prefix2
	assert len(prefix1) == len(prefix2)
	assert hashlib.md5(prefix1).hexdigest() == hashlib.md5(prefix2).hexdigest()

check(prefix1, prefix2)
data1 = prefix1 + suffix
data2 = prefix2 + suffix
check(data1, data2)

with open("coll-1.gz", "wb") as f:
	f.write(data1)
with open("coll-2.gz", "wb") as f:
	f.write(data2)
