#!/usr/bin/env python3

from argparse import ArgumentParser
import random
import hashlib
DESCRIPTION = "Flip Shattered collision."

# Ange Albertini 2024

TARGET = 'pocorgtfo18.pdf'
BLOCK_SIZE = 0x40
MASK = [
    0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x3c, 0x00, 0x00, 0x04,
    0xbc, 0x00, 0x00, 0x1a, 0x20, 0x00, 0x00, 0x10, 0x24, 0x00, 0x00, 0x1c, 0xec, 0x00, 0x00, 0x14,
    #
    0x0c, 0x00, 0x00, 0x02, 0xc0, 0x00, 0x00, 0x10, 0xb4, 0x00, 0x00, 0x1c, 0x2c, 0x00, 0x00, 0x04,
    0xbc, 0x00, 0x00, 0x18, 0xb0, 0x00, 0x00, 0x10, 0x00, 0x00, 0x00, 0x0c, 0xb8, 0x00, 0x00, 0x10,
]
assert len(MASK) == BLOCK_SIZE
indexes = [3, 4]

HEADER_S = (indexes[0]+len(indexes)) * BLOCK_SIZE
HEADER_SHA1 = "f92d74e3874587aaf443d1db961d4e26dde13e9c"


def main() -> None:
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument("filename",
                        nargs='?',
                        type=str,
                        )
    args = parser.parse_args()

    fn = args.filename
    if fn is None:
        fn = TARGET

    with open(fn, "rb") as f:
        data = bytearray(f.read())

    assert hashlib.sha1(data[:HEADER_S]).hexdigest() == HEADER_SHA1
    old_sha1 = hashlib.sha1(data).hexdigest()

    print('Original Shattered prefix file found: %s' % fn)

    print('Flipping collision blocks.')
    l = list(data)
    for index in indexes:
        for i in range(BLOCK_SIZE):
            offset = i + index * BLOCK_SIZE
            l[offset] ^= MASK[i]
    new_data = bytearray(l)

    assert new_data != data

    print('Veryfying hash values.')
    new_sha1 = hashlib.sha1(new_data).hexdigest()
    assert new_sha1 == old_sha1

    with open(f"out.pdf", "wb") as f:
        f.write(new_data)


if __name__ == '__main__':
    main()
