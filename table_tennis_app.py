import pandas as pd
import datetime
import tkinter as tk
from tkinter import ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from graphics_utils import create_player_stats_figure  # Import the new function
import os  # Import os module to handle file paths

# Initialize or load game data
try:
    games_df = pd.read_csv('table_tennis_games.csv')
except FileNotFoundError:
    games_df = pd.DataFrame(columns=['Player 1', 'Player 2', 'Date', 'Score Player 1', 'Score Player 2', 'Winner', 'Game Type'])

# Initialize or load player stats
try:
    stats_df = pd.read_csv('table_tennis_player_stats.csv')
    if 'Playoff Wins' not in stats_df.columns:
        stats_df['Playoff Wins'] = 0
except FileNotFoundError:
    stats_df = pd.DataFrame(columns=[
        'Player', 'Points Scored (Regular)', 'Points Conceded (Regular)', 'Wins (Regular)', 'Losses (Regular)',
        'Points Scored (Playoff)', 'Points Conceded (Playoff)', 'Wins (Playoff)', 'Losses (Playoff)', 'Playoff Wins'
    ])

def update_player_stats(player, points_scored, points_conceded, won, game_type, playoff_winning_game=False):
    global stats_df
    if player not in stats_df['Player'].values:
        new_player = pd.DataFrame({
            'Player': [player],
            'Points Scored (Regular)': [0],
            'Points Conceded (Regular)': [0],
            'Wins (Regular)': [0],
            'Losses (Regular)': [0],
            'Points Scored (Playoff)': [0],
            'Points Conceded (Playoff)': [0],
            'Wins (Playoff)': [0],
            'Losses (Playoff)': [0],
            'Playoff Wins': [0]  # Ensure this column is initialized
        })
        stats_df = pd.concat([stats_df, new_player], ignore_index=True)

    if game_type == 'Regular':
        stats_df.loc[stats_df['Player'] == player, 'Points Scored (Regular)'] += points_scored
        stats_df.loc[stats_df['Player'] == player, 'Points Conceded (Regular)'] += points_conceded
        if won:
            stats_df.loc[stats_df['Player'] == player, 'Wins (Regular)'] += 1
        else:
            stats_df.loc[stats_df['Player'] == player, 'Losses (Regular)'] += 1
    else:  # Playoff
        stats_df.loc[stats_df['Player'] == player, 'Points Scored (Playoff)'] += points_scored
        stats_df.loc[stats_df['Player'] == player, 'Points Conceded (Playoff)'] += points_conceded
        if won:
            stats_df.loc[stats_df['Player'] == player, 'Wins (Playoff)'] += 1
            if playoff_winning_game:
                stats_df.loc[stats_df['Player'] == player, 'Playoff Wins'] += 1
        else:
            stats_df.loc[stats_df['Player'] == player, 'Losses (Playoff)'] += 1

    stats_df.to_csv('table_tennis_player_stats.csv', index=False)

def add_game(player1, player2, score1, score2, game_type='Regular', playoff_winning_game=False):
    date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    winner = player1 if score1 > score2 else player2
    new_game = pd.DataFrame({
        'Player 1': [player1],
        'Player 2': [player2],
        'Date': [date],
        'Score Player 1': [score1],
        'Score Player 2': [score2],
        'Winner': [winner],
        'Game Type': [game_type]
    })
    global games_df
    games_df = pd.concat([games_df, new_game], ignore_index=True)
    games_df.to_csv('table_tennis_games.csv', index=False)

    update_player_stats(player1, score1, score2, score1 > score2, game_type, playoff_winning_game)
    update_player_stats(player2, score2, score1, score2 > score1, game_type, playoff_winning_game)

def calculate_head_to_head(player1, player2, game_type):
    games_between = games_df[((games_df['Player 1'] == player1) & (games_df['Player 2'] == player2) & (games_df['Game Type'] == game_type)) |
                             ((games_df['Player 1'] == player2) & (games_df['Player 2'] == player1) & (games_df['Game Type'] == game_type))]
    if games_between.empty:
        return {
            'points_scored': 0,
            'points_conceded': 0,
            'wins': 0,
            'losses': 0
        }

    points_scored = games_between[games_between['Player 1'] == player1]['Score Player 1'].sum() + \
                    games_between[games_between['Player 2'] == player1]['Score Player 2'].sum()
    points_conceded = games_between[games_between['Player 1'] == player1]['Score Player 2'].sum() + \
                      games_between[games_between['Player 2'] == player1]['Score Player 1'].sum()
    wins = len(games_between[games_between['Winner'] == player1])
    losses = len(games_between[games_between['Winner'] == player2])

    return {
        'points_scored': points_scored,
        'points_conceded': points_conceded,
        'wins': wins,
        'losses': losses
    }

