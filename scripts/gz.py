#!/usr/bin/env python3

# Reusable MD5 collision for .GZ
#  via pre-computed UniColl prefixes

# Ange Albertini 2021

# 2021/10/17: first release
# 2021/10/18: splitting streams of file if too big.


# A (Archive) = T (Trampoline header) + [XtraField] + LP (LandingPad)
# Sa = Size of Archive
# Archive or LP always before JMP

# 000: Aalign
# 03E: Tunicoll
# 0C0: LPs
# 0CA:     Ta (0x100 - required by UniColl)
#         /      [0x100]
# 1C0:   /    LPl [10]
# 1CA:  /        T (10 + Sa1 + 16)
# 1DA: LP       /
# 1E4: Aa1     /
#      T      /
#      |    LP
#      |        T (10 + Sa2 + 16)
#      LP      /
#      Aa2    /
#      ......
#      T     /
#      |    LP
#      |        T (10 + SaN + Boom)
#      LP      /
#      An     /
#      Boom  /
#           LP
#           B

# Make Boom a length of 16 to simplify the loop

# Between each Ai..Aj:
# T(10+16),                 , LP
#           LP, T(10+Saj+16),

# Ta jumps to LPa, but is truncated at LPl.
# Tb jumps to LPb, over LPa+A+Boom.

# Archive A will be split in gzip streams until all streams fit in an extra subfield.
# Size of Archive B doesn't matter.

# Acknowledgment:
# Yann Droneaud - https://twitter.com/ydroneaud/status/1449079965853573127

import argparse
import gzip
import hashlib
import io
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

parser = argparse.ArgumentParser(description="Generate GZip MD5 collisions.")
parser.add_argument('file1',
	help="first 'top' input file - will be cut in smaller chunks if needed.")
parser.add_argument('file2',
	help="second 'bottom' input file.")

args = parser.parse_args()
filename_a = args.file1
filename_b = args.file2

# All landing pads are identical.
lp = b"".join([
	b"\3\0",     # Body [empty data]
	b"\0\0\0\0", # CRC32
	b"\0\0\0\0", # USize32
])

# Gzip terminates when indicating 2 characters - since Gzip signature is 2 bytes
# should be non null, should not be 1F 8B
boom = 8 * b"AA"

with open(filename_a, "rb") as f:
	contents_a = f.read()

archivesA = [contents_a]


def split_archive(archive):
	data = gzip.decompress(archive)
	l = len(data)
	d1 = data[:l//2]
	d2 = data[l//2:]
	a1 = gzip.compress(d1, mtime=0)
	a2 = gzip.compress(d2, mtime=0)
	return a1, a2


while True:
	for i, archive in enumerate(archivesA):
		if len(archive) > 0xfffe:
			archive1, archive2 = split_archive(archive)
			archivesA[i] = archive2
			archivesA.insert(i, archive1)
			break
	else:
		break

concat = b""
for archive in archivesA:
	assert len(archive) <= 0xfffe
	concat += archive
assert gzip.decompress(contents_a) == gzip.decompress(concat)


with open(filename_b, "rb") as f:
	contents_b = f.read()

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
suffix += makeHeader(len(archivesA[0]) + 10 + 16, mtime=b"JUMP")
suffix += lp
suffix += archivesA[0]
for arc in archivesA[1:]:
	suffix += makeHeader(10 + 16, mtime=b"JMPb")
	suffix +=   lp
	suffix +=   makeHeader(len(arc) + 10 + 16, mtime=b"JMPc")
	suffix += lp
	suffix += arc
suffix += boom
suffix += lp
suffix += contents_b


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
