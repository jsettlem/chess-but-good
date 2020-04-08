# Chess, but good

Confused? Watch [the video]() first.

Just want to play the game? Check out the [pre-generated boards](boards). They contain links to Lichess's board editor so you can launch right into a game online or against Stockfish. 

 ## Running the script  

`chessbutgood.py` contains everything you need to generate Good Chess boards, as well as most of the animations from the video. It's not set up as a proper Python project or anything so you'll have to figure out the dependencies on your own. You'll need a relatively new version of Python 3, [python-chess](https://python-chess.readthedocs.io/en/latest/), and Pillow. You'll also have to manually download Stockfish (or your UCI compatible chess engine of choice) and provide the path in `STOCKFISH_PATH`. If you want to output any images, you'll need Inkscape (specified in `INKSCAPE_PATH`) to convert from SVG to PNG (yeah, yeah, it's a heavy dependency, but SVGs are fickle). 

At the bottom of the file are various method calls used for generating boards and visuals. Comment and uncomment these lines to control their execution. 

`combiner.py` will combine a bunch of animations generated by `chessbutgood.py` into a giant collage animation like in the video. I don't anticipate anyone wanting to run this, but if you do, it requires pyvips which isn't very fun to install. 