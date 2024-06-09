# Othello Board Game Project

![Othello](https://github.com/MohamedEssam71/Othello-Game-AI/assets/101371937/903efb0a-8177-4170-beed-328fa0af10bf)

## Overview

This project involves implementing the Othello board game in Prolog or Python. The game should be playable in Human vs. Computer mode, and the computer's moves should be decided using the alpha-beta pruning algorithm.

## Project Requirements

- **Group Work:** Students must work in groups of 3-4, either from the same lab or from another lab taught by the same TA.
- **Playing Mode:** The game must include Human vs. Computer mode. Projects without this mode will not be graded.
- **Algorithm:** Utilize the alpha-beta pruning algorithm for computer moves. No other algorithms are allowed.
- **Languages:** The project can be implemented in Prolog or Python only.

## Grading Criteria

The project will be graded based on the following components:

1. **Game Controller:** 
   - Organizes the game by switching roles between the two players.
   - Receives the user's move, updates the game board, and declares the "End of Game."

2. **Knowledge Representation:** 
   - Suitable representation of the game state.

3. **Utility Function:** 
   - Evaluates the current game state with respect to a given player.

4. **Alpha-Beta Pruning Algorithm:**
   - Implementation of the algorithm (a draft implementation was illustrated in the lab).

5. **Difficulty Levels:** 
   - Support for different difficulty levels (Easy, Medium, Hard), characterized by the depth of the algorithm (e.g., Easy 1, Medium 3, Hard 5).

6. **Bonus:** 
   - User interface in any language (Java, C#, Python, etc.)

## About Othello

Othello is a strategy board game for two players, played on an 8×8 uncheckered board. The game involves two players using 64 identical game pieces ("disks") that are white on one side and black on the other. Each player chooses one color and competes to have the majority of disks showing their color by the end of the game.

### Game Setup

- Initially, the board is set up with two black disks and two white disks at the center, as shown below.
- The remaining 60 disks are divided between players, each receiving 30 disks.

### How the Game Goes

1. **Player's Turn:** 
   - Find an empty square adjacent to an opponent’s piece.
   - Place a disk with your color facing upwards.

2. **Outflanking:**
   - Enclose a row or column of opponent’s pieces between two of your disks.
   - Flip the enclosed opponent’s disks to your color.

3. **Capture:**
   - Flipped disks count as your pieces.

4. **Turn Passing:**
   - After a move, pass the turn to the opponent.

5. **End of Game:**
   - The game ends when no more moves are possible for either player.
   - The player with the majority of disks showing their color wins.

### Game Rules

- **First Move:** Black always moves first.
- **Skipping Turns:** If a player cannot outflank and flip at least one opposing disk, they miss their turn.
- **Outflanking:** A disk can outflank any number of disks in one or more rows in any direction (horizontally or vertically).
- **No Skipping:** Players may not skip over their own color disks to outflank an opposing disk.
- **Direct Line:** Disks must be outflanked as a direct result of a move.
- **Running Out of Pieces:** The game may end if a player runs out of pieces.

### Resources

To get familiar with the game, you can play Othello online: [Play Othello](https://www.eothello.com/)

## Setup and Installation

1. Install the necessary Python packages:
   ```bash
   pip3 install customtkinter
   pip3 install pillow
   ```
2. Install the font named "Poetsen_One".
3. Enjoy

# Contributors

* [Ahmed Abd El-Wahab](https://github.com/AliveTube)
* [Mohamed Khaled (Amin)](https://github.com/emailam)
* [Alan Samir](https://github.com/alanhakoun)
* [Mohamed Essam](https://github.com/MohamedEssam71)
