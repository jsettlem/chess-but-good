import os
import random

vips_path = "D:/Downloads/vips-dev-w64-all-8.9.1/vips-dev-8.9/bin"
os.environ['PATH'] = vips_path + ';' + os.environ['PATH']

from pyvips import Image

padding_size = 20
base_path = "./animations/r1586109741"
animation_path = "./animations/collage"


class Board:
	def __init__(self, name):
		self.name = name
		self.path = f"{base_path}/{name}"
		self.files = [name for name in os.listdir(self.path) if os.path.isfile(os.path.join(self.path, name))]
		self.files.sort(key=lambda f: int(f.split(".")[0]))
		self.images = [Image.new_from_file(f"{self.path}/{file}", access='sequential') for file in self.files]
		self.index = 0

	def get_current(self):
		return self.images[min(self.index, len(self.images) - 1)]

	def get_next(self):
		self.index += 1
		return self.get_current()

	def is_finished(self):
		return self.index >= len(self.images)


def combine():
	os.makedirs(animation_path, exist_ok=True)
	paths = [path for path in os.listdir(base_path)]
	frame = 0
	boards = [Board(path) for path in paths]
	while not all(board.is_finished() for board in boards):
		print("making frame", frame)
		images = [board.get_next() if random.random() < 0.1 else board.get_current() for board in boards]
		out = Image.arrayjoin(images, across=12, shim=padding_size)
		out.write_to_file(f"{animation_path}/{frame}.png")
		frame += 1


if __name__ == '__main__':
	combine()
