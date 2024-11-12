import tkinter as tk
from tkinter import messagebox
import openai
import random

openai.api_key = "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"

class Team:
    def __init__(self, name, color, is_computer=False):
        self.name = name
        self.color = color
        self.score = 0
        self.is_computer = is_computer




class Square:
    def __init__(self, row, col, button):
        self.row = row
        self.col = col
        self.button = button
        self.state = "empty"

    def mark(self, letter, team):
        self.state = "full"
        self.button.config(text=letter, fg=team.color)
        return f"{team.name} placed '{letter}' at ({self.row}, {self.col})"


class Board:
    def __init__(self, root, rows, cols, on_square_click):
        self.rows = rows
        self.cols = cols
        self.squares = {}
        self.on_square_click = on_square_click
        self.create_board(root)

    def create_board(self, root):
        for row in range(self.rows):
            for col in range(self.cols):
                button = tk.Button(root, text="", width=5, height=2,
                                   command=lambda r=row, c=col: self.on_square_click(r, c))
                button.grid(row=row + 4, column=col, padx=2, pady=2)
                self.squares[(row, col)] = Square(row, col, button)

    def get_square(self, row, col):
        return self.squares.get((row, col))

    def reset_board(self):
        for square in self.squares.values():
            square.state = "empty"
            square.button.config(text="")

