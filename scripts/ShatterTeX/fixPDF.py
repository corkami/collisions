#!/usr/bin/env python3

# copies the first 8 objects of a Shattered-PDF and adjust XREF
import sys
import hashlib

comment = """
/==============\\
|*            *|
|   Shattered  |
| Chosen Prefix|
|     SHA1     |
|  Collision   |
| via PDFLaTeX |
|*            *|
|Ange Albertini|
|     and      |
| Marc Stevens |
|              |
|*            *|
\==============/"""

with open(sys.argv[1], "rb") as f:
  tex = f.read()
with open("prefix.pd_", "rb") as f:
  sha = f.read()

sha = sha[:sha.find(b"9 0 obj")]

iTEX = tex.find(b"8 0 obj")

# in my PDF TeX, object 8 was followed by object 11 ?!
iTEX = tex.find(b"endobj", iTEX) + 6

assert iTEX >= len(sha)

out = sha + (iTEX - len(sha)) * b"\n" + tex[iTEX:]

# now we fix XREF for the eight first object, and not changing anything else

iXREF = out.rfind(b"\nxref\n") + 6
iXREFend = out.rfind(b"\ntrailer\n")

#from the XREF on, it's usually text file
xLines = out[iXREF:iXREFend].splitlines()

for i in range(8):
  offset = out.find(b"\n%i 0 obj" % (i + 1)) + 1
  xLines[i + 2] = b"%010i 00000 n " % offset

out1 = out[:iXREF] + "\n".join(xLines) + out[iXREFend:]


# add comment in the header
comment = comment.replace(b"\n", b"")
comment = comment.replace(b"\r", b"")

assert len(comment) % 16 == 0

assert out1[0x140:0x140 + len(comment)] == b"\0" * len(comment)

out1 = out1[:0x140] + comment + out1[0x140 + len(comment):]


with open("shattered1.pdf", "wb") as f:
  f.write(out1)


# generate the colliding file

BLOCK_START = 3
BLOCK_END = 5
blocks = list(out1[64*BLOCK_START:64 * BLOCK_END])

mask = [
  0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x3c, 0x00, 0x00, 0x04,
  0xbc, 0x00, 0x00, 0x1a, 0x20, 0x00, 0x00, 0x10, 0x24, 0x00, 0x00, 0x1c, 0xec, 0x00, 0x00, 0x14,
  0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x2c, 0x00, 0x00, 0x04,
  0xbc, 0x00, 0x00, 0x18, 0xb0, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x0c, 0xb8, 0x00, 0x00, 0x10]

for i,j in enumerate(blocks):
  blocks[i] = chr(ord(j) ^ mask[i % 64])

out2 = out1[:64 * BLOCK_START] + b"".join(blocks) + out1[64*BLOCK_END:]

assert hashlib.sha1(out1).digest() == hashlib.sha1(out2).digest()

# enable this to test the collided file
with open("shattered2.pdf", "wb") as f:
  f.write(out2)
