from customtkinter import *
from PIL import Image, ImageTk
import math
import pygame
from copy import deepcopy
import time
import threading

app = CTk()
app.title("Othello Game")
app.geometry("600x600")
frame_middle = None
hide_panel = False
screen = None
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 144, 103)
WIDTH = 600
HEIGHT = 600
SQUARE_SIZE = WIDTH // 8
PADDING = 10
BORDER = 1
RADIUS = SQUARE_SIZE // 2 - PADDING
dx = [+0, +0, -1, +1, +1, +1, -1, -1]  # left , right , up , down , downright , downleft , upright , upleft
dy = [-1, +1, +0, +0, +1, -1, +1, -1]


# --------------------------------------------------------------
class Piece:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.x = -1
        self.y = -1
        self.calc_center()

    def calc_center(self):
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def draw_piece(self):
        pygame.draw.circle(screen, (0, 0, 0), (self.x, self.y), RADIUS + BORDER)
        pygame.draw.circle(screen, self.color, (self.x, self.y), RADIUS)

    def reset(self):
        radius = SQUARE_SIZE // 2 - PADDING
        # back and front circle
        pygame.draw.circle(screen, GREEN, (self.x, self.y), radius + BORDER)
        pygame.draw.circle(screen, self.color, (self.x, self.y), radius)