class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("SOS Game - Save vs Souls")
        
        self.team_save = Team("Red", "red")
        self.team_souls = Team("Blue", "blue")

        self.current_team = self.team_save

        self.game_mode = "simple"
        self.board_size = 5
        self.letter_choice = tk.StringVar(value="S")
        self.setup_ui()
        self.board = None




    def make_computer_move(self):
        board_state = self.get_board_state()
        n = self.board_size  # The size of the board

        prompt = (
            f"Given this SOS board state that is a MATRIX i.e. a square, starting at the top left square:\n{board_state}\n"
            f"Choose the best move for {self.current_team.name} by providing a row, column, "
            f"and either 'S' or 'O' based on the board state. Only select row and column numbers between 0 and {n-1} "
            f"as to avoid going over the playable area. Also, you can only select a square that is currently empty.\n"
            f"Respond in the format: row, column, letter (e.g., '2, 3, S' or '2, 3, O')."
        )

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an assistant playing the SOS game strategically."},
                    {"role": "user", "content": prompt}
                ]
            )
            move_text = response['choices'][0]['message']['content'].strip()
            move = move_text.split(",")

            if len(move) == 3:
                row, col, letter = int(move[0].strip()), int(move[1].strip()), move[2].strip().upper()
                
                # Validate the move: check bounds, letter, and if the square is empty
                if (
                    0 <= row < n and 0 <= col < n and  # within bounds
                    letter in ['S', 'O'] and  # valid letter
                    self.board.get_square(row, col).state == "empty"  # empty square
                ):
                    self.letter_choice.set(letter)  # Set the chosen letter for the computer
                    self.handle_move(row, col)
                else:
                    print("GPT chose an invalid move (out-of-bounds, occupied square, or incorrect letter). Choosing a random valid move.")
                    self.random_move()  # Fallback if GPT chooses an invalid move
            else:
                print("GPT did not respond with the correct format. Choosing a random move as a fallback.")
                self.random_move()  # Fallback if GPT returns an invalid format
        except Exception as e:
            print(f"Error with GPT: {e}")
            self.random_move()














    def get_board_state(self):
        state = ""
        for row in range(self.board_size):
            for col in range(self.board_size):
                square = self.board.get_square(row, col)
                state += square.button["text"] if square.button["text"] else "."
            state += "\n"
        return state
    

    def handle_move(self, row, col):
        square = self.board.get_square(row, col)
        selected_letter = self.letter_choice.get()
        message = square.mark(selected_letter, self.current_team)
        self.status_label.config(text=message)

        score = self.check_sos(row, col, selected_letter)
        if score:
            self.current_team.score += score
            self.status_label.config(text=f"{self.current_team.name} scored! {self.current_team.score} points")
            
            # Simple mode: End the game if an SOS is formed
            if self.game_mode == "simple" and score > 0:
                self.end_game(f"{self.current_team.name} wins by making an SOS!")
                return

        # If the board is full in general mode, determine the winner by score
        if self.game_mode == "general" and not any(sq.state == "empty" for sq in self.board.squares.values()):
            winner = self.get_winner()
            self.end_game(f"{winner} wins with Save: {self.team_save.score}, Souls: {self.team_souls.score}!")
        else:
            self.switch_turn()




    def switch_turn(self):
        self.current_team = self.team_souls if self.current_team == self.team_save else self.team_save
        self.turn_label.config(text=f"Current turn: {self.current_team.name}")

        if self.current_team.is_computer:
            self.make_computer_move()




    def random_move(self):
        empty_squares = [(row, col) for (row, col), square in self.board.squares.items() if square.state == "empty"]
        if empty_squares:
            row, col = random.choice(empty_squares)
            self.handle_move(row, col)





    def setup_ui(self):
        tk.Label(self.root, text="Choose letter:").grid(row=0, column=0, columnspan=2)
        tk.Radiobutton(self.root, text="S", variable=self.letter_choice, value="S").grid(row=1, column=0)
        tk.Radiobutton(self.root, text="O", variable=self.letter_choice, value="O").grid(row=1, column=1)

        tk.Label(self.root, text="Game Mode:").grid(row=2, column=0, columnspan=2)
        self.mode_choice = tk.StringVar(value="simple")
        tk.Radiobutton(self.root, text="Simple", variable=self.mode_choice, value="simple").grid(row=3, column=0)
        tk.Radiobutton(self.root, text="General", variable=self.mode_choice, value="general").grid(row=3, column=1)

        tk.Label(self.root, text="Board Size:").grid(row=0, column=2, columnspan=2)
        self.board_size_entry = tk.Entry(self.root, width=5)
        self.board_size_entry.grid(row=1, column=2, columnspan=2)
        self.board_size_entry.insert(0, "5")

        tk.Button(self.root, text="Start New Game", command=self.start_new_game).grid(row=2, column=2, columnspan=2)
        
        self.status_label = tk.Label(self.root, text="Click a square to fill it",
                                     font=("Helvetica", 14, "bold"), bg="lightblue",
                                     fg="darkblue", pady=10, padx=10, borderwidth=2, relief="groove")
        self.status_label.grid(row=12, column=0, columnspan=10, pady=10)

        self.turn_label = tk.Label(self.root, text=f"Current turn: {self.current_team.name}",
                                   font=("Helvetica", 12, "bold"), bg="lightgrey", fg="black", pady=5)
        self.turn_label.grid(row=13, column=0, columnspan=10, pady=10)

    def start_new_game(self):
        try:
            self.board_size = int(self.board_size_entry.get())
            if self.board_size < 3:
                raise ValueError("Board size must be at least 3.")
        except ValueError:
            messagebox.showerror("Invalid Board Size", "Please enter a valid integer greater than 2.")
            return

        self.game_mode = self.mode_choice.get()
        self.team_save.is_computer = messagebox.askyesno("Select Player", "Is Red team a computer?")
        self.team_souls.is_computer = messagebox.askyesno("Select Player", "Is Blue team a computer?")
        self.current_team = self.team_save
        self.team_save.score = 0
        self.team_souls.score = 0
        self.status_label.config(text="Click a square to fill it")
        self.turn_label.config(text=f"Current turn: {self.current_team.name}")

        if self.board:
            self.board.reset_board()
        else:
            self.board = Board(self.root, self.board_size, self.board_size, self.on_square_click)


    def on_square_click(self, row, col):
        if self.current_team.is_computer:
            self.make_computer_move()
        else:
            square = self.board.get_square(row, col)
            if square.state == "full":
                self.status_label.config(text=f"Square ({row}, {col}) is already full")
            else:
                selected_letter = self.letter_choice.get()
                message = square.mark(selected_letter, self.current_team)
                self.status_label.config(text=message)

                score = self.check_sos(row, col, selected_letter)
                if score:
                    self.current_team.score += score
                    self.status_label.config(text=f"{self.current_team.name} scored! {self.current_team.score} points")
                    if self.game_mode == "simple" and score > 0:
                        self.end_game(f"{self.current_team.name} wins by making the first SOS!")
                        return

                if not any(sq.state == "empty" for sq in self.board.squares.values()):
                    winner = self.get_winner()
                    self.end_game(f"{winner} wins with Save: {self.team_save.score}, Souls: {self.team_souls.score}!")
                else:
                    self.switch_turn()


    def check_sos(self, row, col, letter):
        score = 0
        # Define directions to check in each of the eight possible orientations
        directions = [
            (-1, -1), (-1, 0), (-1, 1),  # Diagonal up-left, vertical up, diagonal up-right
            (0, -1),         (0, 1),      # Horizontal left, horizontal right
            (1, -1),  (1, 0), (1, 1)      # Diagonal down-left, vertical down, diagonal down-right
        ]

        for drow, dcol in directions:
            # Case 1: Current letter is "S" and it's the start of "SOS"
            if (letter == "S" and
                self.get_letter_at(row + drow, col + dcol) == "O" and
                self.get_letter_at(row + 2 * drow, col + 2 * dcol) == "S"):
                score += 1

            # Case 2: Current letter is "O" and it's the middle of "SOS"
            if (letter == "O" and
                self.get_letter_at(row - drow, col - dcol) == "S" and
                self.get_letter_at(row + drow, col + dcol) == "S"):
                score += 1

            # Case 3: Current letter is "S" and it's the end of "SOS"
            if (letter == "S" and
                self.get_letter_at(row - 2 * drow, col - 2 * dcol) == "S" and
                self.get_letter_at(row - drow, col - dcol) == "O"):
                score += 1

        return score

    # Helper function to safely get the letter at a given position
    def get_letter_at(self, row, col):
        square = self.board.get_square(row, col)
        return square.button["text"] if square and square.state == "full" else None








    def check_line(self, row, col, letter, offset1, offset2):
        def get_square_content(r, c):
            sq = self.board.get_square(r, c)
            return sq.button["text"] if sq else None

        # "S" at start, "O" in middle, "S" at end (SOS)
        if letter == "O":
            return (get_square_content(row + offset1[0], col + offset1[1]) == "S" and
                    get_square_content(row + offset2[0], col + offset2[1]) == "S")
        elif letter == "S":
            return (get_square_content(row + offset1[0], col + offset1[1]) == "O" and
                    get_square_content(row - offset1[0], col - offset1[1]) == "S")
        return False

    def get_winner(self):
        if self.team_save.score > self.team_souls.score:
            return self.team_save.name
        elif self.team_save.score < self.team_souls.score:
            return self.team_souls.name
        return "It's a tie!"


    def end_game(self, message):
        messagebox.showinfo("Game Over", message)
        self.start_new_game()


    def switch_turn(self):
        self.current_team = self.team_souls if self.current_team == self.team_save else self.team_save
        self.turn_label.config(text=f"Current turn: {self.current_team.name}")




# Start the Tkinter event loop
root = tk.Tk()
game = Game(root)
root.mainloop()
