#!/usr/bin/env python3

# Reusable MD5 collision for .GZ
#  via pre-computed UniColl prefixes

# Ange Albertini 2021

# 2021/10/17: - first release
# 2021/10/18: - splitting members of top file if too big.
# 2021/10/20: - splitting bottom file for warning-less decompression.
#             - prefix ordering


# Archive: T (Trampoline header) + [gap] + LP (LandingPad)
# T: 16 bytes
# LP: 2 + 4 + 4 = 10 bytes
# Sa0 = Size of member A0

# 000: Aalign                          vvv Prefix vvv
# 03E: Tunicoll
#       /    \  (jumps short or long) 
# 0C0: LPs_   \                        vvv Suffix vvv
#          Ta  \     (0x100)           (truncated)
#         /     \    <gap>
# 1C0:   /     LPl_
#       /          T (10 + Sa1 + 16)   vvv no more gap vvv
#      LP         /
#      Aa0       /
#      T        /    (10 + 16)
#      |      LP_
#      |         T   (10 + Sa1 + 16)
#      LP       /
#      Aa1     /
#      ...   ...
#      T      /      (10+16)
#      |     LP__
#      |         T   (10 + SaN + 16)
#      LP       /
#      An      /                  <-- archive A is over
#                                     -> end the parsing cleanly
#         T   /      (10 + Sb0 + 16)
#        /   LP
#       /    Ba0
#      /     T       (10 + 16)
#    LP__    |
#     ...    ...
#        T   |       (10 + Sb1 + 16)
#       /    LP
#      /     Ba1
#     /      T       (10 + 16)
#    LP_     |
#       T    |       (10 + SbN + 16)
#        \   LP
#         \  BaN
#          \_T       (0)   \ common end
#            LP            /

# Between each Ai..Aj:
# T(10+16),                 , LP
#           LP, T(10+Saj+16),

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

# All landing pads are identical
LP = b"".join([
	b"\3\0",     # Body [empty data]
	b"\0\0\0\0", # CRC32
	b"\0\0\0\0", # USize32
])

# Gzip terminates when indicating 2 characters - since Gzip signature is 2 bytes
# should be non null, should not be 1F 8B

# Make Boom a length of 16 to simplify the loop
boom = 8 * b"AA"

MAXEF = 0xffff - 2 - 2

def slice_archive(archive, chunk_l=int(MAXEF * 2.0)):
	"""slice in members of arbitrary - small - uncompressed length"""
	uncomp_data = gzip.decompress(archive)
	uncomp_l = len(uncomp_data)
	comp_factor = uncomp_l // chunk_l

	members = []
	for i in range(comp_factor - 1):
		members.append(gzip.compress(uncomp_data[chunk_l * i:chunk_l * (i+1)], mtime=0))
	members.append(gzip.compress(uncomp_data[chunk_l * (comp_factor-1):], mtime=0))
	return members


def split_member(member):
	"""split members by compressing data in halves"""
	data = gzip.decompress(member)
	l = len(data)
	d1 = data[:l//2]
	d2 = data[l//2:]
	a1 = gzip.compress(d1, mtime=0)
	a2 = gzip.compress(d2, mtime=0)
	return a1, a2


def split_members(members):
	"""split members until they're small enough"""
	while True:
		for i, member in enumerate(members):
			if len(member) > MAXEF:
				member1, member2 = split_member(member)
				members[i] = member2
				members.insert(i, member1)
				break
		else:
			break
	return members


def test_members(archive, members):
	concat = b""
	for member in members:
		assert len(member) <= 0xfffe
		concat += member
	assert gzip.decompress(archive) == gzip.decompress(concat)


def process(contents):
	if len(contents) <= MAXEF:
		members = [contents]
	else:
		members = slice_archive(contents)
		members = split_members(members)
		test_members(contents, members)
	return members


with open(filename_a, "rb") as f:
	contents_a = f.read()
membersA = process(contents_a)

if len(membersA) > 1:
	print("%s (%i bytes): split in %i members" % (args.file1, len(contents_a), len(membersA)))

with open(filename_b, "rb") as f:
	contents_b = f.read()
membersB = process(contents_b)
if len(membersB) > 1:
	print("%s (%i bytes): split in %i members" % (args.file2, len(contents_b), len(membersB)))

suffix = LP
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
suffix += LP
suffix += makeHeader(len(membersA[0]) + 10 + 16, mtime=b"JUMP")
suffix += LP
suffix += membersA[0]

for member in membersA[1:]:
	suffix += makeHeader(10 + 16, mtime=b"JMPb")
	suffix +=   LP
	suffix +=   makeHeader(len(member) + 10 + 16, mtime=b"JMPc")
	suffix += LP
	suffix += member

for member in membersB[:-1]:
	suffix += makeHeader(len(member) + 10 + 16, mtime=b"JMPe")
	suffix +=   LP
	suffix +=   member
	suffix +=  makeHeader(10 + 16, mtime=b"JMPd")
	suffix += LP

suffix += makeHeader(len(membersB[-1]) + 10 + 16, mtime=b"JMPe")
suffix +=   LP
suffix +=   membersB[-1]
suffix += makeHeader(0, mtime=b"END_") # required to end on the same LP
suffix += LP


with open("prefix1.gz", "rb") as f:
	prefix1 = f.read()
with open("prefix2.gz", "rb") as f:
	prefix2 = f.read()

assert len(prefix1) % 64 == 0

def check_pair(d1, d2):
	assert prefix1 != prefix2
	assert len(prefix1) == len(prefix2)
	assert hashlib.md5(prefix1).hexdigest() == hashlib.md5(prefix2).hexdigest()

check_pair(prefix1, prefix2)

DIFF_o = -0x77 # first diff in first UniColl block

# is prefix1 the short jump ?
if prefix1[DIFF_o] - 1 == prefix2[DIFF_o]:
	prefix1, prefix2 = prefix2, prefix1

assert prefix1[DIFF_o] + 1 == prefix2[DIFF_o]

data1 = prefix1 + suffix
data2 = prefix2 + suffix

assert gzip.decompress(contents_a) == gzip.decompress(data1)
assert gzip.decompress(contents_b) == gzip.decompress(data2)
check_pair(data1, data2)
print("Success!")

with open("coll-1.gz", "wb") as f:
	f.write(data1)
with open("coll-2.gz", "wb") as f:
	f.write(data2)

print(hashlib.md5(data1).hexdigest())
print("coll-1.gz => %s" % filename_a)
print("coll-2.gz => %s" % filename_b)
