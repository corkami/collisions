#!/usr/bin/env python3

import hashlib
import pathlib
from argparse import ArgumentParser
# Ange Albertini 2024

DESCRIPTION = "Flip Shattered collision."

BLOCK_SIZE = 0x40
XOR_MASK = [
    0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x3c, 0x00, 0x00, 0x04,
    0xbc, 0x00, 0x00, 0x1a, 0x20, 0x00, 0x00, 0x10, 0x24, 0x00, 0x00, 0x1c, 0xec, 0x00, 0x00, 0x14,
    #
    0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x2c, 0x00, 0x00, 0x04,
    0xbc, 0x00, 0x00, 0x18, 0xb0, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x0c, 0xb8, 0x00, 0x00, 0x10,
]
assert len(XOR_MASK) == BLOCK_SIZE

indexes = [3, 4]
HEADER_S = (indexes[0] + len(indexes)) * BLOCK_SIZE
HEADER_SHA1 = "f92d74e3874587aaf443d1db961d4e26dde13e9c"


def main() -> None:
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument("filename", type=str)
    args = parser.parse_args()

    fn = args.filename

    with open(fn, "rb") as f:
        data = bytearray(f.read())

    assert hashlib.sha1(data[:HEADER_S]).hexdigest() == HEADER_SHA1
    old_sha1 = hashlib.sha1(data).hexdigest()
    print('Shattered prefix found in file: `%s`' % fn)

    print('Flipping collision blocks.')
    l = list(data)
    for index in indexes:
        for i in range(BLOCK_SIZE):
            offset = i + index * BLOCK_SIZE
            l[offset] ^= XOR_MASK[i]
    new_data = bytearray(l)

    print('Verifying hash values:', end='')
    assert new_data != data
    assert hashlib.sha1(new_data[:HEADER_S]).hexdigest() == HEADER_SHA1
    assert hashlib.sha1(new_data).hexdigest() == old_sha1
    print(' ok!')

    new_fn = f"{pathlib.PurePath(fn).stem}-coll{pathlib.PurePath(fn).suffix}"
    print(f'Writing: `{new_fn}`')
    with open(new_fn, "wb") as new_f:
        new_f.write(new_data)


if __name__ == '__main__':
    main()
