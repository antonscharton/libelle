# libelle
multi class labeling tool


## Requirements

- pygame
- numpy
- tqdm


## Setup

1) specify paths in libelle.py  ("path_imagefolder", and optionally "path_prjfile")
2) run libelle.py


## Keymap

::                        '  [CTRL] + [S]                         save annotatin file to specified path',
::                        '  [LEFT ARROW], [RIGHT ARROW]          go one frame further / back',
                        '  [L]                                  add class before hovered class',
                        '  [L] + [CTRL] + [SHIFT] + [ALT]       delete hovered class',
                        '  [+]                                  zoom in',
                        '  [-]                                  zoom out',
                        '  [T]                                  text tool tips on / off',
                        ' ',
                        'play mode',
                        '  [SPACE]                              play / pause',
                        '  [BACKSPACE]                          go to frame 0',
                        '  [1] - [9]                            record on / off for class 1,2,...,9',
                        ' ',
                        'edit mode (when not playing)',
                        '  [LEFT MOUSE]                         paint label',
                        '  [LEFT MOUSE] + [LEFT CTRL]           erase label']
