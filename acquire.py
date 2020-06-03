import pygame
import os

path = os.path.dirname(__file__)

#configuration
config =\
{
 'width': 1280,
 'height': 720,
 'fps': 60
}

def center(background_size, object_size):
	return int((background_size-object_size)/2)

class Acquire(object):
	def __init__(self, **kwargs):
		# Change dictionary to object attributes
		self.__dict__.update(kwargs)

		pygame.init()
		pygame.display.set_caption("Acquire")
		flags = pygame.DOUBLEBUF
		self.window = pygame.display.set_mode((self.width, self.height), flags)
		self.background = pygame.Surface(self.window.get_size()).convert()
		self.board = Board(self.background)
		self.clock = pygame.time.Clock()
		self.playtime = 0.0
		self.font = pygame.font.SysFont('mono', 15)

	def paint(self):

		x = 1

	def run(self):
		"""The mainloop
		"""
		self.paint()
		running = True
		while running:
			for event in pygame.event.get():
				if event.type == pygame.QUIT:
					running = False
				elif event.type == pygame.KEYDOWN:
					if event.key == pygame.K_ESCAPE:
						running = False

			milliseconds = self.clock.tick(self.fps)
			self.playtime += milliseconds / 1000.0
			self.draw_text("FPS: {:6.3}{}PLAYTIME: {:6.3} SECONDS".format(
						   self.clock.get_fps(), " "*5, self.playtime))

			pygame.display.flip()
			self.window.blit(self.background, (0, 0))

		pygame.quit()


	def draw_text(self, text):
		"""Center text in window
		"""
		fw, fh = self.font.size(text)
		surface = self.font.render(text, True, (0, 255, 0))
		self.window.blit(surface, (10,10))


class Board(object):
	def __init__(self, background):
		self.rows, self.cols = (9, 12)
		rect = background.get_rect()
		self.x = 50
		self.y = 50
		self.width = int(self.cols * round((rect.width-self.x*2)/self.cols))
		self.height = int(self.rows * round((rect.height-self.y*2)/self.rows))

		self.tile_width = int(self.width/self.cols)
		self.tile_height = int(self.height/self.rows)
		if self.tile_height < self.tile_width:
			self.tile_width = self.tile_height
		else:
			self.tile_height = self.tile_width
		self.width = self.tile_width*self.cols
		self.height = self.tile_height*self.rows
		self.x = center(rect.width,self.width)
		self.y = center(rect.height,self.height)

		self.draw_tiles(background)
		border = 3
		pygame.draw.rect(background, (150,150,150),
						(self.x-border,self.y-border,
						self.width+border*2,self.height+border*2),border*2)

	def draw_tiles(self, background):
		font_file = os.path.join(path,
								"TarzanaNarrow_Bold.ttf")
		print(font_file)
		font = pygame.font.Font(font_file, 30)
		x = self.x
		y = self.y
		#tiles = [[0 for j in range(cols)] for i in range(rows)]
		#for tile in tiles:
		for i in range(self.rows):
			for j in range(self.cols):
				pygame.draw.rect(background, (0,0,125),
								(x,y,self.tile_width,self.tile_height), 1)
				text = f"{j+1}{chr(i+65)}"
				self.draw_label(font, text, background, x, y)
				x += self.tile_width
			x = self.x
			y += self.tile_height

	def draw_label(self, font, text, background, x, y):
		surface = font.render(text, True, (255, 255, 255))
		font_width, font_height = font.size(text)
		font_x = center(self.tile_width, font_width)
		font_y = center(self.tile_height, font_height)
		background.blit(surface, (x+font_x, y+font_y))


if __name__ == '__main__':
	Acquire(**config).run()
