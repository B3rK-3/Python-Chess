# Python Chess Engine
This is a python chess module developed from scratch with Stockfish implemented or any chess AI for that matter with only a few changes to the code.

## Guide / Installation
```bash
git clone https://github.com/B3rK-3/Python-Chess.git
cd Python-Chess
```

If you directly want to run the Engine you can just do
```bash
python runtime.py
```
This fires up the GUI and the actual game.

### Classes

*ChessEngine.py*

Includes: 
1. GameState
- GameState is the class that contains all the methods for move generation and validation. This class also contains the board which may be modified as pleased.
2. Move
- The Move class contains a notation as ```__str__``` method, and static methods getSquare used to turn array indexes to chess coordinates, parseSquare doess the opposite and it returns the chess coordinates to array indexes (also handles things like pawn promotion).
3. PGN
- FEN also known as Forsyth-Edwards Notation converts array boards to to strings that express the current state of the board, [FEN documentation](https://www.chess.com/terms/fen-chess).

*interface.py*

Includes multiple methods responsible for rendering the game. Some important ones:
1. drawBoard
- Draws the board background.
2. drawPlaces
- Draws the places on the rows and columns, "12345678" on rows and "abcdefgh" on columns.
3. drawPieces
- Draws the pieces using the preloaded ones in loadImages.

---

### Feel free to modify the code as you like!