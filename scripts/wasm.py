#!/usr/bin/env python3

# Reusable MD5 collision for Wasm files
#  via pre-computed UniColl prefixes

# Ange Albertini 2023

import argparse
import hashlib
import sys

FILETYPE = 'WebAssembly'
MAGIC = b"\0asm\1\0\0\0"
EXT = 'wasm'

parser = argparse.ArgumentParser(description="Generate %s MD5 collisions." % (FILETYPE))
parser.add_argument('file1', help="first 'top' input file.")
parser.add_argument('file2', help="second 'bottom' input file.")

args = parser.parse_args()
filename_a = args.file1
filename_b = args.file2


def toLEB128(n):
    buf = []
    while True:
        out = n & 0x7f
        n >>= 7
        if n:
            buf += [out | 0x80]
        else:
            buf += [out]
            break
    return bytes(buf)

assert toLEB128(256) == b'\x80\x02'
assert toLEB128(197) == b'\xC5\x01'
assert toLEB128(129) == b'\x81\x01'
assert toLEB128(128) == b'\x80\x01'
assert toLEB128(127) == b'\x7f'


CUSTOM_SECTION = b"\0"

def wrapper(length, name=b""):
    header = len(name).to_bytes(1, "little") + name
    header = b""
    section = CUSTOM_SECTION + toLEB128(len(header) + length)
    return section


def wrap(parasite, name=b""):
    wrapped = wrapper(len(parasite), name) + parasite
    return wrapped


def check_magic(contents):
    return contents.startswith(MAGIC)


with open(filename_a, "rb") as f:
    contents_a = f.read()

if check_magic(contents_a) == False:
    print("Error: File A (%s) is not a valid %s file." %
          (filename_b, FILETYPE))
    sys.exit(1)
sections_a = contents_a[8:]

with open(filename_b, "rb") as f:
    contents_b = f.read()

if check_magic(contents_a) == False:
    print("Error: File B (%s) is not a valid %s file." %
          (filename_b, FILETYPE))
    sys.exit(1)

sections_b = contents_b[8:]

with open('wasm1.bin', "rb") as f:
    prefix_s = f.read()
with open('wasm2.bin', "rb") as f:
    prefix_l = f.read()

assert hashlib.md5(prefix_s).digest() == hashlib.md5(prefix_l).digest()
assert hashlib.sha1(prefix_s).digest() != hashlib.sha1(prefix_l).digest()

wrapped_b = wrap(sections_b)

# MD5 constant
BLOCK_SIZE = 0x40


# For this prefix pair:

# index of the first unicoll block
UNICOLL_INDEX = 1
# incremented position in the unicoll block
UNICOLL_INCPOS = 0x9

# Landing offset after the Increment position
DELTA = 1

# Jump between the 2 unicoll blocks - usually 0x100
UNICOLL_GAP = 0x80 # because the increment is on a leb128


jump = UNICOLL_GAP - 1 + len(sections_a)
jump128 = len(toLEB128(jump))

prewrap_b = len(wrap(sections_b)) - len(sections_b)
suffix = b"".join([
    # Unicoll (0xC0) and landing () gap between Unicoll
    b">" * ((UNICOLL_INDEX * BLOCK_SIZE + UNICOLL_INCPOS + DELTA + UNICOLL_GAP) - (UNICOLL_INDEX + 2) * BLOCK_SIZE),
    CUSTOM_SECTION,
    toLEB128(jump - jump128 + prewrap_b),
    b"<" * (UNICOLL_GAP - 1 - jump128),
    sections_a,
    wrap(sections_b),
])

coll_s = prefix_s + suffix
coll_l = prefix_l + suffix
assert hashlib.md5(coll_s).digest() == hashlib.md5(coll_l).digest()
assert hashlib.sha1(coll_s).digest() != hashlib.sha1(coll_l).digest()

hash = hashlib.md5(coll_s).hexdigest()[:8]
cn1 = "coll1-%s.%s" % (hash, EXT)
cn2 = "coll2-%s.%s" % (hash, EXT)

with open(cn1, "wb") as f:
    f.write(coll_s)
with open(cn2, "wb") as f:
    f.write(coll_l)

print("Collision successful: %s / %s" % (cn1, cn2))
