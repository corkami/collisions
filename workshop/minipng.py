#!/usr/bin/env python3

# png chunks reader/writer

# Ange Albertini, BSD Licence, 2011-2021

import struct
import binascii

_MAGIC = b"\x89PNG\x0d\x0a\x1a\x0a"

_crc32 = lambda d:(binascii.crc32(d) % 0x100000000)

def read(f):
    """gets a file, returns a list of [type, data] chunks"""
    assert f.read(8) == _MAGIC

    chunks = []
    while (True):
        l, = struct.unpack(">I", f.read(4))
        t = f.read(4)
        d = f.read(l)
        assert _crc32(t + d) == struct.unpack(">I", f.read(4))[0]

        chunks += [[t, d]]

        if t == b"IEND":
            return chunks

    raise(BaseException("Invalid image"))


def make(chunks):
    """returns a PNG binary string from a list of [type, data] PNG chunks"""
    s = [_MAGIC]
    for t, d in chunks:
        assert len(t) == 4
        s += [
            struct.pack(">I", len(d)),
            t,
            d,
            struct.pack(">I", _crc32(t + d))
            ]
    return b"".join(s)


fno = "no.png"
with open(fno, "rb") as f:
    no = read(f)

fyes = "yes.png"
with open(fyes, "rb") as f:
    yes = read(f)

# SPOILER
# (not entirely correct but in the right direction)
final = [
    [b"aLIG", 0x33*b"\0"], 
    [b"cOLL", 0x71*b"\0"], 
    ] + no + yes
with open("final.png", "wb") as f:
    f.write(make(final))
