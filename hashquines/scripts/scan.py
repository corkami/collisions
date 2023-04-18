#!/usr/bin/env python3

DESCRIPTION = "Shows IPC MD5 collisions (Fastcolls and Unicolls) of a given file."

# Ange Albertini 2023

import hashlib

from argparse import ArgumentParser
from collisions import *


def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-a',
                        '--all',
                        action='store_true',
                        help='Show all collision indexes')
    parser.add_argument(
        '-f',
        '--flip',
        type=int,
        nargs='?',
        const=hashlib,
        help='Flip all collision blocks [to a given side, 0 or 1]')

    parser.add_argument("filename")
    args = parser.parse_args()

    fn = args.filename
    with open(fn, "rb") as f:
        data = bytearray(f.read())
    FULL_MD5 = hashlib.md5(data).hexdigest()
    # print("FULL_MD5 = '%s'" % (FULL_MD5))

    fc_blkidxs, fc_sidesB = getFastColls(data)
    print("Found %i FastColls." % (len(fc_blkidxs)))

    uc_blkidxs, uc_sidesB = getUniColls(data)
    print("Found %i UniColls." % (len(uc_blkidxs)))

    if args.all:
        if fc_blkidxs:
            print("FastColls", fc_blkidxs, fc_sidesB)
        if uc_blkidxs:
            print("UniColls:", uc_blkidxs, uc_sidesB)

    last_block = -1
    last_block = max(fc_blkidxs + [last_block])
    last_block = max(uc_blkidxs + [last_block])
    if last_block > -1:
        print("Last collision block index: %i" % (last_block))
        HEADER_S = (last_block + 2) * 0x40
        HEADER_MD5 = hashlib.md5(data[:HEADER_S]).hexdigest()
        print("HEADER_S = %i" % (HEADER_S))
        print("HEADER_MD5 = '%s'" % (HEADER_MD5))
    else:
        print("No collision found")

    if args.flip is not None:
        if args.flip == hashlib:
            sideB = None
            print("Flipping all collisions")
        else:
            sideB = args.flip != 0
            print("Setting all collisions to side %i" % (1 if sideB else 0))
        assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5
        if fc_blkidxs:
            for _, block_index in enumerate(fc_blkidxs):
                data, _ = setFastcoll(data, block_index, sideB)
        if uc_blkidxs:
            for _, block_index in enumerate(uc_blkidxs):
                data, _ = setUniColl(data, block_index, sideB)
        assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5
        with open("test.bin", "wb") as f:
            f.write(data)


if __name__ == '__main__':
    main()
