# libelle
multi class labeling tool


### Requirements

- pygame
- numpy
- tqdm


### Setup

1) specify paths in libelle.py  ("path_imagefolder", and optionally "path_prjfile")
2) run libelle.py


### Keymap
```
[CTRL] + [S]                         save annotation file to specified path
[LEFT ARROW]                         go one frame back
[RIGHT ARROW]                        go one frame forward
[L]                                  add class before hovered class
[L] + [CTRL] + [SHIFT] + [ALT]       delete hovered class
[+]                                  zoom in
[-]                                  zoom out
[T]                                  text tool tips on / off

play mode
[SPACE]                              play / pause
[BACKSPACE]                          go to frame 0
[1] - [9]                            record on / off for class 1,2,...,9

edit mode (when not playing)
[LEFT MOUSE]                         paint label
[LEFT MOUSE] + [LEFT CTRL]           erase label
[1]-[9] + [RETURN]                   paint label at current frame for class 1,2,...,9
[1]-[9] + [DEL]                      erase label at current frame for class 1,2,...,9
```

### Saving format
Annotations are saved to .txt files.
Each row correspondes to the annotation of one frame.
```
...
128357_4278566666.jpg 1 0 1
128359_4278633333.jpg 1 0 1
128360_4278666666.jpg 1 1 1
128362_4278733333.jpg 1 1 1
128364_4278800000.jpg 0 1 1
128365_4278833333.jpg 0 1 1
128367_4278899999.jpg 0 1 1
128368_4278933333.jpg 0 1 1
...
```
