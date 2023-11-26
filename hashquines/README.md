# Hashquines

Hashquines are files showing their own MD5.

It seems like an impossible magic trick because modifying the file's contents changes the hash, therefore the hash can't be known in advance.
So it's the opposite strategy: make it possible to display *any* value, included the value of the actual hash of the file, without changing the overall hash of the file.

While the security risk they represent is debatable, they certainly show that MD5 is now just a fun toy.
 

# Strategies


## Self-check

'Cheating' by just computing the hash value and displaying it. They don't rely on hash collisions.

In Python:
```python
import hashlib
import sys
print(hashlib.md5(open(sys.argv[0],"rb").read()).hexdigest())
```

In Batch:
```batch
md5sum %0
```


## Read an encoded value

Chain enough fast collisions to be able to encode a hash value without modifying the final hash value, then some code is *executed* to check and display that value.

Some fixed offsets of FastColl collision blocks will be xored with `0x80`, so that bit can be checked reliably - in this case, one collision equals 1 bit of information.

An MD5 is 128 bits, so 128 Fastcoll blocks are needed.


## Abuse format parsing

Abuse the format structure to make the parser display a digit or another while keeping the same hash value, repeat for each digit and for every value to be displayed (`32*16=512`).

Like colliding 2 images or documents, but instead colliding the contents of many different elements at various positions, to display the right value of the actual hash file without changing the overall file hash.


Depending on the format, a possible way is to use a collision as a switch to enable one character or another. In this case, `N` chained collisions display `N+1` different objects in the same position.

To display the hex value of an MD5, 16 characters are required for 32 digits, so `480` (=`32*15`) collisions if there's the ability to select between different characters.

If it's only possible to turn on/off decoded sequences, then `512` (=`32*16`) collisions are needed.

A way to reduce this amount of collision is to display the characters via 7-segments display, in which case each segments needs to be toggled on or off (like bits).
So in this case, `224` (`=32*7`) collisions are required.

```
 -
| |
 -
| |
 -
```


# Examples

