import pygame
import os
import math
import random

# file directory
path = os.path.dirname(__file__)
font_file = os.path.join(path, "TarzanaNarrow_Bold.ttf")

# set window position
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
os.environ['SDL_VIDEO_CENTERED'] = '1'

#configuration
config =\
{
'window_width': 1280,
'window_height': 720,
'fps': 30
}

colors =\
{
'gry_tile': (125,125,125),
'blu_outline': (0,0,125),
'blk_background': (30,30,30)
}

def center(background_size, object_size):
	return int((background_size-object_size)/2)

class Acquire(object):

	rows, cols = (9, 12)
	pile_tiles = []
	max_player_tiles = 6

	def __init__(self, **kwargs):
		# Change dictionary to object attributes
		self.__dict__.update(kwargs)

		pygame.init()
		pygame.display.set_caption("Acquire")
		#flags = pygame.DOUBLEBUF
		self.window = pygame.display.set_mode(
									(self.window_width, self.window_height))
		self.background = pygame.Surface(self.window.get_size()).convert()
		self.clock = pygame.time.Clock()
		self.playtime = 0.0
		self.font = pygame.font.SysFont('mono', 15)

		self.num_tiles = self.rows*self.cols
		for i in range(self.num_tiles):
			letter = chr(i % self.rows + 65)
			num = math.ceil((i+1) / self.rows)
			self.pile_tiles.append(f"{num}{letter}")
		print(self.pile_tiles)

		self.board = Board((self.rows, self.cols), self.background)
		self.player = Player(self.max_player_tiles)
		self.player.starting_tiles(self.pile_tiles, self.board.rack_x,
								self.board.rack_y, self.board.tile_size)
		self.board.draw_player_tiles(self.player.my_tiles)

	def run(self):
		"""The mainloop"""
		running = True
		while running:
			self.window.blit(self.background, (0, 0))
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False
				elif event.type == pygame.MOUSEBUTTONDOWN:
					self.on_mouse_down(event)

			for label, tile in self.player.my_tiles.items():
				if tile.rect.collidepoint(pygame.mouse.get_pos()):
					if tile.hover == False:
						tile.hover = True
						self.board.highlight_tile(label)
				else:
					tile.hover = False
					self.board.unhighlight_tile(label)


			milliseconds = self.clock.tick(self.fps)
			self.playtime += milliseconds / 1000.0
			self.draw_text(f"FPS: {round(self.clock.get_fps())}")
			pygame.display.update()

		pygame.quit()

	def choose_tile(self):
		t = 0

	def draw_text(self, text):
		text_box = self.font.render(text, True, (0, 255, 0))
		self.window.blit(text_box, (10,10))

	def on_mouse_down(self, mouse):
		print(mouse.pos, mouse.button)
		if mouse.button == 1:
			for tile in self.player.my_tiles.values():
				if tile.rect.collidepoint(pygame.mouse.get_pos()):
					self.board.draw_board_tile(tile.label, colors['gry_tile'], (0,0,0))
					new_tile = self.player.place_tile(tile, self.pile_tiles)
					print(f"{len(self.pile_tiles)} Tiles Remaining: ", self.pile_tiles)
					#pygame.display.update(new_tile.rect)
					self.board.draw_player_tiles(self.player.my_tiles)
					break