class Board:
    def __init__(self):
        self.board = []
        self.create_board()
        self.count_white = 2
        self.count_black = 2

    def create_board(self):
        self.board = [[0 for i in range(8)] for j in range(8)]
        self.board[3][8 // 2 - 1] = Piece(WHITE, 3, 8 // 2 - 1)
        self.board[3][8 // 2] = Piece(BLACK, 3, 8 // 2)
        self.board[4][8 // 2 - 1] = Piece(BLACK, 4, 8 // 2 - 1)
        self.board[4][8 // 2] = Piece(WHITE, 4, 8 // 2)

    def draw_board(self):
        self.draw_square()
        self.count_black = self.count_white = 0
        for row in range(8):
            for col in range(8):
                if self.board[row][col] != 0:
                    self.board[row][col].draw_piece()
                    if self.board[row][col].color == WHITE:
                        self.count_white += 1
                    elif self.board[row][col].color == BLACK:
                        self.count_black += 1
        pygame.display.update()

    def update_piece(self, piece):
        self.board[piece.row][piece.col] = piece

    def draw_square(self):
        screen.fill(BLACK)
        for row in range(8):
            size = SQUARE_SIZE - 2 if row != 7 else SQUARE_SIZE
            for col in range(8):
                pygame.draw.rect(screen, GREEN, (row * SQUARE_SIZE, col * SQUARE_SIZE, size, SQUARE_SIZE - 2))

    def valid(self, x, y):
        return 8 > x >= 0 and 0 <= y < 8 and self.board[x][y] != 0 and self.board[x][y].color != GREEN

    def valid2(self, x, y):
        return 8 > x >= 0 and 8 > y >= 0 == self.board[x][y]

    def get_all_available_moves(self, color):
        valid_set = set()
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece != 0 and piece.color == color:
                    for k in range(8):
                        cnt = 0
                        x = dx[k] + row
                        y = dy[k] + col
                        while self.valid(x, y) and self.board[x][y].color != color:
                            x += dx[k]
                            y += dy[k]
                            cnt = cnt + 1
                        if cnt == 0 or not self.valid2(x, y):
                            continue
                        else:
                            valid_set.add(((row, col), (x, y), (dx[k], dy[k])))
        return valid_set

    def get_piece(self, row, col):
        return self.board[row][col]

    def set_piece(self, row, col, piece):
        self.board[row][col] = piece


def get_row_col_from_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col


class Game:
    def __init__(self, difficulty):
        self.difficulty = difficulty
        self.current_player = BLACK
        self.board = Board()
        self.valid_moves = set()

    def play(self):
        run = True
        clock = pygame.time.Clock()
        self.board.draw_board()
        th1 = threading.Thread(target=update_counters, args=(self.board.count_black, self.board.count_white))
        th1.start()

        while run:
            clock.tick(60)
            self.show_available()
            black_finish = False
            if not self.valid_moves:
                black_finish = True
            while self.current_player == BLACK and not black_finish:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit()
                    if event.type == pygame.MOUSEBUTTONDOWN:
                        pos = pygame.mouse.get_pos()
                        row, col = get_row_col_from_mouse(pos)
                        if self.update_board(row, col):
                            black_finish = True
                            self.fill_sandwich(BLACK, row, col)
                            break
            th1 = threading.Thread(target=update_counters, args=(self.board.count_black, self.board.count_white))
            th1.start()
            # white plays
            self.delete_green()
            self.change_player()
            if self.check_endgame():
                self.print_winner()
                break

            self.ai_move()
            self.delete_green()
            self.change_player()
            th1 = threading.Thread(target=update_counters, args=(self.board.count_black, self.board.count_white))
            th1.start()

    def update_board(self, row, col):
        ok = False
        for move in self.valid_moves:
            start_x, start_y = move[0][0], move[0][1]
            end_x, end_y = move[1][0], move[1][1]
            dx, dy = move[2][0], move[2][1]
            if row == end_x and col == end_y:
                ok = True
                self.board.update_piece(Piece(self.current_player, end_x, end_y))
                i = start_x
                j = start_y
                while i != end_x or j != end_y:
                    i += dx
                    j += dy
                    if 8 > i >= 0 and 0 <= j < 8:
                        self.board.update_piece(Piece(self.current_player, i, j))
        self.board.draw_board()
        pygame.display.update()
        return ok

    def show_available(self):
        self.valid_moves = self.board.get_all_available_moves(self.current_player)
        for move in self.valid_moves:
            end_x, end_y = move[1][0], move[1][1]
            self.board.update_piece(Piece(GREEN, end_x, end_y))
            self.board.get_piece(end_x, end_y).draw_piece()
        pygame.display.update()

    def delete_green(self):
        for i in range(8):
            for j in range(8):
                piece = self.board.get_piece(i, j)
                if piece != 0 and piece.color == GREEN:
                    self.board.get_piece(i, j).reset()
                    self.board.set_piece(i, j, 0)
        pygame.display.update()

    def change_player(self):
        if self.current_player == BLACK:
            self.current_player = WHITE
        else:
            self.current_player = BLACK

    def print_winner(self):
        if self.board.count_white > self.board.count_black:
            print("WHITE WINS")
            th1 = threading.Thread(target=change_label_winner, args=("WHITE",))
            th1.start()
        elif self.board.count_black > self.board.count_white:
            print("BLACK WINS")
            th1 = threading.Thread(target=change_label_winner, args=("BLACK",))
            th1.start()
        else:
            print("Draw")
            th1 = threading.Thread(target=change_label_winner, args=("DRAW",))
            th1.start()

    def check_endgame(self):
        if self.board.count_black + self.board.count_white == 64:
            return True
        elif not self.board.get_all_available_moves(BLACK) and not self.board.get_all_available_moves(WHITE):
            return True
        else:
            return False

    def evaluate(self, move, player):
        board_copy = deepcopy(self.board)
        if move:
            start_x, start_y = move[0][0], move[0][1]
            end_x, end_y = move[1][0], move[1][1]
            dx, dy = move[2][0], move[2][1]
            board_copy.update_piece(Piece(player, end_x, end_y))
            i = start_x
            j = start_y
            while i != end_x or j != end_y:
                i += dx
                j += dy
                if board_copy.valid2(i, j):
                    board_copy.update_piece(Piece(player, i, j))
                    break
        return board_copy.count_white - board_copy.count_black if player == WHITE else board_copy.count_black - board_copy.count_white

    def minimax_alpha_beta(self, move, depth, alpha, beta, maximizing_player):
        if depth == 0 or self.check_endgame():
            return self.evaluate(move, maximizing_player)

        if maximizing_player == BLACK:
            max_eval = -math.inf
            self.valid_moves = self.board.get_all_available_moves(maximizing_player)
            for move in self.valid_moves:
                my_eval = self.minimax_alpha_beta(move, depth - 1, alpha, beta, WHITE)
                max_eval = max(max_eval, my_eval)
                alpha = max(alpha, my_eval)
                if alpha >= beta:
                    break
            return max_eval
        else:
            min_eval = math.inf
            self.valid_moves = self.board.get_all_available_moves(maximizing_player)
            for move in self.valid_moves:
                my_eval = self.minimax_alpha_beta(move, depth - 1, alpha, beta, BLACK)
                min_eval = min(min_eval, my_eval)
                beta = min(beta, my_eval)
                if alpha >= beta:
                    break
            return min_eval

    def ai_move(self):
        best_move = None
        best_score = -math.inf
        self.valid_moves = self.board.get_all_available_moves(WHITE)

        for move in self.valid_moves:
            score = self.minimax_alpha_beta(move, self.difficulty, math.inf, -math.inf, BLACK)
            if score >= best_score:
                best_score = score
                best_move = move
        if best_move:
            start_x, start_y = best_move[0][0], best_move[0][1]
            end_x, end_y = best_move[1][0], best_move[1][1]
            dx, dy = best_move[2][0], best_move[2][1]
            self.board.update_piece(Piece(WHITE, end_x, end_y))
            i = start_x
            j = start_y
            while i != end_x or j != end_y:
                i += dx
                j += dy
                if 8 > i >= 0 and 0 <= j < 8:
                    self.board.update_piece(Piece(WHITE, i, j))
            self.fill_sandwich(WHITE, end_x, end_y)
            self.board.draw_board()
            return True
        else:
            return False

    def fill_sandwich(self, color, i, j):
        for k in range(8):
            row = i
            col = j
            row += dx[k]
            col += dy[k]
            cnt = 0
            while self.board.valid(row, col) and self.board.get_piece(row, col).color != color:
                row += dx[k]
                col += dy[k]
                cnt += 1
            if cnt == 0 or not (0 <= row < 8 and 0 <= col < 8):
                continue
            elif cnt != 0 and self.board.get_piece(row, col) != 0 and self.board.get_piece(row, col).color == color:
                start_x = i
                start_y = j
                end_x = row
                end_y = col
                while start_x != end_x or start_y != end_y:
                    start_x += dx[k]
                    start_y += dy[k]
                    if 0 <= start_x < 8 and 0 <= start_y < 8:
                        self.board.update_piece(Piece(color, start_x, start_y))
                    else:
                        break
        self.board.draw_board()


# --------------------------------------------------------------

def start_game2(difficulty_level):
    global screen
    global hide_panel
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    game = Game(difficulty_level)
    game.play()
    # time.sleep(3)
    hide_panel = False

    time.sleep(3)
    pygame.quit()
    th2 = threading.Thread(target=show_Start_again)
    th2.start()


def show_Start_again():
    frame_start.pack_forget()
    frame_middle.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
    return_label_counter()


def start_game():
    global hide_panel
    if not hide_panel:
        frame_middle.pack_forget()
        frame_start.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
        hide_panel = True
    else:
        frame_start.pack_forget()
        frame_middle.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
        hide_panel = False

    difficulty = radio_var.get()
    game_thread = threading.Thread(target=start_game2, args=(difficulty,))
    game_thread.start()


def click_handler_setting():
    global hide_panel
    if not hide_panel:
        frame_middle.pack_forget()
        frame_start.pack_forget()
        frame_info.pack_forget()
        frame_setting.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
        hide_panel = True
    else:
        frame_setting.pack_forget()
        frame_middle.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
        hide_panel = False


def click_handler_info():
    global hide_panel
    if not hide_panel:
        frame_middle.pack_forget()
        frame_start.pack_forget()
        frame_setting.pack_forget()
        frame_info.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
        hide_panel = True
    else:
        frame_info.pack_forget()
        frame_middle.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
        hide_panel = False


# ------------------Upper Title-------------------------
frame_title = CTkFrame(master=app, fg_color="#007351", border_width=2)
frame_title.configure(height=200)
frame_title.pack_propagate(False)
frame_title.pack(pady=0, padx=0, fill='x', expand=True, anchor='n', )
# -------------------------------------------


# ------------------Middle Title-------------------------
frame_middle = CTkFrame(master=app, fg_color="#007351", border_width=2)
frame_middle.configure(height=800, width=800)
frame_middle.pack_propagate(False)
frame_middle.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')

# ------------------Middle start-------------------------
# Open and resize the image
img_back = Image.open("images/background6.png")
img_back_resized = img_back.resize((520, 320))

# Create a PhotoImage from the resized PIL Image
photo_image = ImageTk.PhotoImage(img_back_resized)

# Create a CTkCanvas and add the image to it
canvas = CTkCanvas(master=frame_middle, width=520, height=320, bg="#007351",
                   highlightcolor="#007351", highlightthickness=0)
canvas.create_image(0, 0, image=photo_image, anchor='nw')
canvas.place(x=110, y=5)

btn_start = CTkButton(master=frame_middle, text="Start", font=("PoetsenOne", 60),
                      corner_radius=32, fg_color="#007351",
                      hover_color="#000000", command=start_game)
btn_start.configure(width=200, height=80)
btn_start.pack(pady=50, padx=0, expand=True, anchor='s')

# ------------------Settings-------------------------
frame_setting = CTkFrame(master=app, fg_color="#007351", border_width=2)
frame_setting.configure(height=800, width=800)
frame_setting.pack_propagate(False)

img_setting = Image.open("images\settings.png")
btn_setting = CTkButton(master=frame_title, text="", corner_radius=32,
                        image=CTkImage(dark_image=img_setting,
                                       light_image=img_setting),
                        fg_color="#007351", hover_color="#007351",
                        command=click_handler_setting)

btn_setting.configure(width=0, height=0)
btn_setting.pack(pady=2, padx=3, expand=True, anchor='nw')

# ------------------Radio Buttons-------------------------
radio_var = IntVar()
radio_easy = CTkRadioButton(master=frame_setting, text="Easy",
                            variable=radio_var, value=1, fg_color="#FFFFFF",
                            text_color="#FFFFFF", font=("PoetsenOne", 40),
                            border_color="black")

radio_easy.pack(pady=0, padx=0, expand=True, anchor='center')
radio_easy.select()

radio_medium = CTkRadioButton(master=frame_setting, text="Medium",
                              variable=radio_var, value=3, fg_color="#FFFFFF",
                              text_color="#FFFFFF", font=("PoetsenOne", 40),
                              border_color="black")
radio_medium.pack(pady=0, padx=182, expand=True, anchor='e')

radio_hard = CTkRadioButton(master=frame_setting, text="Hard",
                            variable=radio_var, value=5, fg_color="#FFFFFF",
                            text_color="#FFFFFF", font=("PoetsenOne", 40),
                            border_color="black")
radio_hard.pack(pady=0, padx=0, expand=True, anchor='center')

# ------------------Info-------------------------
frame_info = CTkFrame(master=app, fg_color="#007351", border_width=2)
frame_info.configure(height=800, width=800)
frame_info.pack_propagate(False)

img_info = Image.open("images\info.png")
btn_info = CTkButton(master=frame_title, text="", corner_radius=32,
                     image=CTkImage(dark_image=img_info,
                                    light_image=img_info),
                     fg_color="#007351", hover_color="#007351",
                     command=click_handler_info)
btn_info.configure(width=0, height=0)
btn_info.pack(pady=2, padx=3, expand=True, anchor='nw')

textbox = CTkTextbox(master=frame_info, fg_color="#007351", text_color="#FFFFFF", font=("PoetsenOne", 20),
                     border_width=2, corner_radius=20, scrollbar_button_color="#000000")
textbox.pack(pady=0, padx=0, fill='both', expand=True, anchor='center')
textbox.insert("0.0", "**About Othello** \t\n"
                      "\nOthello is a strategy board game for two players,"
                      "\nplayed on an 8×8 uncheckered board. Two players"
                      "\ncompete, using 64 identical game pieces (disks)"
                      "\nthat are white on one side and black on the other."
                      "\nEach player chooses one color to use throughout"
                      "\nthe game. Players take turns placing one disk on an"
                      "\nempty square, with their assigned color facing up."
                      "\nAfter a play is made, any disks of the opponent's"
                      "\ncolor that lie in a straight line bounded by the one"
                      "\njust played and another one in the current player's"
                      "\ncolor are turned over. When all playable empty"
                      "\nsquares are filled, the player with more disks"
                      "\nshowing in their own color wins the game."
                      "\n\n**GameSetup**\n\t"
                      "● Initially, the board is set up by placing\n\t two black disks"
                      "\n\t and two white disks at the center of the board \n\texactly as shown"
                      "\n\tin the opposite figure. The game always begins \n\twith this setup."
                      "\n\t● Then, the remaining 60 disks are divided\n\t between players"
                      "\n\tsuch that each player has 30 disks."
                      "\n\n**Team Members**\n"
                      "\tMohamed Essam Mahmoud Osman\n"
                      "\tAhmed Mohamed Abd El-Wahab\n"
                      "\tMohamed Khaled Elsayed Omran\n"
                      "\tAlan Samir Hakoun\n")
# -------------------------------------------

frame_start = CTkFrame(master=app, fg_color="#007351", border_width=2)
frame_start.configure(height=800, width=800)
frame_start.pack_propagate(False)

# ------------------Upper Title-------------------------
label_title = CTkLabel(master=frame_title, text="Othello", text_color="#FFFFFF", font=("PoetsenOne", 100))
label_title.pack(pady=0, padx=0, expand=True, anchor='center')


def update_counters(count, count2):
    label_black.configure(text=f"{count} Blacks")
    label_white.configure(text=f"{count2} Whites")


label_black = CTkLabel(master=frame_start, text="2 Blacks", font=("PoetsenOne", 60),
                       text_color="#FFFFFF")
label_black.pack(pady=0, padx=0, expand=True, anchor='center')

label_white = CTkLabel(master=frame_start, text="2 Whites", font=("PoetsenOne", 60),
                       text_color="#FFFFFF")
label_white.pack(pady=0, padx=0, expand=True, anchor='center')


def change_label_winner(color):
    label_black.pack_forget()
    label_white.pack_forget()
    label_winner.pack(pady=0, padx=0, expand=True, anchor='center')
    if color != "DRAW":
        label_winner.configure(text=f"{color} Wins !")
    else:
        label_winner.configure(text=f"{color} !")


def return_label_counter():
    label_winner.pack_forget()
    label_black.pack(pady=0, padx=0, expand=True, anchor='center')
    label_white.pack(pady=0, padx=0, expand=True, anchor='center')


label_winner = CTkLabel(master=frame_start, text="", font=("PoetsenOne", 60),
                        text_color="#FFFFFF")
label_winner.pack(pady=0, padx=0, expand=True, anchor='center')

app.mainloop()