def show_player_stats(player):
    player_stats = stats_df[stats_df['Player'] == player]
    if player_stats.empty:
        return "No stats available for this player."

    championships_won = player_stats['Playoff Wins'].values[0]
    emoji_trophy = "\U0001F3C6"  # Trophy emoji

    result = f"{player}'s Stats:\n"
    result += f"Championships Won: {championships_won} {emoji_trophy}\n\n"

    result += "Regular Season:\n"
    result += f"  Points Scored: {player_stats['Points Scored (Regular)'].values[0]}\n"
    result += f"  Points Conceded: {player_stats['Points Conceded (Regular)'].values[0]}\n"
    result += f"  Wins: {player_stats['Wins (Regular)'].values[0]}\n"
    result += f"  Losses: {player_stats['Losses (Regular)'].values[0]}\n\n"
    result += "Playoffs:\n"
    result += f"  Points Scored: {player_stats['Points Scored (Playoff)'].values[0]}\n"
    result += f"  Points Conceded: {player_stats['Points Conceded (Playoff)'].values[0]}\n"
    result += f"  Wins: {player_stats['Wins (Playoff)'].values[0]}\n"
    result += f"  Losses: {player_stats['Losses (Playoff)'].values[0]}\n"
    result += f"  Playoff Series Wins: {player_stats['Playoff Wins'].values[0]}\n\n"

    # Head-to-Head Stats
    result += "Head-to-Head:\n"
    for opponent in stats_df['Player'].values:
        if opponent != player:
            head_to_head_regular = calculate_head_to_head(player, opponent, 'Regular')
            head_to_head_playoff = calculate_head_to_head(player, opponent, 'Playoff')
            win_rate_head_to_head_regular = head_to_head_regular['wins'] / (head_to_head_regular['wins'] + head_to_head_regular['losses']) if (head_to_head_regular['wins'] + head_to_head_regular['losses']) > 0 else 0
            win_rate_head_to_head_playoff = head_to_head_playoff['wins'] / (head_to_head_playoff['wins'] + head_to_head_playoff['losses']) if (head_to_head_playoff['wins'] + head_to_head_playoff['losses']) > 0 else 0
            result += f"  vs {opponent} (Regular Season):\n"
            result += f"    Points Scored: {head_to_head_regular['points_scored']}\n"
            result += f"    Points Conceded: {head_to_head_regular['points_conceded']}\n"
            result += f"    Wins: {head_to_head_regular['wins']}\n"
            result += f"    Losses: {head_to_head_regular['losses']}\n"
            result += f"    Win Rate: {win_rate_head_to_head_regular:.2f}\n\n"
            result += f"  vs {opponent} (Playoffs):\n"
            result += f"    Points Scored: {head_to_head_playoff['points_scored']}\n"
            result += f"    Points Conceded: {head_to_head_playoff['points_conceded']}\n"
            result += f"    Wins: {head_to_head_playoff['wins']}\n"
            result += f"    Losses: {head_to_head_playoff['losses']}\n"
            result += f"    Win Rate: {win_rate_head_to_head_playoff:.2f}\n\n"

    return result

def on_player_select(event):
    selected_player = player_combobox.get()
    player_stats_text.set(show_player_stats(selected_player))
    update_player_graph(selected_player)

