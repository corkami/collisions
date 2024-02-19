Detectcoll (unsafe) outputs.

# MD5
- FastColl: `dm4=80000000 dm11=00008000 dm14=80000000` / `dm4=80000000 dm11=ffff8000 dm14=80000000` (Wang, Flame(!) too)

- Unicoll1: `dm2=00000100` / `dm2=ffffff00`
- Unicoll2: no detection
- Unicoll3: `dm6=00000100 dm9=80000000 dm15=80000000`/ `dm6=ffffff00 dm9=80000000 dm15=80000000`

- Apop: no dm, but ihv, ihv: 7,7,7,7

- Single block IPC: `dm8=02000000 dm13=80000000` / `dm8=fe000000 dm13=80000000`

Hashclash CPC:
- pe: `dm11=00000004` / `dm11=fffffffc`
- jpg/pe: `dm11=00000008` / `dm11=fffffff8`
- pdf/pe: `dm11=40000000` / `dm11=c0000000`
- ca.der: `dm11=fffffe00` / `dm11=00000200`
- Zinsider:
  - 3mf: `dm11=ffe00000` / `dm11=00200000`
  - docx: `dm11=ffe00000` / `dm11=00200000`
  - epub: `dm11=ffe00000` / `dm11=00200000`
  - xps: `dm11=fffc0000` / `dm11=00040000`
  - xlsx: `dm11=00080000` / `dm11=fff80000`
  - pptx: `dm11=10000000` / `dm11=f0000000`
  - oxps: `dm11=fe000000` / `dm11=02000000`
- pileup
  - pdf: block10: `dm11=00200000` / block20: `dm11=20000000`
  - mp4: block10: `dm11=ffe00000` / block20: `dm11=20000000`
  - pe: block10: `dm11=ffff0000` / block20: `dm11=e0000000`
  - png: block10: `dm11=00010000` / block20: `dm11=e0000000`

- single block CPC: `dm2=00000100 dm4=80000000 dm11=00008000 dm14=80000000` / `dm2=ffffff00 dm4=80000000 dm11=ffff8000 dm14=80000000`

# SHA1
Shattered (IPC):
- `dm0=0c000002 dm1=3ffffff0 dm2=abfffff4 dm3=fbfffffc dm4=4c00000a dm5=dffffff0 dm6=e400001c dm7=d4000014 dm8=fbfffffe dm9=bffffff0 dm10=8c000004 dm11=e4000004 dm12=84000008 dm13=affffff0 dm14=00000004 dm15=47fffff0` side A, block +0
- `dm0=f3fffffe dm1=bffffff0 dm2=8c00001c dm3=ec000004 dm4=43fffff6 dm5=dffffff0 dm6=1bffffe4 dm7=ec000014 dm8=fc000002 dm9=40000010 dm10=54000004 dm11=e4000004 dm12=83fffff8 dm13=90000010 dm14=00000004 dm15=47fffff0` side A, block +1
- `dm0=f3fffffe dm1=c0000010 dm2=5400000c dm3=04000004 dm4=b3fffff6 dm5=20000010 dm6=1bffffe4 dm7=2bffffec dm8=04000002 dm9=40000010 dm10=73fffffc dm11=1bfffffc dm12=7bfffff8 dm13=50000010 dm14=fffffffc dm15=b8000010` side B, block +0
- `dm0=0c000002 dm1=40000010 dm2=73ffffe4 dm3=13fffffc dm4=bc00000a dm5=20000010 dm6=e400001c dm7=13ffffec dm8=03fffffe dm9=bffffff0 dm10=abfffffc dm11=1bfffffc dm12=7c000008 dm13=6ffffff0 dm14=fffffffc dm15=b8000010` side B, block +1


Shambles (CPC):
- `dm0=f4000002 dm1=3ffffff0 dm2=6c00001c dm3=e4000004 dm4=5bfffffa dm5=1ffffff0 dm6=24000014 dm7=abffffec dm8=f4000002 dm9=c0000010 dm10=93ffffe4 dm11=1bfffffc dm12=43fffff8 dm13=4ffffff0 dm14=fffffffc dm15=a8000010`
- `dm0=0bfffffe dm1=c0000010 dm2=93ffffe4 dm3=1bfffffc dm4=a4000006 dm5=e0000010 dm6=dbffffec dm7=54000014 dm8=0bfffffe dm9=3ffffff0 dm10=6c00001c dm11=e4000004 dm12=bc000008 dm13=b0000010 dm14=00000004 dm15=57fffff0`
