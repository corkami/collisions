#!/usr/bin/env python3

DESCRIPTION = "Create a 'self-checking' tar.zst out of a tar archive."

# takes a tar-based archive
# creates a .tar.zst with a hash.md5 containing the MD5 of all files in the archive
# as well as the MD5 of the .tar.zst archive itself,
# using Retroid's Zstandard 'hashquine'.

# Ange Albertini 2023

import hashlib
import struct
import io
import os
import tarfile
import zstandard
from argparse import ArgumentParser
from collisions import *

# 1. take a .tar.(something)
# 2. extract file paths and their MD5 [check if binary]
# 3. generate hash.md5 with a placeholder value for the archive
# 4. make a tar out of everything
# 5. encode hash.md5 length
# 6. encode tar header checksum
# 7. encode archive hash

HEX_BASE = 16
MD5_LEN = 32

HEADER_S = 292288
HEADER_MD5 = 'a7b9c184887213304fd55f9fb06686aa'

block_indexes = [
    1, 8, 15, 22, 29, 36, 43, 50, 57, 64, 71, 78, 85, 92, 99, 106, 113, 120,
    127, 134, 141, 148, 155, 162, 169, 176, 183, 190, 197, 204, 211, 218, 225,
    232, 239, 246, 253, 260, 267, 274, 281, 288, 295, 302, 309, 316, 323, 330,
    337, 344, 351, 358, 365, 372, 379, 386, 393, 400, 407, 414, 421, 428, 435,
    442, 449, 456, 463, 470, 477, 484, 491, 498, 505, 512, 519, 526, 533, 540,
    547, 554, 561, 568, 575, 582, 589, 596, 603, 610, 617, 624, 631, 638, 645,
    652, 659, 666, 673, 680, 687, 694, 701, 708, 715, 722, 729, 736, 743, 750,
    757, 764, 771, 778, 785, 792, 799, 806, 813, 820, 827, 834, 841, 848, 855,
    862, 869, 876, 883, 890, 897, 904, 911, 918, 925, 932, 939, 946, 953, 960,
    967, 974, 981, 988, 995, 1002, 1009, 1016, 1023, 1030, 1037, 1044, 1051,
    1058, 1065, 1072, 1079, 1086, 1093, 1100, 1107, 1114, 1121, 1128, 1135,
    1142, 1149, 1156, 1163, 1170, 1177, 1184, 1191, 1198, 1205, 1212, 1219,
    1226, 1233, 1240, 1247, 1254, 1261, 1268, 1275, 1282, 1289, 1296, 1303,
    1310, 1317, 1324, 1331, 1338, 1345, 1352, 1359, 1366, 1373, 1380, 1387,
    1394, 1401, 1408, 1415, 1422, 1429, 1436, 1443, 1450, 1457, 1464, 1471,
    1478, 1485, 1492, 1499, 1506, 1513, 1520, 1527, 1534, 1541, 1548, 1555,
    1562, 1569, 1576, 1583, 1590, 1597, 1604, 1611, 1618, 1625, 1632, 1639,
    1646, 1653, 1660, 1667, 1674, 1681, 1688, 1695, 1702, 1709, 1716, 1723,
    1730, 1737, 1744, 1751, 1758, 1765, 1772, 1779, 1786, 1793, 1800, 1807,
    1814, 1821, 1828, 1835, 1842, 1849, 1856, 1863, 1870, 1877, 1884, 1891,
    1898, 1905, 1912, 1919, 1926, 1933, 1940, 1947, 1954, 1961, 1968, 1975,
    1982, 1989, 1996, 2003, 2010, 2017, 2024, 2031, 2038, 2045, 2052, 2059,
    2066, 2073, 2080, 2087, 2094, 2101, 2108, 2115, 2122, 2129, 2136, 2143,
    2150, 2157, 2164, 2171, 2178, 2185, 2192, 2199, 2206, 2213, 2220, 2227,
    2234, 2241, 2248, 2255, 2262, 2269, 2276, 2283, 2290, 2297, 2304, 2311,
    2318, 2325, 2332, 2339, 2346, 2353, 2360, 2367, 2374, 2381, 2388, 2395,
    2402, 2409, 2416, 2423, 2430, 2437, 2444, 2451, 2458, 2465, 2472, 2479,
    2486, 2493, 2500, 2507, 2514, 2521, 2528, 2535, 2542, 2549, 2556, 2563,
    2570, 2577, 2584, 2591, 2598, 2605, 2612, 2619, 2626, 2633, 2640, 2647,
    2654, 2661, 2668, 2675, 2682, 2689, 2696, 2703, 2710, 2717, 2724, 2731,
    2738, 2745, 2752, 2759, 2766, 2773, 2780, 2787, 2794, 2801, 2808, 2815,
    2822, 2829, 2836, 2843, 2850, 2857, 2864, 2871, 2878, 2885, 2892, 2899,
    2906, 2913, 2920, 2927, 2934, 2941, 2948, 2955, 2962, 2969, 2976, 2983,
    2990, 2997, 3004, 3011, 3018, 3025, 3032, 3039, 3046, 3053, 3060, 3067,
    3074, 3081, 3088, 3095, 3102, 3109, 3116, 3123, 3130, 3137, 3144, 3151,
    3158, 3165, 3172, 3179, 3186, 3193, 3200, 3207, 3214, 3221, 3228, 3235,
    3242, 3249, 3256, 3263, 3270, 3277, 3284, 3291, 3298, 3305, 3312, 3319,
    3326, 3333, 3340, 3347, 3354, 3361, 3368, 3375, 3382, 3389, 3396, 3403,
    3410, 3417, 3424, 3431, 3438, 3445, 3452, 3459, 3466, 3473, 3480, 3487,
    3494, 3501, 3508, 3515, 3522, 3529, 3536, 3543, 3550, 3557, 3564, 3571,
    3578, 3585, 3592, 3599, 3606, 3613, 3620, 3627, 3634, 3641, 3648, 3655,
    3662, 3669, 3676, 3683, 3690, 3697, 3704, 3711, 3718, 3725, 3732, 3739,
    3746, 3753, 3760, 3767, 3774, 3781, 3788, 3795, 3802, 3809, 3816, 3823,
    3830, 3837, 3844, 3851, 3858, 3865, 3872, 3879, 3886, 3893, 3900, 3907,
    3914, 3921, 3928, 3935, 3942, 3949, 3956, 3963, 3970, 3977, 3984, 3991,
    3998, 4005, 4012, 4019, 4026, 4033, 4040, 4047, 4054, 4061, 4068, 4075,
    4082, 4089, 4096, 4103, 4110, 4117, 4124, 4131, 4138, 4145, 4152, 4159,
    4166, 4173, 4180, 4187, 4194, 4201, 4208, 4215, 4222, 4229, 4236, 4243,
    4250, 4257, 4264, 4271, 4278, 4285, 4292, 4299, 4306, 4313, 4320, 4327,
    4334, 4341, 4348, 4355, 4362, 4369, 4376, 4383, 4390, 4397, 4404, 4411,
    4418, 4425, 4432, 4439, 4446, 4453, 4460, 4467, 4474, 4481, 4488, 4495,
    4502, 4509, 4516, 4523, 4530, 4537, 4544, 4551, 4558, 4565
]


