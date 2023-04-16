#!/usr/bin/env python3

# Sets the hex value of SPQ's Gif 2*8 segment display hashquine

# Ange Albertini 2023

import hashlib
import random

HEX_BASE = 16
MD5_LEN = 32
HEADER_S = 85376
HEADER_MD5 = '6cc83e8357bd1a75b9f2005ba6fab928'

from argparse import ArgumentParser
from collisions import *

#  1
# 2 3
#  4
# 5 6
#  7
display = {
    '0': '1110111',
    '1': '0010010',
    '2': '1011101',
    '3': '1011011',
    '4': '0111010',
    '5': '1101011',
    '6': '1101111',
    '7': '1010010',
    '8': '1111111',
    '9': '1111011',
    'a': '1111110',
    'b': '0101111',
    'c': '1100101',
    'd': '0011111',
    'e': '1101101',
    'f': '1101100',
}


def test_segments():
    for l in display:
        segments = display[l]
        print(l)
        print(" - " if segments[0] == '1' else "   ")
        print("|" if segments[1] == '1' else ' ', end=' ')
        print("|" if segments[2] == '1' else ' ')
        print(" - " if segments[3] == '1' else "   ")
        print("|" if segments[4] == '1' else ' ', end=' ')
        print("|" if segments[5] == '1' else ' ')
        print(" - " if segments[6] == '1' else "   ")
        print()


flips = [
    0, 1, 3, 4, 7, 8, 10, 12, 13, 14, 15, 18, 20, 21, 22, 23, 24, 25, 26, 29,
    30, 31, 33, 35, 36, 38, 39, 42, 43, 44, 45, 47, 48, 49, 51, 52, 54, 55, 56,
    57, 59, 61, 62, 65, 66, 67, 68, 69, 71, 72, 73, 75, 78, 79, 80, 82, 85, 87,
    88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 101, 103, 104, 105, 106,
    109, 111, 113, 114, 115, 117, 119, 121, 122, 124, 125, 128, 131, 133, 134,
    135, 136, 137, 138, 140, 141, 142, 143, 144, 145, 146, 148, 150, 151, 152,
    153, 154, 155, 157, 158, 161, 162, 163, 166, 168, 169, 170, 171, 172, 173,
    174, 175, 176, 177, 178, 179, 180, 181, 182, 183, 186, 188, 189, 190, 191,
    193, 194, 195, 196, 197, 199, 200, 202, 203, 204, 205, 206, 207, 208, 210,
    211, 214, 216, 217, 218, 219, 220, 221, 222
]

block_indexes = [
    86, 92, 98, 104, 110, 116, 122, 128, 134, 140, 145, 151, 156, 161, 167,
    172, 178, 184, 189, 195, 201, 206, 212, 217, 222, 228, 233, 239, 245, 251,
    256, 262, 267, 273, 278, 284, 289, 295, 301, 307, 312, 317, 323, 328, 334,
    339, 344, 350, 356, 362, 368, 374, 380, 385, 391, 397, 403, 409, 414, 420,
    426, 432, 437, 443, 448, 453, 459, 465, 471, 476, 481, 486, 492, 498, 504,
    510, 516, 521, 527, 533, 539, 545, 551, 556, 562, 568, 573, 579, 584, 589,
    595, 601, 607, 613, 618, 624, 629, 634, 640, 645, 651, 656, 661, 666, 671,
    676, 682, 688, 694, 699, 704, 709, 715, 721, 727, 733, 739, 745, 750, 755,
    760, 765, 771, 776, 782, 788, 793, 799, 805, 811, 817, 823, 828, 833, 838,
    844, 850, 855, 861, 866, 872, 877, 882, 887, 893, 898, 904, 909, 914, 919,
    925, 931, 937, 943, 948, 953, 959, 964, 969, 975, 981, 986, 992, 997, 1003,
    1009, 1014, 1019, 1024, 1030, 1036, 1042, 1047, 1053, 1059, 1064, 1070,
    1076, 1081, 1086, 1092, 1097, 1103, 1108, 1114, 1120, 1125, 1131, 1137,
    1143, 1149, 1155, 1161, 1167, 1172, 1177, 1182, 1187, 1193, 1198, 1204,
    1210, 1215, 1220, 1225, 1231, 1236, 1242, 1248, 1253, 1259, 1264, 1269,
    1274, 1280, 1286, 1291, 1297, 1303, 1309, 1314, 1320, 1326, 1332
]


def get_flips():
    flips = []
    FULL_HASH = "f5ca4f935d44b85c431a8bf788c0eaca"
    for letter_index, letter in enumerate(FULL_HASH):
        segments = display[letter]
        for bit_index, bit in enumerate(segments):
            if bit == "1":
                flips += [letter_index * 7 + bit_index]
    return flips


def main():
    flips = get_flips()

    parser = ArgumentParser(
        description="Set values in SPQ's 'display' GIF hashquine.")
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

    assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5
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

    for letter_index, letter in enumerate(hex_value):
        for segment_index, segment in enumerate(display[letter]):
            block_index = letter_index * 7 + segment_index
            if (block_index not in flips) == (segment == '1'):
                data, _ = setFastcoll(data, block_indexes[block_index])

    with open("output.gif", "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main()
