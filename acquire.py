import pygame
import os
import math
import random

# file directory
path = os.path.dirname(__file__)

# set window position
#os.environ['SDL_VIDEO_WINDOW_POS'] = "%d,%d" % (50,50)
os.environ['SDL_VIDEO_CENTERED'] = '1'

#configuration
config =\
{
 'window_width': 1280,
 'window_height': 720,
 'fps': 60
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
		flags = pygame.DOUBLEBUF
		self.window = pygame.display.set_mode(
									(self.window_width, self.window_height), flags)
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

		self.board = Board(self.background)
		self.player = Player(self.max_player_tiles)
		self.pile_tiles, self.player_tiles = self.player.select_tiles(self.pile_tiles)
		self.player.draw_player_tiles(self.board, self.background)

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



			milliseconds = self.clock.tick(self.fps)
			self.playtime += milliseconds / 1000.0
			self.draw_text(f"FPS: {round(self.clock.get_fps())}")
			pygame.display.flip()

		pygame.quit()

	def choose_tile(self):
		t = 0

	def draw_text(self, text):
		text_box = self.font.render(text, True, (0, 255, 0))
		self.window.blit(text_box, (10,10))

	def on_mouse_down(self, mouse):
		print(mouse.pos, mouse.button)
		if mouse.button == 1:
			for tile in self.player_tiles:
				if tile.rect.collidepoint(pygame.mouse.get_pos()):
					print("collide")
					self.board.draw_board_tile(tile.label)
					new_tile = self.player.place_tile(tile, self.pile_tiles)
					print(f"{len(self.pile_tiles)} Tiles Remaining: ", self.pile_tiles)
					#print(new_tile.label, new_tile.rect)
					self.player.draw_player_tiles(self.board, self.background)
					break


class Board(object):
	board_margin = board_x = board_y = 20
	max_player_tiles = 6
	board_tiles = {}
	# board border
	border = 4

	def __init__(self, background):
		self.background_surface = background
		self.rows, self.cols = (9, 12)
		self.window_rect = background.get_rect()
		# set maximum board size
		self.board_width = self.window_rect.width - self.board_margin*2
		self.board_height = self.window_rect.height - self.board_margin*3
		print(self.board_height)
		# make all tiles the same size
		self.tile_width = int(self.board_width / self.cols)
		# divide by rows + 1 to leave room for the player tiles
		self.tile_height = int(self.board_height / (self.rows+1))
		if self.tile_height < self.tile_width:
			self.tile_width = self.tile_height
		else:
			self.tile_height = self.tile_width
		# scale up board by tile size
		self.board_width = self.tile_width * self.cols
		self.board_height = self.tile_height * self.rows
		print(self.board_height)
		self.board_x = center(self.window_rect.width, self.board_width)

		self.draw_board()


	def draw_board(self):
		#pygame.draw.rect(surface, (150,150,150),
		#				(self.board_x-border, self.board_y-border,
		#				self.board_width+border*2, self.board_height+border*2),
		#				border*2)
		self.board_surface = pygame.Surface((self.board_width+self.border*2,
											self.board_height+self.border*2))
		pygame.draw.rect(self.board_surface, (150,150,150),
						self.board_surface.get_rect(), self.border*2)
		# board spaces
		x = self.border
		y = self.border
		for i in range(self.rows):
			for j in range(self.cols):
				rect = pygame.draw.rect(self.board_surface, (0,0,125),
								(x,y,self.tile_width,self.tile_height), 1)
				text = f"{j+1}{chr(i+65)}"
				self.board_tiles[text] = rect
				self.draw_tile_text(text, self.board_surface, x, y, (255,255,255))
				x += self.tile_width
			x = self.border
			y += self.tile_height

		# blit board to surface
		self.board_surface.convert()
		self.background_surface.blit(self.board_surface,
									(self.board_x-self.border, self.board_y-self.border))
		# tile rack
		rack_width = (self.tile_width + self.board_margin) * self.max_player_tiles
		self.rack_x = center(self.window_rect.width, rack_width)
		self.rack_y = self.board_height + self.board_margin*2
		self.tile_rack_surface = pygame.Surface((rack_width, self.tile_height))
		#pygame.draw.rect(self.tile_rack_surface, (255,0,0),
		#				self.tile_rack_surface.get_rect(), 2)
		self.blit_tile_rack(self.background_surface)

	def blit_tile_rack(self, blit_surface):
		self.tile_rack_surface.convert()
		blit_surface.blit(self.tile_rack_surface, (self.rack_x,self.rack_y))

	def draw_tile_text(self, text, blit_surface, x, y, rgb):
		font_file = os.path.join(path, "TarzanaNarrow_Bold.ttf")
		#print(font_file)
		tile_font = pygame.font.Font(font_file, 30)
		text_box = tile_font.render(text, True, rgb)
		font_width, font_height = tile_font.size(text)
		font_x = center(self.tile_width, font_width)
		font_y = center(self.tile_height, font_height)
		text_box.convert()
		blit_surface.blit(text_box, (x+font_x, y+font_y))

	def draw_board_tile(self, tile_label):
		print(tile_label, self.board_tiles[tile_label])
		rect = self.board_tiles[tile_label]
		pygame.draw.rect(self.board_surface, (125,125,125), rect)
		text = f"{tile_label}"
		self.draw_tile_text(text, self.board_surface, rect.left, rect.top, (0,0,0))
		self.blit_board_tile(self.background_surface)

	def blit_board_tile(self, blit_surface):
		self.board_surface.convert()
		blit_surface.blit(self.board_surface,
							(self.board_x-self.border, self.board_y-self.border))

class Player(object):
	my_tiles = []
	tile_margin = 20
	def __init__(self, max_tiles):
		self.max_tiles = max_tiles

	def place_tile(self, placed_tile, new_tiles):
		print("Placed Tile: ",placed_tile.label)
		for i, tile in enumerate(self.my_tiles):
			if tile.label == placed_tile.label:
				if len(new_tiles) > 0:
					choice = random.choice(new_tiles)
					loc = new_tiles.index(choice)
					self.my_tiles[i] = Tile(new_tiles.pop(loc), tile.rect)
					return self.my_tiles[i]
				else:
					self.my_tiles.pop(i)
					return None


	def select_tiles(self, new_tiles):
		self.my_tiles = []
		while len(self.my_tiles) < self.max_tiles:
			if len(new_tiles) == 0:
				break
			choice = random.choice(new_tiles)
			loc = new_tiles.index(choice)
			self.my_tiles.append(Tile(new_tiles.pop(loc)))
		#print("Player Tiles:", self.my_tiles)
		return new_tiles, self.my_tiles

	def discard_tile(self, discarded_tile, new_tiles):
		print("Discarded Tile: ",discarded_tile.label)
		for i, tile in enumerate(self.my_tiles):
			if tile.label == discarded_tile.label:
				choice = random.choice(new_tiles)
				loc = new_tiles.index(choice)
				self.my_tiles[i] = Tile(new_tiles.pop(loc), tile.rect)
				return self.my_tiles[i]

	"""def draw_player_tile(self, tile, board, blit_surface):
		pygame.draw.rect(board.tile_rack_surface, (125,125,125),
						tile.rect)
		text = f"{tile.label}"
		board.draw_tile_text(text, board.tile_rack_surface,
							tile.rect.left, tile.rect.top, (0,0,0))
		board.blit_tile_rack(blit_surface)"""

	def draw_player_tiles(self, board, blit_surface):
		x = int(self.tile_margin/2)
		y = 0
		board.tile_rack_surface.fill((0,0,0))
		for tile in self.my_tiles:
			rect = pygame.draw.rect(board.tile_rack_surface, (125,125,125),
							(x, y, board.tile_width, board.tile_height))
			tile.rect = rect.move(board.rack_x, board.rack_y)
			text = f"{tile.label}"
			board.draw_tile_text(text, board.tile_rack_surface, x, y, (0,0,0))
			x += (board.tile_width + self.tile_margin)
		board.blit_tile_rack(blit_surface)

class Tile(object):
	def __init__(self, label, rect = (0, 0, 50, 50)):
		self.label = label
		self.rect = rect


if __name__ == '__main__':
	game = Acquire(**config)
	game.run()
