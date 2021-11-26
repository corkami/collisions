#!/usr/bin/env python3

# a zip generator for root prefix.
# abusing the extra field of an empty file to host collision blocks.

# Craft your root files (with forged CRC32s)
# Then run with the name of the root in the archive
# Ex: makezip.py root1 root2 _rels/.rels

# Ange Albertini 2021 - MIT licence

import io
import sys
import zlib

# ZipFile, with no Extra Field written in the Central Directory
import ziphack as z

def collblock(count):
	result = b""
	for _ in range(count + 1):
		result += bytes(range(64))
	return result

ROOT_NAME = sys.argv[3]

# Better keep this file uncompressed and of same length
# so that offsets are guaranteed to be constant
relsfile = z.ZipInfo(filename=ROOT_NAME)

blocks = z.ZipInfo(
	filename="blocks",
	date_time=(2015, 11,13, 21,15,0),
)


field = collblock(10)
blocks.extra = b"AP" + \
	len(field).to_bytes(2, "little") + \
	field


def poc(rels, fn):
	hFile = io.BytesIO()
	with z.ZipFile(hFile, mode='w') as final:
		final.writestr(relsfile, rels)
		final.writestr(blocks, b"\x9c\x7c\xbe\xae") # => 0xC0111DED CRC32

	with open(fn, "wb") as f:
		f.write(hFile.getvalue())


with open(sys.argv[1], "rb") as f1:
	root1 = f1.read()

with open(sys.argv[2], "rb") as f2:
	root2 = f2.read()

# requirements to keep the Central Directory identical
assert root1 != root2
assert zlib.crc32(root1) == zlib.crc32(root2) # == 0XC0111DED
assert len(root1) == len(root2)

poc(root1, "root1.zip")
poc(root2, "root2.zip")
