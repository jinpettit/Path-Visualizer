import heapq
import pygame
import pygame_gui
from queue import PriorityQueue
from collections import deque
import constants
WINDOW_WIDTH = constants.WINDOW_WIDTH
WINDOW_HEIGHT = constants.WINDOW_HEIGHT

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165 ,0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
DARK_GREY = (33, 40, 45)

class Spot:
	def __init__(self, row, col, width, total_rows):
		self.row = row
		self.col = col
		self.x = row * width
		self.y = col * width
		self.color = WHITE
		self.neighbors = []
		self.width = width
		self.total_rows = total_rows

	def __repr__(self):
			return str(self.row) + "," + str(self.col) + ",,,"

	def get_pos(self):
		return self.row, self.col

	def is_closed(self):
		return self.color == RED

	def is_open(self):
		return self.color == GREEN

	def is_barrier(self):
		return self.color == BLACK

	def is_start(self):
		return self.color == ORANGE

	def is_end(self):
		return self.color == TURQUOISE

	def reset(self):
		self.color = WHITE

	def make_start(self):
		self.color = ORANGE

	def make_closed(self):
		self.color = RED

	def make_open(self):
		self.color = GREEN

	def make_barrier(self):
		self.color = BLACK

	def make_end(self):
		self.color = TURQUOISE

	def make_path(self):
		self.color = PURPLE

	def draw(self, win):
		pygame.draw.rect(win, self.color, (self.x, self.y, self.width, self.width))

	def update_neighbors(self, grid):
		self.neighbors = []
		if self.row > 0 and not grid[self.row - 1][self.col].is_barrier(): # UP
			self.neighbors.append(grid[self.row - 1][self.col])

		if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier(): # RIGHT
			self.neighbors.append(grid[self.row][self.col + 1])

		if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier(): # DOWN
			self.neighbors.append(grid[self.row + 1][self.col])

		if self.col > 0 and not grid[self.row][self.col - 1].is_barrier(): # LEFT
			self.neighbors.append(grid[self.row][self.col - 1])

	def __lt__(self, other):
		return False


def h(p1, p2):
	x1, y1 = p1
	x2, y2 = p2
	return abs(x1 - x2) + abs(y1 - y2)


def reconstruct_path(came_from, current, draw):
	while current in came_from:
		current = came_from[current]
		current.make_path()
		draw()


def algorithm(draw, grid, start, end):
	count = 0
	open_set = PriorityQueue()
	open_set.put((0, count, start))
	came_from = {}
	g_score = {spot: float("inf") for row in grid for spot in row}
	g_score[start] = 0
	f_score = {spot: float("inf") for row in grid for spot in row}
	f_score[start] = h(start.get_pos(), end.get_pos())

	open_set_hash = {start}

	while not open_set.empty():
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				pygame.quit()

		current = open_set.get()[2]
		open_set_hash.remove(current)

		if current == end:
			reconstruct_path(came_from, end, draw)
			end.make_end()
			return True

		for neighbor in current.neighbors:
			temp_g_score = g_score[current] + 1

			if temp_g_score < g_score[neighbor]:
				came_from[neighbor] = current
				g_score[neighbor] = temp_g_score
				f_score[neighbor] = temp_g_score + h(neighbor.get_pos(), end.get_pos())
				if neighbor not in open_set_hash:
					count += 1
					open_set.put((f_score[neighbor], count, neighbor))
					open_set_hash.add(neighbor)
					neighbor.make_open()

		draw()

		if current != start:
			current.make_closed()

	return False


def draw_path(came_from, draw):
	while came_from:
		current = came_from[-1]
		current.make_path()
		came_from.pop()
		draw()

def solve_dfs(draw, start, end):
		"""
		Solves the maze using depth-first search algorithm with int delay ms.
		"""
		stack = []
		stack.append(start)
		visited = {}

		came_from = []

		while stack:
			current = stack[-1]
			came_from.append(current)
			visited[current] = current
			if current == end:
				draw_path(came_from, draw)
				end.make_end()
				return True
			
			for neighbor in current.neighbors:
				if neighbor not in visited:
					stack.append(neighbor)
					if neighbor != start:
						neighbor.make_open()
			draw()
			if current != start:
					current.make_closed()

		return False


def solve_bfs(draw, start, end):
		"""
		Solves the maze using depth-first search algorithm with int delay ms.
		"""
		queue = deque()
		queue.append(start)
		visited = {}
		came_from = {}
		while queue:
			current = queue.popleft()
			if current in visited:
				continue
			visited[current] = current
			if current == end:
				reconstruct_path(came_from, end, draw)
				end.make_end()
				return True
			for neighbor in current.neighbors:
				if neighbor not in visited:
					came_from[neighbor] = current
					queue.append(neighbor)
					neighbor.make_open()
					
			draw()
			if current != start:
				current.make_closed()


		return False
				
def make_grid(rows, width):
	grid = []
	gap = width // rows
	for i in range(rows):
		grid.append([])
		for j in range(rows):
			spot = Spot(i, j, gap, rows)
			grid[i].append(spot)

	return grid


