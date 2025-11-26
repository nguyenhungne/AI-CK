# Go Game 9x9

A Python implementation of the classic board game Go on a 9x9 board, featuring both human vs human and human vs AI gameplay modes.

## Features

- **9x9 Go Board**: Traditional Go gameplay on a smaller board
- **Two Game Modes**:
  - Human vs Human: Two players take turns on the same computer
  - Human vs AI: Play against a computer opponent
- **Heuristic Minimax AI**: Computer opponent using alpha-beta pruning
- **Full Go Rules**: Including captures, Ko rule, and territory scoring
- **Friendly UI**: Mouse-based interaction with visual feedback

## Requirements

- Python 3.8+
- Pygame

## Installation

```bash
pip install pygame
```

## Running the Game

```bash
python main.py
```

## How to Play

1. **Start**: The game begins in Human vs Human mode
2. **Place Stones**: Click on any intersection to place a stone
3. **Alternate Turns**: Black plays first, then players alternate
4. **Capture**: Surround opponent stones to capture them
5. **Pass/Resign**: Use the buttons on the right panel
6. **Switch Mode**: Click "vs Human" or "vs AI" to change game mode

## AI Implementation

### Heuristic Function

The AI evaluates board positions using four components:

**H(board) = w1×Territory + w2×GroupStrength + w3×Captures + w4×Strategic**

| Component | Weight | Description |
|-----------|--------|-------------|
| Territory | 1.0 | Empty intersections influenced by player's stones |
| GroupStrength | 1.5 | Sum of (liberties × group_size) for all groups |
| Captures | 2.0 | Captured stones and potential captures (atari) |
| Strategic | 0.8 | Bonus for corners (3), edges (2), star points (2) |

### Depth Limit Strategy

The search depth adapts to the game phase:

| Game Phase | Empty Positions | Depth | Rationale |
|------------|-----------------|-------|-----------|
| Opening | > 60 | 2 | High branching factor |
| Middle | 30-60 | 3 | Balanced search |
| Endgame | < 30 | 4 | Lower branching factor |

### Optimizations

- **Alpha-Beta Pruning**: Reduces search space by ~50%
- **Move Ordering**: Prioritizes captures and strategic positions
- **Transposition Table**: Caches up to 10,000 evaluated positions
- **Move Filtering**: Limits moves to positions near existing stones

## Project Structure

```
├── main.py                 # Application entry point
├── src/
│   ├── models/
│   │   ├── board.py        # Board state and Go rules
│   │   └── game_state.py   # Game state tracking
│   ├── controllers/
│   │   └── game_controller.py  # Game flow management
│   ├── ai/
│   │   ├── minimax.py      # Minimax with alpha-beta pruning
│   │   └── heuristic.py    # Position evaluation
│   ├── players/
│   │   ├── player.py       # Abstract player class
│   │   ├── human_player.py # Human player implementation
│   │   └── ai_player.py    # AI player implementation
│   └── ui/
│       ├── game_ui.py      # Pygame UI
│       └── button.py       # UI button component
```

## Controls

- **Left Click**: Place stone on intersection
- **New Game**: Start a new game
- **Pass**: Skip your turn
- **Resign**: Forfeit the game
- **vs Human/vs AI**: Switch game mode

## Scoring

The game uses Chinese scoring rules:
- Count stones on the board
- Count territory (empty points surrounded by one color)
- Add captured stones
- White receives 6.5 komi (compensation for going second)
