import os
import random
import subprocess
import time
import urllib.parse
import uuid
from typing import Iterator, Optional, Union, Tuple

import chess
import chess.engine
import chess.svg
from PIL import Image, ImageDraw, ImageFont
from chess.engine import Score, Mate, Cp

INKSCAPE_PATH = "D:/Downloads/inkscape-0.92.4-x64/inkscape/inkscape.exe"
STOCKFISH_PATH = "D:/Downloads/stockfish-11-win/stockfish-11-win/Windows/stockfish_20011801_x64.exe"

engine = chess.engine.SimpleEngine.popen_uci(STOCKFISH_PATH)
engine.configure({"Threads": 7})
animation_styles = {}
run = f"r{int(time.time())}"


def get_empty_squares(board: chess.Board) -> Iterator[chess.Square]:
	return list(filter(lambda s: board.piece_at(s) is None, chess.SQUARES))


def get_random_empty_square(board: chess.Board) -> chess.Square:
	return random.choice(get_empty_squares(board))


def find_valid_square(board: chess.Board, piece: chess.Piece) -> Optional[chess.Square]:
	valid_squares = []
	for square in get_empty_squares(board):
		board_copy = board.copy()
		board_copy.set_piece_at(square, piece)
		if board_copy.is_valid():
			valid_squares.append(square)
	if valid_squares:
		return random.choice(valid_squares)
	else:
		return None


def add_kings(animate: bool = False, animation_name: str = None, in_board: chess.Board = None) -> chess.Board:
	board = in_board if in_board is not None else chess.Board(None)
	if animate:
		output_animation_frame(board, animation_name, 0)
	board.set_piece_at(get_random_empty_square(board), chess.Piece(chess.KING, True))
	if animate:
		output_animation_frame(board, animation_name, 1)
	black_king = chess.Piece(chess.KING, False)
	board.set_piece_at(find_valid_square(board, black_king), black_king)
	if animate:
		output_animation_frame(board, animation_name, 2)

	return board


def generate_board(animate: bool = True) -> Union[Tuple[chess.Board, str, int], chess.Board]:
	animation_name = str(uuid.uuid4())
	pieces = [chess.QUEEN] + [chess.BISHOP] * 2 + [chess.KNIGHT] * 2 + [chess.ROOK] * 2 + [chess.PAWN] * 8
	white_pieces = list(map(lambda p: chess.Piece(p, True), pieces))
	black_pieces = list(map(lambda p: chess.Piece(p, False), pieces))
	all_pieces = white_pieces + black_pieces
	random.shuffle(all_pieces)
	board = chess.Board(None)

	add_kings(animate, animation_name, board)

	frame = 3
	for i in range(len(all_pieces)):
		square = find_valid_square(board, all_pieces[i])
		if square:
			board.set_piece_at(square, all_pieces[i])

			if animate:
				output_animation_frame(board, animation_name, frame)

			frame += 1
		if i > 25 and random.random() < 0.1:
			break
	if animate:
		return board, animation_name, frame
	else:
		return board


def get_lichess_url(board: chess.Board):
	return f"https://lichess.org/editor/{urllib.parse.quote(board.fen())}"


def score_to_str(score: Score) -> str:
	cp = score.score()
	if cp is None:
		return str(score)
	else:
		p = cp / 100
		score_str = f"{p:.1f}" if abs(p) > 0.05 else f"{p:.2f}"
		return f"{'+' if p > 0 else ''}{score_str}"