- a [PostScript](md5.ps) 'encoding' hashquine by *Gregor Kopf* - cf [Poc||GTFO 0x14:09](https://github.com/angea/pocorgtfo#0x14) ([article 9](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-09.pdf)) ([script](scripts/ps.py))

<img src=pics/postscript.png height=200></img>

- 2 PDF hashquines: one via [JPG](pocs/md5jpg.pdf), one via [text](pocs/md5text.pdf), by *Mako* - cf [Poc||GTFO 0x14:10](https://github.com/angea/pocorgtfo#0x14) ([article 10](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-10.pdf)) (scripts: [jpg](scripts/pdf_jpg.py), [txt](scripts/pdf_txt.py))

<img src=pics/jpgpdf.png height=100></img>

```
$ pdftotext -q md5text.pdf -
66DA5E07C0FD4C921679A65931FF8393

$ md5sum md5text.pdf
66da5e07c0fd4c921679a65931ff8393 *md5text.pdf
```

- 2 GIF hashquines by *spq* - cf [Poc||GTFO 0x14:11](https://github.com/angea/pocorgtfo#0x14) ([article 11](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-11.pdf)) (scripts: [segments](scripts/gif_seg.py), [avp](scripts/gif_avp.py))

<img src=pocs/md5.gif width=400></img>
<img src=pocs/md5_avp_loop.gif width=300></img>


- a NES 'encoding' hashquine, by Evan Sultanik and Evan Teran, in PoC||GTFO 0x14 (here as a [standalone file](pocs/hashquine.nes)) - cf [Poc||GTFO 0x14:12](https://github.com/angea/pocorgtfo#0x14) ([article 12](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-12.pdf)) ([script](scripts/nes.py))

<img src=pics/nes.png height=200></img>

- [Poc||GTFO 0x14](https://github.com/angea/pocorgtfo#0x14) is a polyglot file: simultaneously a JPG in PDF hashquine and a NES hashquine, with also a hidden cover while keeping the same MD5 - a classic collision, albeit the JPG picture has a lot of custom scans. ([script](scripts/pocorgtfo14.py))

<img src=pics/pocorgtfo14.png height=400></img>


- a GIF hashquine by *Rogdham* - cf [blog post](https://www.rogdham.net/2017/03/12/gif-md5-hashquine.en) ([script](scripts/gif_rog.py))

<img src=pocs/rogdham_gif_md5_hashquine.gif height=150></img>


- a TIFF [hashquine (4 gb)](pocs/rogdham_tiff_md5_hashquine_4Go.zip) by *Rogdham*

Cf self-descriptive image (here as PNG):

<img src=pics/tiff_preview.png height=600></img>

- a PNG hashquine by *David 'Retr0id' Buchanan*

<img src=pocs/hashquine_by_retr0id.png height=600></img>


## Archive hashquines

Decompressing these archives gives the hash of the whole archive.

- a [GZIP hashquine](pocs/hashquine.gz) by *Ange Albertini* ([script](scripts/gzip.py))

```
$ md5sum hashquine.gz
ad5de2581f4bd8f35051b789df379d36 *hashquine.gz

$ gzip -dck hashquine.gz
ad5de2581f4bd8f35051b789df379d36 is the hash of this archive.

This is a Gzip partial hashquine, made of many Gzip members chained together.
It's using 192 Unicoll MD5 collisions to display optionally each of the
16 hexadecimal characters '0123456789abcdef' 12 times (in that order).
This is not enough to display any MD5 digest (32 nibbles),
so an extra small member with bruteforced contents was appended to give the file
an MD5 that can be displayed with this limited input.

Thanks to Marc Stevens for creating Unicoll.
Thanks to David Buchanan for the constructive discussions.

Ange Albertini 2023
```

- an [LZ4 hashquine](pocs/hashquine.lz4) by *Ange Albertini*, with 160 collisions.  ([script](scripts/lz4.py))

```
$ md5sum hashquine.lz4
1690738ac079d914645ade5693ab019b *hashquine.lz4
$ lz4 -c hashquine.lz4
1690738ac079d914645ade5693ab019b
```

### Retroid's Zstandard file

A clever Zstandard hashquine++ by *David 'Retr0id' Buchanan*.  (scripts: [zst](scripts/zst.py), [tar.zst](scripts/tar_zst.py))

As a pure [ZStandard](pocs/hashquine.zst) file:

```
$ md5sum hashquine.zst
720ca7f6842f1a608fcb924f5811ebb9 *hashquine.zst

$ zstd -cd hashquine.zst
The MD5 of hashquine.zst is:
720ca7f6842f1a608fcb924f5811ebb9
```

As a [Zstandard(tar)](pocs/hashquine.tar.zst) file:

```
$ md5sum hashquine.tar.zst
703911cf9e409965cebd05392acc1503 *hashquine.tar.zst

$ tar -Oxf hashquine.tar.zst hash.md5
The MD5 of hashquine.tar.zst is:
703911cf9e409965cebd05392acc1503
```

As a self-checked 'auto-manifest' [Tar.zst](pocs/self.tar.zst) (this is generic: make [your own](scripts/tar_zst.py) from any given Tar!):

```
$ md5sum self.tar.zst
f068d54fabb12dbb1b359745a80d78fc *self.tar.zst
```

```
$ tar -xvf self.tar.zst
x hash.md5
x hello.txt
```

```
$ cat hash.md5
f068d54fabb12dbb1b359745a80d78fc *self.tar.zst
ed076287532e86365e841e92bfc50d8c *hello.txt
```

```
$ md5sum -c hash.md5
self.tar.zst: OK
hello.txt: OK
```

All these files are Zstandard-streams via the same prefix with 653 collisions (!):

1. Tar Header (entirely optional and generic for `hash.md5` contents):
   1. `1` for the Tar header start `hash.md5 [...] 0000644 0000000 0000000` (constant)
   2. `8*11` for the `hash.md5` file size, in octal.
   3. `1` for a Tar timestamp: ` 14412572240 ` (constant)
   4. `8*6` tar header checksum, in octal
   5. `1` for the rest of the Tar header `  0 [...] ustar 00root [...] root [...] 0000000 0000000 [...] ` (constant)

2. File contents:

  Optional text prefixes:
 
   6. `1` for the prefix "The MD5 of hashquine.tar.zst is" (constant)
   7. `1` for the prefix "The MD5 of hashquine.zst is" (constant)

  Hashquine:

   8. `32*16` MD5 hash (all nibble possibilities)

So this file archive prefix can be set to be decompressed as a tar archive or not, as the tar header is entirely optional, and the tar header checksum can be adjusted. Since all the collisions make each compressed frame optional, they can be set to decompress as a 292kB [empty Zstandard archive](pocs/empty.zst):

```
$ zstd -d empty.zst
empty.zst           : 0 bytes
```

# Notes


## Custom FastColl

For these hashquines, new forms of hash collisions were introduced by *Mako*:

- Rather than relying on UniColl, FastColl was modified to force the creation of a JPEG comment `FF FE` right before the collision difference. Also useable for standard JPEG [collisions](../examples/free).

- Similarly, in the PDF hashquine with text, 32b of the FastColl are forced to be ` Do(...)` which is a valid PDF operator. It's very nice to have such a short text operator that can be abused in the middle of a collision block!


## Hiding collision blocks

As usual, hiding collision blocks can be tricky. Here are some introduced techniques.

- *Mako* abused PDF name conventions, forcing the start of the collision block to define a PDF name - the last character before the collision block is a `/`, defining a PDF name. The name has to be reused later in the file.

For example, the first collision block defines the atrocious but working name `/öÃÝüúá.3A¢å¦e»ñæÀ¿Wæ‚b—»ò´óûàÊÄÃ’\q±*,ÆýH™æSùÞsp`.

- *Retr0id* put the collision blocks in plain sight: a custom palette is used to hide all colors but 0, and collision blocks containing null values are rejected.

Here's the a crop of the picture around the `8` digit with a more revealing palette (black and red color unmodified).

<img src=pics/8blue.png height=100></img>

These are unicoll blocks to turn on/off the red pixels (color `0` or `1`)


## Misc

- [`detectcoll`](https://github.com/corkami/collisions#detection) in *unsafe mode* can enumerate all Fastcoll and Unicoll occurences are present in the file - cf [logs](logs/).
  - Knowing the offsets and the types of the collision just from one file, it's then possible to modify or reset the collisions and alter the display yourself of the files without changing their MD5 or recomputing any collision, whether it's an encoding-based, format-based or archive hashquine.

- Since Unicoll only changes one byte, Retr0id's PNG font is made of one pixel per line:

<img src=pics/8.png height=100></img>

```
  *
     *
*
       *
*
       *
  *
     *
*
       *
*
       *
  *
     *
```

- Since correct values of Adler32 are required for Zlib chunks and CRC32 are required for PNG chunks, *Retr0id* had to forge these values while keeping the same MD5 hash: to do that, he added many fastcoll blocks and swapped them in a clever meet-in-a-middle attack to reach a suitable value - cf this [gist](https://gist.github.com/DavidBuchanan314/a15e93eeaaad977a0fec3a6232c0b8ae).

The Fastcoll blocks to forge the CRCs are 'visible' at the bottom of the picture (here, with a revealing palette).

<img src=pics/retr0id_blue.png height=500></img>


- If the whole file has to be parsed, and each hex character can be switched on/off,
 an MD5 might be displayable by less characters than the whole range of 16 characters: in practice, `192` (=`12*16`) collisions are enough to display a bruteforced MD5 after roughly a few 1000s tries.

  For example, `ad5de2581f4bd8f35051b789df379d36` is a bruteforced MD5 made of 12 groups of hex characters in increasing order:

  `ad`, `5de`, `258`, `1f`, `4bd`, `8f`, `35`, `05`, `1b`, `789df`, `379d`, `36`.

  It's possible with even fewer collisions (for example with only 10 characters sets), but it requires more luck:

  `169`, `07`, `38ac`, `079d`, `9`, `146`, `45ade`, `569`, `3ab`, `019b` fits in 10 groups.


# More than hash values

Many collisions can be used to encode or display a hash value, but they can be used to encode anything else, even bigger.

*Retr0id* [combined](https://github.com/DavidBuchanan314/monomorph) parallelized Fastcoll with a linux 4kb shellcode loader, generating a hashquine (benign), a rickroll (fun) or a meterpreter (evil) or anything you want with the same final hash.

```
$ python3 monomorph.py bin/monomorph.linux.x86-64.benign benign
[...]
$ python3 monomorph.py bin/monomorph.linux.x86-64.benign hashquine sample_payloads/bin/hashquine.bin
[...]
$ benign
$ hashquine
My MD5 is: 3cebbe60d91ce760409bbe513593e401
$ md5sum benign hashquine
3cebbe60d91ce760409bbe513593e401  benign
3cebbe60d91ce760409bbe513593e401  hashquine
```

<!-- pandoc -s -f gfm -t html README.md -o README.html -->
