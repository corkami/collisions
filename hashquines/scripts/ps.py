#!/usr/bin/env python3

# Sets the value of Greg's PS hashquine

# Ange Albertini 2022-2023

import hashlib
import random

from argparse import ArgumentParser
from collisions import setFastcoll

HEX_BASE = 16
MD5_LEN = 32
HEADER_S = 41344
HEADER_MD5 = '54add7e1da7b2a31b5a5900be13622df'
FULL_MD5 = '768d9d89d2bc825a319eb8962ad30580'
# This hashquine has 128 evenly spaced collisions.
block_idx = lambda i: 9 + i * 5


def get_bits(s):
    return '{md5:0>128b}'.format(md5=int("0x" + s, 16))


def flip_bits(d, bits):
    for i, j in enumerate(bits):
        d, _ = setFastcoll(d, block_idx(i), sideB=j == "1")
    return d


def main():
    parser = ArgumentParser(description="Sets value in Evan's NES hashquine")
    parser.add_argument('-v',
                        '--value',
                        type=str,
                        nargs='?',
                        const=random,
                        help='Hex value to encode (random if not specified)')

    parser.add_argument("filename")
    args = parser.parse_args()

    fn = args.filename
    with open(fn, "rb") as f:
        data = bytearray(f.read())
    assert hashlib.md5(data).hexdigest() == FULL_MD5

    # check we have the right file
    assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5
    print('Original NES hashquine file found')
    print('Resetting Fastcoll blocks')

    if args.value is not None:
        if args.value == random:
            hex_value = "".join(
                [random.choice("0123456789abcdef") for _ in range(MD5_LEN)])
            print("Encoding random value: %s" % hex_value)
        else:
            hex_value = "%032x" % int(args.value, HEX_BASE)
            hex_value = hex_value[:MD5_LEN]
            print("Encoding requested value: `%s` (len:%i)" %
                  (hex_value, len(hex_value)))
    else:
        hex_value = hashlib.md5(data).hexdigest()
        print("Encoding file MD5: `%s` (len:%i)" % (hex_value, len(hex_value)))

    reset_bits = get_bits(hex_value)[::-1]
    data = flip_bits(data, reset_bits)

    assert hashlib.md5(data).hexdigest() == FULL_MD5
    with open("output.ps", "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main()
