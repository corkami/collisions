#!/usr/bin/env python3

DESCRIPTION = "Change filetypes of PoC or GTFO 0x14 (MD5 NES/PDF hashquine + collision)."

# Ange Albertini 2023

import hashlib
import random
from argparse import ArgumentParser
from collisions import *


TARGET = 'pocorgtfo14.pdf'
HEX_BASE = 16
MD5_LEN = 32


indexes_NES = list(135+2*i for i in range(128))

# small byte = skip next jpeg scan
# big byte = parse next jpeg scan
indexes_PDF = [
    654,   722,   764,   833,   903,   961,  1024,  1099,  1149,  1230,  1304,  1369,  1436,  1503,  1564,
    1719,  1786,  1826,  1895,  1965,  2022,  2085,  2159,  2210,  2291,  2366,  2430,  2497,  2563,  2624,
    2784,  2852,  2894,  2962,  3032,  3090,  3153,  3226,  3277,  3356,  3431,  3494,  3561,  3627,  3688,
    3849,  3916,  3956,  4024,  4093,  4151,  4214,  4288,  4338,  4418,  4493,  4557,  4624,  4692,  4754,
    4914,  4982,  5023,  5091,  5160,  5219,  5282,  5357,  5408,  5488,  5563,  5627,  5694,  5761,  5822,
    5980,  6048,  6089,  6156,  6227,  6286,  6349,  6423,  6474,  6554,  6628,  6691,  6757,  6823,  6884,
    7045,  7113,  7154,  7223,  7292,  7350,  7413,  7488,  7539,  7618,  7692,  7756,  7822,  7888,  7949,
    8110,  8178,  8220,  8289,  8359,  8418,  8481,  8555,  8606,  8686,  8760,  8825,  8892,  8959,  9021,
    9175,  9243,  9284,  9351,  9421,  9478,  9541,  9616,  9667,  9747,  9822,  9886,  9953, 10019, 10081,
    10240, 10306, 10346, 10415, 10485, 10542, 10605, 10679, 10730, 10809, 10884, 10949, 11016, 11083, 11144,
    11305, 11373, 11414, 11481, 11552, 11609, 11671, 11746, 11797, 11878, 11952, 12016, 12082, 12149, 12210,
    12371, 12438, 12478, 12547, 12617, 12675, 12737, 12812, 12862, 12943, 13018, 13082, 13148, 13215, 13277,
    13436, 13504, 13544, 13613, 13684, 13742, 13804, 13879, 13930, 14011, 14085, 14148, 14215, 14281, 14342,
    14501, 14568, 14608, 14675, 14746, 14803, 14866, 14941, 14992, 15071, 15146, 15210, 15277, 15344, 15406,
    15566, 15632, 15672, 15740, 15810, 15868, 15931, 16005, 16056, 16137, 16212, 16276, 16343, 16410, 16471,
    16631, 16697, 16738, 16807, 16877, 16935, 16998, 17072, 17122, 17201, 17275, 17339, 17406, 17473, 17535,
    17697, 17765, 17805, 17874, 17945, 18004, 18067, 18142, 18193, 18274, 18349, 18412, 18479, 18546, 18607,
    18762, 18829, 18870, 18939, 19010, 19069, 19131, 19206, 19257, 19337, 19412, 19476, 19543, 19611, 19672,
    19827, 19895, 19936, 20004, 20075, 20132, 20194, 20269, 20320, 20399, 20474, 20538, 20605, 20671, 20732,
    20892, 20960, 21001, 21069, 21140, 21198, 21260, 21334, 21385, 21464, 21538, 21601, 21668, 21734, 21796,
    21957, 22025, 22065, 22134, 22205, 22263, 22325, 22399, 22450, 22530, 22604, 22669, 22735, 22802, 22863,
    23022, 23090, 23132, 23201, 23270, 23328, 23391, 23465, 23516, 23595, 23670, 23735, 23801, 23867, 23929,
    24088, 24155, 24196, 24264, 24334, 24392, 24454, 24528, 24578, 24659, 24733, 24797, 24863, 24930, 24992,
    25153, 25221, 25262, 25331, 25402, 25460, 25523, 25597, 25648, 25729, 25804, 25867, 25935, 26001, 26062,
    26218, 26286, 26326, 26393, 26463, 26521, 26584, 26658, 26709, 26789, 26863, 26927, 26994, 27061, 27122,
    27283, 27351, 27393, 27461, 27531, 27588, 27651, 27726, 27777, 27857, 27932, 27995, 28061, 28129, 28189,
    28348, 28415, 28455, 28522, 28593, 28652, 28714, 28789, 28840, 28920, 28995, 29059, 29125, 29192, 29254,
    29413, 29481, 29521, 29589, 29659, 29716, 29779, 29854, 29905, 29985, 30060, 30125, 30192, 30259, 30321,
    30479, 30547, 30587, 30655, 30726, 30785, 30849, 30922, 30972, 31052, 31127, 31192, 31259, 31327, 31389,
    31544, 31612, 31653, 31720, 31790, 31849, 31912, 31986, 32037, 32117, 32192, 32255, 32322, 32388, 32449,
    32609, 32677, 32718, 32786, 32856, 32914, 32978, 33053, 33104, 33185, 33259, 33324, 33390, 33458, 33520,
    33674, 33742, 33783, 33852, 33923, 33981, 34044, 34119, 34169, 34250, 34324, 34389, 34456, 34523, 34585,
]

# sideA = carving, sideB = Mario
index_collision = [34738]

covers = {
    None: "Carving (original)",
    False: "Carving (original)",
    True: "Mario (hidden)",
}

HEADER_S = (34738+2) * BLOCK_SIZE
HEADER_MD5 = "6e066c260f24647290db62900bf4d329"


def get_bits(s) -> str:
    return '{md5:0>128b}'.format(md5=int("0x" + s, 16))


def flip_nes_bits(d: bytearray, bits: str) -> bytearray:
    for i, j in enumerate(bits):
        d, _ = setFastcoll(d, indexes_NES[i] - 1, sideB=j == "0")
    return d


def main() -> None:
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument('-v',
                        '--value',
                        type=str,
                        nargs='?',
                        const=random,
                        help='Hex value to encode (random if not specified)')
    parser.add_argument("filename",
                        nargs='?',
                        type=str,
                        )
    parser.add_argument('-c',
                        '--cover',
                        action="store_true",
                        help='Use alternate cover')
    args = parser.parse_args()

    fn = args.filename
    if fn is None:
        fn = TARGET

    with open(fn, "rb") as f:
        data = bytearray(f.read())
    assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5
    print('Original PoC||GTFO 0x14 file found')

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

    print("Encoding NES hash value")
    reset_bits = get_bits(hex_value)
    data = flip_nes_bits(data, reset_bits)

    print("Encoding PDF hash value")
    for char_index, char in enumerate(hex_value):
        value = int(char, HEX_BASE)
        for bit_idx in range(15):
            idx = char_index * 15 + bit_idx

            data = setFastCollbySize(
                data,
                indexes_PDF[idx] - 1,
                bSmaller=(bit_idx < value))

    print(f"Setting cover: ({covers[args.cover]})")
    data, _ = setFastcoll(data, index_collision[0] - 1, args.cover is not None)

    with open(f"out.pdf", "wb") as f:
        f.write(data)


if __name__ == '__main__':
    main()