def main():
    parser = ArgumentParser(description=DESCRIPTION)
    parser.add_argument("hashquine",
                        help="a copy of Retroid's Zstandard hashquine")
    parser.add_argument(
        "tarfile", help="a Tar-based archive (tgz, tbz2... will work too)")
    args = parser.parse_args()

    fn = args.tarfile
    outname = os.path.basename(fn).split(".")[0] + ".tar.zst"

    # hashes separator:
    # " ", then:
    # - " ": text file
    # - "*": binary file

    # Can't we force everything to binary ?
    # textchars = bytearray({7, 8, 9, 10, 12, 13, 27}
    #                     | set(range(0x20, 0x100)) - {0x7f})
    # is_binary = lambda bytes: bool(bytes.translate(None, textchars))
    SEPARATOR = b" *"
    hashes = [SEPARATOR.join([b"0" * 32, outname.encode()])]
    bio = io.BytesIO()
    with tarfile.open(fn, 'r') as tfi:
        for member in tfi:
            f = tfi.extractfile(member.name)
            if f is not None:
                data = f.read()
                md5 = hashlib.md5(data).hexdigest().encode()
                hashes += [SEPARATOR.join([md5, member.name.encode("ascii")])]
        hashfile = b"\n".join(hashes)
        hashlength = len(hashfile)

        with tarfile.open(fileobj=bio, mode='w',
                          format=tarfile.GNU_FORMAT) as tfo:
            tinfo = tarfile.TarInfo(name='hash.md5')
            tinfo.mtime = 1680536736  # 14412572240 in octal
            tinfo.size = hashlength
            tinfo.uname = 'root'
            tinfo.gname = 'root'

            tfo.addfile(tinfo, io.BytesIO(hashfile))
            for member in tfi:
                member.frombuf(member.tobuf(format=tarfile.USTAR_FORMAT),
                               encoding='ascii',
                               errors='strict')
                member.uname = 'root'
                member.gname = 'root'
                if member.isdir():
                    tfo.addfile(member)
                else:
                    tfo.addfile(member, tfi.extractfile(member))
    tarcontents = bio.getvalue()
    hashleno = tarcontents[0x7C:0x87]

    header = b"".join([
        tarcontents[:0x100],
        b"\0ustar\x0000root",
        b"\0" * 0x1C,
        b"root",
        b"\0" * 0x1C,
        7 * b"0",
        b"\0",
        7 * b"0",
        0xA8 * b"\0",
    ])
    checksum = 256 + sum(struct.unpack_from("148B8x356B", header))
    checksum_s = bytes("%06o" % checksum, "ascii")

    # cut the suffix after the empty hash
    suffix = tarcontents[0x220:]
    zcomp = zstandard.ZstdCompressor()
    suffix = zcomp.compress(suffix)

    with open(args.hashquine, "rb") as f:
        data = bytearray(f.read())
    assert hashlib.md5(data[:HEADER_S]).hexdigest() == HEADER_MD5

    hex_value = hashlib.md5(data).hexdigest()

    # All the collisions don't display anything on side 0,
    # so they can be easily reset

    for index in block_indexes:
        data, _ = setUniColl(data, index, sideB=False)

    # Tar stuff:
    # 1. 1 Tar header start `hash.md5 [...] 0000644 0000000 0000000`
    data, _ = setUniColl(data, block_indexes[0], sideB=True)

    # 2. 8*11 hash.md5 file size
    for index, char in enumerate(hashleno):
        v = char - 0x30
        data, _ = setUniColl(data,
                             block_indexes[1 + 8 * index + v],
                             sideB=True)

    # 3. 1 Tar timestamp: ` 14412572240 `
    data, _ = setUniColl(data, block_indexes[89], sideB=True)

    # 4. 8*6 tar header checksum
    for index, char in enumerate(checksum_s):
        v = char - 0x30
        data, _ = setUniColl(data,
                             block_indexes[90 + 8 * index + v],
                             sideB=True)
    # 5. 1 Tar header end `  0 [...] ustar 00root [...] root [...] 0000000 0000000 [...] `
    data, _ = setUniColl(data, block_indexes[138], sideB=True)

    # `hash.md5` content start
    # 6. 1: "The MD5 of hashquine.tar.zst is"
    # 7. 1: "The MD5 of hashquine.zst is"

    # already reset and disabled

    data = data[:0x476c0] + suffix
    hex_value = hashlib.md5(data).hexdigest()

    # Hashquine part starts now, at the 141-th

    # 8. 32*16 MD5 hash (all nibble possibilities)
    # => 1+8*11+1+8*6+1+1+1+32*16=653

    for letter_index, letter in enumerate(hex_value):
        value = int(letter, HEX_BASE)
        block_index = 141 + letter_index * 16 + value
        data, _ = setUniColl(data, block_indexes[block_index], sideB=True)

    with open(outname, "wb") as f:
        f.write(data)
    print("Created file `%s`" % outname)


if __name__ == '__main__':
    main()