def draw_grid(win, rows, width):
	gap = width // rows
	for i in range(rows):
		pygame.draw.line(win, GREY, (0, i * gap), (width, i * gap))
		for j in range(rows):
			pygame.draw.line(win, GREY, (j * gap, 0), (j * gap, width))


def draw(win, grid, rows, width):
	for row in grid:
		for spot in row:
			spot.draw(win)

	draw_grid(win, rows, width)
	pygame.display.update()


def get_clicked_pos(pos, rows, width):
	gap = width // rows
	y, x = pos

	row = y // gap
	col = x // gap

	return row, col


def within_bounds(rows):
	pos = pygame.mouse.get_pos()
	row, col = get_clicked_pos(pos, rows, WINDOW_HEIGHT)
	if row > rows - 1:
		return False
	elif col > rows - 1:
		return False
	return True

def main():
	pygame.init()
	clock = pygame.time.Clock()
	WIN = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
	pygame.display.set_caption("Path Visualizer by Jinrong Pettit")

	FPS = constants.FPS
	GUI_X = constants.GUI_X
	GUI_Y = constants.GUI_Y
	GUI_X_CENTER = constants.GUI_X_CENTER
	SLIDER_SIZE = constants.SLIDER_SIZE
	SLIDER_X = GUI_X_CENTER - int (SLIDER_SIZE[0] / 2)

	SOL_ALGORITHMS = constants.SOL_ALGORITHMS

	manager = pygame_gui.UIManager((WINDOW_WIDTH, WINDOW_HEIGHT))

	gui = (GUI_X, GUI_Y, int(WINDOW_WIDTH / 3), WINDOW_HEIGHT)
	font = pygame.font.Font('freesansbold.ttf', 28)
	text = font.render("Path Visualizer", True, WHITE)
	text_rect = text.get_rect()
	text_rect.center = (GUI_X_CENTER, 50)

	solve_label = pygame_gui.elements.UILabel(relative_rect=pygame.Rect((SLIDER_X, 195), SLIDER_SIZE),
																								 text="Pathing Algorithms",
																								 manager=manager)
	solve_menu = pygame_gui.elements.UIDropDownMenu(options_list=SOL_ALGORITHMS,
																									starting_option=SOL_ALGORITHMS[0],
																									relative_rect=pygame.Rect((SLIDER_X, 220), SLIDER_SIZE),
																									manager=manager)
	solve_button = pygame_gui.elements.UIButton(relative_rect=pygame.Rect(GUI_X_CENTER - 50, 260, 100, 50),
																								 text='Solve',
																								 manager=manager)

	ROWS = 50
	
	grid = make_grid(ROWS, WINDOW_HEIGHT)

	start = None
	end = None

	run = True

	while run:
		WIN.fill(WHITE)
		pygame.draw.rect(WIN, DARK_GREY, gui)
		WIN.blit(text, text_rect)
		manager.draw_ui(WIN)

		time_delta = clock.tick(FPS)/1000.0

		draw(WIN, grid, ROWS, WINDOW_HEIGHT)
		pygame.display.update()
		solve_menu.enable()
		solve_button.enable()
		for event in pygame.event.get():
			manager.process_events(event)
			manager.update(time_delta)
			if event.type == pygame.QUIT:
				run = False
		
			if pygame.mouse.get_pressed()[0] and within_bounds(ROWS) : # LEFT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, WINDOW_HEIGHT)
				spot = grid[row][col]
				
				if not start and spot != end:
					start = spot
					start.make_start()

				elif not end and spot != start:
					end = spot
					end.make_end()

				elif spot != end and spot != start:
					spot.make_barrier()

			elif pygame.mouse.get_pressed()[2] and within_bounds(ROWS): # RIGHT
				pos = pygame.mouse.get_pos()
				row, col = get_clicked_pos(pos, ROWS, WINDOW_HEIGHT)
				spot = grid[row][col]
				spot.reset()
				if spot == start:
					start = None
				elif spot == end:
					end = None

			if event.type == pygame.USEREVENT:
				if event.user_type == pygame_gui.UI_BUTTON_PRESSED and start and end:
					for row in grid:
						for spot in row:
							spot.update_neighbors(grid)
					if event.ui_element == solve_button:
						algorithm = solve_menu.selected_option
						if algorithm == "DFS":
							solve_dfs(lambda: draw(WIN, grid, ROWS, WINDOW_HEIGHT), start, end)
						elif algorithm == "BFS":
							solve_bfs(lambda: draw(WIN, grid, ROWS, WINDOW_HEIGHT), start, end)
						elif algorithm == "A*":
							algorithm(lambda: draw(WIN, grid, ROWS, WINDOW_HEIGHT), grid, start, end)


			if event.type == pygame.KEYDOWN:
				if event.key == pygame.K_c:
					start = None
					end = None
					grid = make_grid(ROWS, WINDOW_HEIGHT)

	pygame.quit()

if __name__ == "__main__":
	main()