#!/usr/bin/env python3

DESCRIPTION = "Set rendered hex value in Rogdham's GIF hashquine."

# Ange Albertini 2023

from collisions import *
from argparse import ArgumentParser
import random
import hashlib

HEX_BASE = 16
MD5_LEN = 32
VALUES_PER_NIBBLE = 16

HEADER_S = 155072
HEADER_MD5 = 'eb34bbfe1c8e07c7f64f285e5c9bc10d'

# 416 fastcolls (= 26*16 - 26 characters, 6 are set by "M*d5* is *dead*")
block_indexes = [
    68, 74, 79, 84, 90, 96, 102, 108, 114, 119, 125, 131, 137, 142, 147, 153,
    158, 164, 170, 176, 182, 187, 193, 199, 204, 210, 216, 222, 228, 234, 240,
    245, 251, 256, 261, 267, 273, 279, 285, 291, 296, 301, 306, 311, 316, 322,
    328, 333, 338, 344, 350, 356, 362, 367, 373, 379, 385, 391, 397, 403, 409,
    415, 421, 427, 433, 439, 445, 450, 456, 462, 468, 474, 480, 486, 491, 496,
    502, 507, 512, 518, 523, 528, 534, 540, 546, 551, 556, 561, 566, 571, 576,
    582, 588, 594, 600, 606, 612, 618, 624, 630, 635, 640, 646, 651, 656, 662,
    668, 674, 680, 686, 692, 697, 703, 709, 715, 721, 727, 732, 738, 744, 749,
    755, 760, 766, 772, 778, 784, 789, 794, 800, 806, 811, 816, 822, 827, 833,
    839, 844, 850, 855, 861, 866, 872, 877, 883, 889, 894, 900, 906, 912, 917,
    923, 929, 935, 941, 947, 953, 958, 964, 970, 976, 981, 987, 993, 999, 1004,
    1009, 1014, 1019, 1025, 1031, 1037, 1043, 1049, 1054, 1060, 1066, 1072,
    1078, 1083, 1088, 1094, 1100, 1105, 1111, 1116, 1122, 1127, 1133, 1139,
    1145, 1151, 1156, 1162, 1168, 1174, 1180, 1186, 1191, 1196, 1201, 1207,
    1213, 1219, 1225, 1231, 1236, 1241, 1246, 1251, 1257, 1262, 1268, 1273,
    1279, 1284, 1289, 1294, 1300, 1306, 1312, 1318, 1323, 1328, 1333, 1338,
    1343, 1348, 1353, 1359, 1364, 1370, 1376, 1381, 1386, 1392, 1397, 1403,
    1409, 1415, 1421, 1427, 1433, 1439, 1444, 1449, 1455, 1460, 1465, 1471,
    1477, 1482, 1488, 1494, 1500, 1506, 1511, 1516, 1522, 1528, 1534, 1539,
    1545, 1551, 1556, 1561, 1567, 1573, 1579, 1585, 1591, 1597, 1603, 1609,
    1615, 1620, 1626, 1632, 1638, 1644, 1650, 1656, 1662, 1668, 1673, 1679,
    1685, 1691, 1697, 1703, 1709, 1714, 1719, 1725, 1731, 1737, 1742, 1747,
    1753, 1759, 1765, 1771, 1776, 1782, 1787, 1793, 1799, 1804, 1810, 1816,
    1821, 1827, 1833, 1838, 1843, 1849, 1854, 1859, 1865, 1871, 1877, 1883,
    1888, 1894, 1900, 1906, 1911, 1916, 1922, 1928, 1934, 1939, 1944, 1949,
    1955, 1961, 1967, 1973, 1979, 1984, 1989, 1995, 2001, 2007, 2013, 2019,
    2025, 2031, 2037, 2043, 2049, 2055, 2061, 2067, 2072, 2077, 2083, 2088,
    2093, 2099, 2104, 2110, 2116, 2122, 2128, 2134, 2140, 2146, 2151, 2157,
    2163, 2168, 2174, 2180, 2186, 2191, 2197, 2203, 2209, 2214, 2220, 2225,
    2231, 2237, 2242, 2248, 2253, 2259, 2265, 2271, 2277, 2283, 2288, 2293,
    2299, 2305, 2311, 2316, 2321, 2327, 2332, 2338, 2344, 2350, 2356, 2361,
    2367, 2373, 2379, 2385, 2391, 2397, 2403, 2409, 2415, 2421
]

# 00000000001111111111222222222233
# 01234567890123456789012345678901
#
#           md5 is dead!
# 22d058dd8aad588cadeadf33e6c9977e
#           ]12[  ]1234[

#           ][  ][
# 22d058dd8aa88caf33e6c9977e


def reduce(input):
    assert len(input) == 32
    output = input[:11] + input[13:17] + input[21:]
    assert len(output) == 26
    return output


def expand(input):
    assert len(input) == 26
    output = input[:11] + 'd5' + input[11:15] + 'dead' + input[15:]
    assert len(output) == 32
    return output


def main():
    parser = ArgumentParser(description=DESCRIPTION)
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

    print("Patched hex value: %s" % (expand(reduce(hex_value))))

    for block_index in block_indexes:
        data = setFastCollbySize(data,
                                 block_index,
                                 bSmaller=False,
                                 DIFF_BYTE=0x7B)
        
    for letter_index, letter in enumerate(reduce(hex_value)):
        value = int(letter, HEX_BASE)
        block_index = letter_index * VALUES_PER_NIBBLE + value
        data, _ = setFastcoll(data, block_indexes[block_index])

    with open("output.gif", "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main()
