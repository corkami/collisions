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

To display the hex value of an MD5, 16 characters are required for 32 digits, so `480` (=`32*15`) collisions.

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

- a [PostScript](md5.ps) 'encoding' hashquine by *Gregor Kopf* - cf [Poc||GTFO 0x14:09](https://github.com/angea/pocorgtfo#0x14) ([article 9](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-09.pdf))

<img src=pics/postscript.png height=200></img>

- 2 PDF hashquines: one via [JPG](pocs/md5jpg.pdf), one via [text](pocs/md5text.pdf), by *Mako* - cf [Poc||GTFO 0x14:10](https://github.com/angea/pocorgtfo#0x14) ([article 10](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-10.pdf))

<img src=pics/jpgpdf.png height=100></img>

```
$ pdftotext -q md5text.pdf -
66DA5E07C0FD4C921679A65931FF8393

$ md5sum md5text.pdf
66da5e07c0fd4c921679a65931ff8393 *md5text.pdf
```

- 2 GIF hashquines by *spq* - cf [Poc||GTFO 0x14:11](https://github.com/angea/pocorgtfo#0x14) ([article 11](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-11.pdf))

<img src=pocs/md5.gif width=400></img>
<img src=pocs/md5_avp_loop.gif width=300></img>


- a NES 'encoding' hashquine, by Evan Sultanik and Evan Teran, in PoC||GTFO 0x14 (here as a [standalone file](pocs/hashquine.nes)) - cf [Poc||GTFO 0x14:12](https://github.com/angea/pocorgtfo#0x14) ([article 12](https://github.com/angea/pocorgtfo/blob/master/contents/articles/14-12.pdf))

<img src=pics/nes.png height=200></img>

- [Poc||GTFO 0x14](https://github.com/angea/pocorgtfo#0x14) is a polyglot file: simultaneously a JPG in PDF hashquine and a NES hashquine, with also a hidden cover while keeping the same MD5 - a classic collision, albeit the JPG picture has a lot of custom scans.

<img src=pics/pocorgtfo14.png height=400></img>


- a GIF hashquine by *Rogdham* - cf [blog post](https://www.rogdham.net/2017/03/12/gif-md5-hashquine.en)

<img src=pocs/rogdham_gif_md5_hashquine.gif height=150></img>


- a TIFF [hashquine (4 gb)](pocs/rogdham_tiff_md5_hashquine_4Go.zip) by *Rogdham*

Cf self-descriptive image (here as PNG):

<img src=pics/tiff_preview.png height=600></img>

- a PNG hashquine by *David 'Retr0id' Buchanan*

<img src=pocs/hashquine_by_retr0id.png height=600></img>


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
  - Knowing the offsets and the types of the collision just from one file, it's then possible to modify or reset the collisions and alter the display yourself of the files without changing their MD5 or recomputing any collision, whether it's an 'encoding' hashquine (ex: for [NES](scripts/nes.py)) or a 'format' hashquine (ex: [Jpg in PDF](scripts/jpgpdf.py)).

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

- Since correct values of Adler32 are required for Zlib chunks and CRC32 are required for PNG chunks, *Retr0id* had to forge these values while keeping the same MD5 hash: to do that, he added many fastcoll blocks and swapped them in a clever meet-in-a-middle attack to reach a suitable value - cf this [gitst](https://gist.github.com/DavidBuchanan314/a15e93eeaaad977a0fec3a6232c0b8ae).

The Fastcoll blocks to forge the CRCs are 'visible' at the bottom of the picture (here, with a revealing palette).

<img src=pics/retr0id_blue.png height=500></img>


<!-- pandoc -s -f gfm -t html README.md -o README.html -->