class Board(object):
	max_player_tiles = 6
	board_tiles = {}
	board_y = margin = 20

	def __init__(self, dimensions, background):
		self.rows, self.cols = dimensions
		self.background_surface = background
		self.window_rect = background.get_rect()
		self.set_board_size()
		self.draw_board()

	def set_board_size(self):
		# set maximum board size
		max_height = self.window_rect.height - self.margin*3
		# divide by rows + 1 to leave room for the player tiles
		self.tile_size = int(max_height / (self.rows+1))
		# scale board by tile size
		self.board_width = self.tile_size * self.cols
		self.board_height = self.tile_size * self.rows
		self.board_x = center(self.window_rect.width, self.board_width)

	def draw_board(self):
		# board tiles
		x = self.board_x
		y = self.board_y
		ts = self.tile_size
		for i in range(self.rows):
			for j in range(self.cols):
				rect = pygame.Rect(x,y,ts,ts)
				text = f"{j+1}{chr(i+65)}"
				tile = Tile(text, rect, self.tile_size)
				self.board_tiles[text] = tile
				self.draw_board_tile(text, colors['blk_background'], (255,255,255))
				self.draw_board_tile(text, colors['blu_outline'], (255,255,255), 1)
				#tile.draw_tile(self.background_surface, (0,0,125), (255,255,255), 1)
				x += ts
			x = self.board_x
			y += ts
		# border
		border = 3
		pygame.draw.rect(self.background_surface, (150,150,150),
						(self.board_x-border, self.board_y-border,
						self.board_width+border*2, self.board_height+border*2),
						border)
		# tile rack
		self.rack_width = (ts + self.margin) * self.max_player_tiles
		self.rack_x = center(self.window_rect.width, self.rack_width)
		self.rack_y = self.board_height + self.margin*2

	def draw_board_tile(self, label, tile_color, text_color, width = 0):
		tile = self.board_tiles[label]
		tile.draw_tile(self.background_surface, tile_color, text_color, width)

	def draw_player_tiles(self, tiles):
		for tile in tiles.values():
			tile.draw_tile(self.background_surface, colors['gry_tile'], (0,0,0))

	def highlight_tile(self, label):
		tile = self.board_tiles[label]
		tile.draw_tile(self.background_surface, (255, 255, 200), (0,0,0), 0, 200)

	def unhighlight_tile(self, label):
		tile = self.board_tiles[label]
		tile.surface.fill(colors['blk_background'])
		self.draw_board_tile(label, colors['blu_outline'], (255,255,255), 1)

class Player(object):
	my_tiles = {}
	margin = 20
	def __init__(self, max_tiles):
		self.max_tiles = max_tiles

	def place_tile(self, placed_tile, new_tiles):
		# new_tiles is a list
		print("Placed Tile: ",placed_tile.label)
		for label,tile in self.my_tiles.items():
			if label == placed_tile.label:
				self.my_tiles.pop(label)
				if len(new_tiles) > 0:
					choice = random.choice(new_tiles)
					loc = new_tiles.index(choice)
					self.my_tiles[choice] = Tile(new_tiles.pop(loc),
												tile.rect, tile.size)
					return self.my_tiles[choice]
				else:
					return None

	def starting_tiles(self, new_tiles, rack_x, rack_y, tile_size):
		# new_tiles is a list
		x = rack_x + int(self.margin/2)
		while len(self.my_tiles) < self.max_tiles:
			choice = random.choice(new_tiles)
			loc = new_tiles.index(choice)
			rect = pygame.Rect(x, rack_y, tile_size, tile_size)
			self.my_tiles[choice] = Tile(new_tiles.pop(loc), rect, tile_size)
			x += (tile_size + self.margin)

	def discard_tile(self, discarded_tile, new_tiles):
		# new_tiles is a list
		print("Discarded Tile: ",discarded_tile.label)
		for i, tile in enumerate(self.my_tiles):
			if tile.label == discarded_tile.label:
				choice = random.choice(new_tiles)
				loc = new_tiles.index(choice)
				self.my_tiles[i] = Tile(new_tiles.pop(loc), tile.rect, tile.size)
				return self.my_tiles[i]

class Tile(object):
	hover = False
	def __init__(self, label, rect, size):
		self.label = label
		self.rect = rect
		self.size = size
		self.surface = pygame.Surface((size,size))

	def draw_tile(self, blit_surface, tile_color, text_color, width = 0, alpha = None):
		pygame.draw.rect(self.surface, tile_color, (0,0,self.size,self.size), width)
		self.surface.set_alpha(alpha)
		self.draw_text(text_color)
		#self.surface = pygame.Surface.convert_alpha(self.surface)
		blit_surface.blit(self.surface, self.rect)

	def draw_text(self, rgb):
		tile_font = pygame.font.Font(font_file, 30)
		text_box = tile_font.render(self.label, True, rgb)
		font_width, font_height = tile_font.size(self.label)
		font_x = center(self.size, font_width)
		font_y = center(self.size, font_height)
		text_box.convert()
		self.surface.blit(text_box, (font_x, font_y))


if __name__ == '__main__':
	game = Acquire(**config)
	game.run()
