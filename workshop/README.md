<!-- pandoc -s -f gfm -t html README.md -o README.html -->

[<img width=350 src=../preview.png />](../preview.png)

# Workshop materials

[Slides](https://speakerdeck.com/ange/colltris) (SpeakerDeck)

[<img width=350 src=../pics/CollTris.png />](https://speakerdeck.com/ange/colltris)

[Video](https://www.youtube.com/watch?v=BcwrMnGVyBI) (Youtube)

[<img width=350 src=../pics/recording.jpg />](https://www.youtube.com/watch?v=BcwrMnGVyBI)


## Start files

- precomputed [prefixes](prefixes/README.md)
- PNG pictures: <img width=20 src=yes.png /> [yes.png](yes.png) / <img width=20 src=no.png /> [no.png](no.png)
- GIF animation: <img width=20 src=yesno.gif />[yesno.gif](yesno.gif)


## References

- simple PNG chunk reader/writer: [minipng.py](minipng.py)
  - resulting 'merged' image: <img width=20 src=final.png />[final.png](final.png)
- simplified Kaitai grammar for abusive PNG files (starting with a dummy chunk): [png_simple.ksy](png_simple.ksy)

- tiny PNG colliding files: <img width=40 src=tiny1.png /> Ken Silverman' [most interesting](http://web.archive.org/web/20070905115613/http://www.jonof.id.au/forum/index.php?topic=934.15#msg5809) / <img width=40 src=tiny2.png /> 3x1 R,G,B => [tiny1.png](tiny1.png) / [tiny2.png](tiny2.png)

## Captures

- collisions: [FastColl](../examples/fastcoll.svg) / [UniColl](../examples/unicoll.svg) / [HashClashCPC (log)](../examples/cpc.html)

- precomputed collisions: [generic PNG](../examples/pngGen.svg) / [specific header PNG](../examples/pngSpec.svg)

- collisions: [GIF w/ FastColl](../examples/gifFastColl.svg) / [PNG w/ UniColl](../examples/pngUniColl.svg)


## External links

- [Kaitai IDE](http://ide.kaitai.io)
- [HashClash](https://github.com/cr-marcstevens/hashclash)