def output_animation_frame(board: chess.Board,
                           animation: str = "",
                           frame: int = 0,
                           run_name: str = run,
                           score: Score = None,
                           base_path: str = None,
                           convert_to_png: bool = True):
	if animation in animation_styles:
		light_color, dark_color = animation_styles[animation]
	else:
		hue = random.randint(0, 360)
		saturation = random.randint(40, 90)
		dark_lightness = random.randint(20, 50)
		light_lightness = dark_lightness + (100 - dark_lightness) / 2
		light_color, dark_color = f"hsl({hue}, {saturation}%, {light_lightness}%)", f"hsl({hue}, {saturation}%, {dark_lightness}%)"
		animation_styles[animation] = light_color, dark_color

	base_path = f'animations/{run_name}/{animation}' if base_path is None else base_path
	svg_path = f'{base_path}/svg'
	png_path = f"{base_path}/{frame}.png"

	os.makedirs(svg_path, exist_ok=True)
	with open(f'{svg_path}/{frame}.svg', 'w') as f:
		svg = chess.svg.board(board,
		                      coordinates=False,
		                      style=f'''
	                      .dark {{
	                          fill: {dark_color};
	                      }}
	                      .light {{
	                          fill: {light_color};
	                      }}
	                      ''')
		f.write(svg)

	if convert_to_png:
		subprocess.call(f"{INKSCAPE_PATH} -z -f {svg_path}/{frame}.svg -w 600 -j -e {png_path}")
		if score is not None:
			score_text = score_to_str(score)
			text_color = "white" if score.score(mate_score=1000000) > 0 else "black"
			stroke_color = "black" if text_color == "white" else "white"
			img = Image.open(png_path)
			img = img.point(lambda p: p * 0.8)
			draw = ImageDraw.Draw(img)
			font = ImageFont.truetype("arialbd.ttf", 175)
			image_w, image_h = img.size
			text_w, text_h = draw.textsize(score_text, font=font)
			draw.text(((image_w - text_w) / 2, (image_h - text_h) / 2), score_text, fill=text_color, font=font,
			          stroke_width=5, stroke_fill=stroke_color)
			img.save(png_path)


def find_good_board(animate=False):
	lowest_score = 99999
	lowest_board = None
	animation_name, frame = "", 0

	for i in range(100):
		if animate:
			random_board, animation_name, frame = generate_board(animate=True)
		else:
			random_board = generate_board(animate=False)

		score = evaluate_board(random_board)

		print("score:", score, "board:", get_lichess_url(random_board))
		if animate:
			output_animation_frame(random_board, animation_name, frame=frame + 1, score=score)
		abs_score = abs(score.score(mate_score=100000))
		if abs_score < lowest_score and abs_score != 0:
			lowest_score = abs_score
			lowest_board = random_board
			print("new lowest!")
	engine.quit()
	print("lowest overall:", lowest_score)
	print(get_lichess_url(lowest_board))


def evaluate_board(random_board):
	analysis = engine.analyse(random_board, chess.engine.Limit(time=1))
	score = analysis['score'].white()
	return score


def random_animation():
	for j in range(10):
		for i in range(50):
			board = generate_board(animate=False)
			output_animation_frame(board, f"random_{j}", i, run_name=f"random_{run}")


def kings_animation():
	for i in range(20):
		board = add_kings()
		output_animation_frame(board, "kings", i, run_name=f"kings_{run}")


def chess960_animation():
	for i in range(25):
		board = chess.Board.from_chess960_pos(random.randint(0, 959))
		output_animation_frame(board, "chess960", i, run_name=f"chess960_{run}")


def output_board(position: str):
	board = chess.Board(position)
	output_animation_frame(board, "starting_board", 0, run_name=f"starting_board_{run}")


def generate_sample_boards():
	os.makedirs("./boards/images", exist_ok=True)
	f = open("./boards/readme.md", 'a')
	try:

		f.write(''' # Sample Boards

Each sample Good Chess board contains a link to Lichess's board editor so you can launch right into an online game against a friend or try your hand against Stockfish. Just click on "continue from here."

 ## Boards
 
''')
		while True:
			board = generate_board(animate=False)
			score = evaluate_board(board)
			abs_score = abs(score.score(mate_score=99999))
			print("Board:", abs_score)
			if 0 != abs_score < 30:
				board_id = str(uuid.uuid4())
				board_fen = board.fen()
				board_url = get_lichess_url(board)
				output_animation_frame(board,
				                       animation=board_id,
				                       base_path=f"./boards/images/{board_id}",
				                       convert_to_png=False)
				f.write(f''' ### Score: {score_to_str(score)}

[![{board_fen}](./images/{board_id}/svg/0.svg)]({board_url})
FEN: `{board_fen}`    
[Lichess board editor]({board_url})

''')
				f.flush()
	finally:
		f.close()


if __name__ == '__main__':
	find_good_board(animate=False)
	# generate_sample_boards()
	# find_good_board(animate=True)
	# random_animation()
	# kings_animation()
	# chess960_animation()
	# output_board("3RQ3/rN1BNPp1/p2pK3/2pp1P2/pP2q1r1/B1k1P3/4P2b/n1bn3q w - - 0 1")