def update_player_graph(player):
    fig = create_player_stats_figure(player, stats_df)
    for widget in graph_frame.winfo_children():
        widget.destroy()
    if fig:
        canvas = FigureCanvasTkAgg(fig, master=graph_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

def sanitize_player_names(players):
    sanitized_names = []
    for name in players:
        sanitized_names.append(name.replace("]", "").replace("[", "").replace('"', "").replace("'", ""))
    return sanitized_names

# Create the main window
root = tk.Tk()
root.title("Table Tennis Stats")

# Set the initial size of the window
root.geometry("1200x800")

# Load an image and display it
trophy_image_path = os.path.join(os.path.dirname(__file__), "trophy.png")
try:
    trophy_image = tk.PhotoImage(file=trophy_image_path)
except tk.TclError:
    trophy_image = None

# Configure the main window to expand with the content
root.rowconfigure(0, weight=1)
root.columnconfigure(0, weight=1)

# Notebook widget for tabs
notebook = ttk.Notebook(root)
notebook.grid(row=0, column=0, sticky="nsew")

# Frame for player stats
player_stats_frame = ttk.Frame(notebook)
notebook.add(player_stats_frame, text='Player Stats')

# Frame for adding game data
add_game_frame = ttk.Frame(notebook)
notebook.add(add_game_frame, text='Add Game')

# Configure player_stats_frame to expand with the content
player_stats_frame.rowconfigure(0, weight=1)
player_stats_frame.columnconfigure(0, weight=1)

# Canvas and Scrollbar for player stats
canvas = tk.Canvas(player_stats_frame)
scrollbar = ttk.Scrollbar(player_stats_frame, orient="vertical", command=canvas.yview)
scrollable_frame = ttk.Frame(canvas)

scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(
        scrollregion=canvas.bbox("all")
    )
)

canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

# Sanitize player names
sanitized_player_names = sanitize_player_names(stats_df['Player'].values)

# Dropdown to select player in player stats tab
player_combobox = ttk.Combobox(scrollable_frame, values=sanitized_player_names)
player_combobox.bind("<<ComboboxSelected>>", on_player_select)
player_combobox.pack(pady=10)

# Text area to show player stats
player_stats_text = tk.StringVar()
player_stats_label = tk.Label(scrollable_frame, textvariable=player_stats_text, justify='left')
player_stats_label.pack(pady=10, side=tk.LEFT, anchor='n')

# Frame for player graph
graph_frame = ttk.Frame(scrollable_frame)
graph_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

# Display the image at the top of the player stats
if trophy_image:
    trophy_label = tk.Label(scrollable_frame, image=trophy_image)
    trophy_label.pack(side=tk.TOP, pady=10)

def add_game_form():
    for widget in add_game_frame.winfo_children():
        widget.destroy()

    tk.Label(add_game_frame, text="Player 1:").grid(row=0, column=0)
    player1_entry = ttk.Combobox(add_game_frame, values=sanitized_player_names)
    player1_entry.grid(row=0, column=1)

    tk.Label(add_game_frame, text="Player 2:").grid(row=1, column=0)
    player2_entry = ttk.Combobox(add_game_frame, values=sanitized_player_names)
    player2_entry.grid(row=1, column=1)

    tk.Label(add_game_frame, text="Score Player 1:").grid(row=2, column=0)
    score1_entry = tk.Entry(add_game_frame)
    score1_entry.grid(row=2, column=1)

    tk.Label(add_game_frame, text="Score Player 2:").grid(row=3, column=0)
    score2_entry = tk.Entry(add_game_frame)
    score2_entry.grid(row=3, column=1)

    tk.Label(add_game_frame, text="Game Type:").grid(row=4, column=0)
    game_type_entry = ttk.Combobox(add_game_frame, values=["Regular", "Playoff"])
    game_type_entry.grid(row=4, column=1)

    playoff_winning_game_var = tk.BooleanVar()
    playoff_winning_game_check = tk.Checkbutton(add_game_frame, text="Playoff Winning Game", variable=playoff_winning_game_var)
    playoff_winning_game_check.grid(row=5, columnspan=2)

    def save_game():
        player1 = player1_entry.get()
        player2 = player2_entry.get()
        score1 = int(score1_entry.get())
        score2 = int(score2_entry.get())
        game_type = game_type_entry.get()
        playoff_winning_game = playoff_winning_game_var.get()
        add_game(player1, player2, score1, score2, game_type, playoff_winning_game)
        add_game_form()

    save_button = tk.Button(add_game_frame, text="Save", command=save_game)
    save_button.grid(row=6, column=0, columnspan=2)

add_game_form()

# Initialize with the first player's stats and graph
if not stats_df.empty:
    player_combobox.current(0)
    player_stats_text.set(show_player_stats(stats_df['Player'].values[0]))
    update_player_graph(stats_df['Player'].values[0])

root.mainloop()
