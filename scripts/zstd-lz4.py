#!/usr/bin/env python3

# Reusable MD5 collision for Zstd/Lz4 files
#  via pre-computed UniColl prefixes

# Ange Albertini 2023

import argparse
import hashlib
import sys

parser = argparse.ArgumentParser(
    description="Generate Zstd/lz4 MD5 collisions.")
parser.add_argument('file1', help="first 'top' input file.")
parser.add_argument('file2', help="second 'bottom' input file.")

args = parser.parse_args()
filename_a = args.file1
filename_b = args.file2


def check_magic(contents):
    magics = [
        [0x28, 0xB5, 0x2F, 0xFD],  # Zstd Magic
        [0x04, 0x22, 0x4D, 0x18],  # LZ4 Magic
        [0x50, 0x2A, 0x4D, 0x18],  # Skippable Frame 0
        [0x51, 0x2A, 0x4D, 0x18],  # Skippable Frame 1
        [0x52, 0x2A, 0x4D, 0x18],  # Skippable Frame 2
        [0x53, 0x2A, 0x4D, 0x18],  # Skippable Frame 3
        [0x54, 0x2A, 0x4D, 0x18],  # Skippable Frame 4
        [0x55, 0x2A, 0x4D, 0x18],  # Skippable Frame 5
        [0x56, 0x2A, 0x4D, 0x18],  # Skippable Frame 6
        [0x57, 0x2A, 0x4D, 0x18],  # Skippable Frame 7
        [0x58, 0x2A, 0x4D, 0x18],  # Skippable Frame 8
        [0x59, 0x2A, 0x4D, 0x18],  # Skippable Frame 9
        [0x5A, 0x2A, 0x4D, 0x18],  # Skippable Frame A
        [0x5B, 0x2A, 0x4D, 0x18],  # Skippable Frame B
        [0x5C, 0x2A, 0x4D, 0x18],  # Skippable Frame C
        [0x5D, 0x2A, 0x4D, 0x18],  # Skippable Frame D
        [0x5E, 0x2A, 0x4D, 0x18],  # Skippable Frame E
        [0x5F, 0x2A, 0x4D, 0x18],  # Skippable Frame F
    ]
    for magic in magics:
        if contents.startswith(bytearray(magic)):
            return True
    else:
        return False


def makeSkipFrameHdr(l):
    return bytearray([0x50, 0x2A, 0x4D, 0x18]) + l.to_bytes(4, "little")


def makeSkipFrame(contents):
    return makeSkipFrameHdr(len(contents)) + contents


with open(filename_a, "rb") as f:
    contents_a = f.read()

if check_magic(contents_a) == False:
    print("Error: File B (%s) is not a valid Zstandard/LZ4 file." %
          (filename_b))
    sys.exit(1)

with open(filename_b, "rb") as f:
    contents_b = f.read()

if check_magic(contents_a) == False:
    print("Error: File B (%s) is not a valid Zstandard/LZ4 file." %
          (filename_b))
    sys.exit(1)

with open('zstdlz4-s.bin', "rb") as f:
    prefix_s = f.read()
with open('zstdlz4-l.bin', "rb") as f:
    prefix_l = f.read()
assert hashlib.md5(prefix_s).digest() == hashlib.md5(prefix_l).digest()
assert hashlib.sha1(prefix_s).digest() != hashlib.sha1(prefix_l).digest()

## 0C0: MMMM 1111 .... ....
## 1C0: AA..AA MMMM 2222 BB..BB

suffix = b"".join([
    makeSkipFrameHdr(0xF8 + len(contents_a) + 8),
    b"\0" * (0xF8),
    contents_a,
    makeSkipFrame(contents_b),
])

coll_s = prefix_s + suffix
coll_l = prefix_l + suffix
assert hashlib.md5(coll_s).digest() == hashlib.md5(coll_l).digest()
assert hashlib.sha1(coll_s).digest() != hashlib.sha1(coll_l).digest()

hash = hashlib.md5(coll_s).hexdigest()[:8]
cn1 = "coll1-%s.zstd" % hash
cn2 = "coll2-%s.zstd" % hash

with open(cn1, "wb") as f:
    f.write(coll_s)
with open(cn2, "wb") as f:
    f.write(coll_l)

print("Collision successful: %s / %s" % (cn1, cn2))
