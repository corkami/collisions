By Marc Stevens

# MD5 collisions

Since a team of researchers led by Xiaoyun Wang disclosed collisions for MD5 in 2004, it has been clear that MD5 is broken.
Nevertheless it turned out hard to convince people to stop using MD5. 
This led to new research in making the MD5 attacks faster and stronger as well as constructing meaningful collisions with realistic attack scenarios, notable highlights are:
* 2004: First (identical-prefix) collision by Wang et al.: pseudo-random 128-byte collisions. [WY05]
* 2004-2006: Various meaningful collision examples: X.509 certificates (Lenstra, de Weger, Wang [LdWW05]), postscript documents (Daum, Lucks) [DL06], software (Kaminsky [K04]/ Mikle [M04] / Selinger [Sel06]) 
* 2006: First chosen-prefix collison: colliding X.509 certificates with distinct names [SLdW07]
* 2009: Short chosen-prefix collision: rogue intermediary Certification Authority certificate [SSALMOdW09]
* 2012: FLAME malware exploits unknown chosen-prefix collision attack to obtain code signing certificate for Windows Update [S13][FS15]
* 2017: toy MD5 hashquines: creating documents that show their own MD5 hash: GIF, PDF, PostScript [twitter]

# on Unicoll

The chosen-prefix collision attack is the most powerful collision attack because it allows two distinct arbitrarily chosen prefixes, so one typically only needs to 'hide' the attack generated collision bitstrings in the document. Another benefit is that each colliding document only contains 1 prefix. With available MD5 cryptanalysis tools ([HashClash][hashclash] script `scripts/cpc.sh`, or [precompiled GUI with CUDA support][hashclashbin]) one can create such chosen-prefix collisions in one day. 
Convenient for 2 colliding files, but not fast enough for tricks such as MD5 hashquines that require at least 128 collision attacks generating 2^128 possible files all with the same hash.

Identical-prefix collisions can be created much faster within a few seconds (using e.g. [fastcoll][fastcoll], [S06]), but these generate pseudo-random looking 128-byte byte strings. The only difference occurs in these collision byte strings which makes it a bit more tricky to exploit these meaningfully in file formats.

To facilitate file format exploits with identical-prefix collisions together with Ange Albertini I've modified [hashclash][hashclash] and created a script `scripts/poc_no.sh` for a special type of a fast identical-prefix collision attack that we've dubbed UniColl.
It's special in that it uses a message block difference of just a single bit which is located early in the 10th-byte and actually in its least-significant bit.
This is rather unique because all fast collision attack message block differences seem to require at least 3 bit differences, at least one of which on the most-significant bit of a certain byte. Moreover, with UniColl one can completely choose the content of the first 12 bytes which makes it very flexible for a number of file formats, including text-based formats.
There are other single-bit collision attacks including some on lower bits of bytes, namely those used for the chosen-prefix collision attack, but these attacks are quite a bit slower.

The script is not perfect and sometimes fails (I will try to make it smarter), in which case I suggest to just retry with a slightly modified prefix (another fix is to set `data=200000` in the script to a higher value, say `data=1000000`).
* Clone hashclash repo
* Follow instructions to build hashclash
* Run `[hashclashdir]/scripts/poc_no.sh <prefixfile>` with a prefixfile of length N x 64 + K x 4 bytes where K<=3.

[WY05]: https://link.springer.com/chapter/10.1007/11426639_2 
[M04]: https://eprint.iacr.org/2004/356.pdf
[K04]: https://eprint.iacr.org/2004/357.pdf
[LdWW05]: https://eprint.iacr.org/2005/067.pdf
[DL06]: http://web.archive.org/web/20071226014140/http://www.cits.rub.de/MD5Collisions/
[Sel06]: https://www.mscs.dal.ca/~selinger/md5collision/
[S06]: https://marc-stevens.nl/research/papers/eprint-2006-104-S.pdf
[SLdW07]: https://marc-stevens.nl/research/papers/EC07-SLdW.pdf
[SSALMOdW09]: https://marc-stevens.nl/research/papers/CR09-SSALMOdW.pdf
[S12]: https://marc-stevens.nl/research/md5-1block-collision
[S13]: https://marc-stevens.nl/research/papers/C13-S.pdf
[FS15]: https://marc-stevens.nl/research/papers/AC15-FS.pdf
[hashclash]: https://github.com/cr-marcstevens/hashclash
[hashclashbin]: https://github.com/cr-marcstevens/hashclash-old-svn-repo/tree/master/downloads
[fastcoll]: https://marc-stevens.nl/research/software/download.php?file=fastcoll_v1.0.0.5-1_source.zip
[thesis]: https://marc-stevens.nl/research/papers/PhD%20Thesis%20Marc%20Stevens%20-%20Attacks%20on%20Hash%20Functions%20and%20Applications.pdf
