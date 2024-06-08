# graphics_utils.py
import matplotlib.pyplot as plt
import pandas as pd

def create_player_stats_figure(player, stats_df):
    player_stats = stats_df[stats_df['Player'] == player]
    if player_stats.empty:
        print(f"No stats available for player: {player}")
        return None

    fig, ax = plt.subplots(2, 1, figsize=(8, 10))

    # Plot points scored and conceded
    labels = ['Points Scored (Regular)', 'Points Scored (Playoff)', 'Points Conceded (Regular)', 'Points Conceded (Playoff)']
    points = [player_stats['Points Scored (Regular)'].values[0], player_stats['Points Scored (Playoff)'].values[0],
              player_stats['Points Conceded (Regular)'].values[0], player_stats['Points Conceded (Playoff)'].values[0]]
    ax[0].bar(labels, points, color=['blue', 'blue', 'red', 'red'])
    ax[0].set_title(f"Points Scored vs Conceded for {player}", fontsize=14)
    ax[0].tick_params(axis='x', rotation=45, labelsize=10)
    ax[0].tick_params(axis='y', labelsize=12)

    # Plot win/loss ratio
    labels = ['Wins (Regular)', 'Losses (Regular)', 'Wins (Playoff)', 'Losses (Playoff)']
    win_loss_data = [player_stats['Wins (Regular)'].values[0], player_stats['Losses (Regular)'].values[0],
                     player_stats['Wins (Playoff)'].values[0], player_stats['Losses (Playoff)'].values[0]]
    ax[1].bar(labels, win_loss_data, color=['green', 'red', 'green', 'red'])
    ax[1].set_title(f"Win/Loss Ratio for {player}", fontsize=14)
    ax[1].tick_params(axis='x', rotation=45, labelsize=10)
    ax[1].tick_params(axis='y', labelsize=12)

    plt.tight_layout()
    return fig
