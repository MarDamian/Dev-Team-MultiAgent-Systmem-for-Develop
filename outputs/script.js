// Constants for piece types and players
const PLAYER_1 = 1;
const PLAYER_2 = 2;
const EMPTY = 0;
const PAWN_1 = 1;
const PAWN_2 = 2;
const KING_1 = 3; // King for player 1
const KING_2 = 4; // King for player 2

// UI Elements
const boardElement = document.getElementById('board');
const turnDisplay = document.getElementById('turn-display');
const messageDisplay = document.getElementById('message-display');
const resetButton = document.getElementById('reset-button');

// Frontend UI State (minimal, reflects what backend sends)
let currentGameState = {
    board: [],
    currentPlayer: PLAYER_1,
    selectedPiece: null, // { row, col } of selected piece
    possibleMoves: [],  // Array of { row, col, isCapture } for selected piece
    gameOver: false,
    gameMessage: ''
};

// --- State Pattern Implementation ---

// Base State Class
class GameState {
    constructor(context) {
        this.context = context;
    }

    // Default implementations for actions. Concrete states will override these.
    selectPiece(row, col) {
        this.context.setMessage("Invalid action in current game state.");
        return { selectedPiece: null, possibleMoves: [] };
    }

    makeMove(fromR, fromC, toR, toC) {
        this.context.setMessage("Invalid action in current game state.");
        return false;
    }

    deselectPiece() {
        this.context.setMessage("No piece is selected to deselect.");
    }

    // Getters for UI to reflect current state
    getPossibleMoves() { return []; }
    getSelectedPiece() { return null; }
    getGameMessage() { return this.context.gameMessage; }
}

// Concrete State: No Piece Selected (Initial State, or after a move)
class NoPieceSelectedState extends GameState {
    constructor(context) {
        super(context);
        this.context.setSelectedPiece(null);
        this.context.setPossibleMoves([]);
        this.context.setMessage(''); // Clear message when no piece is selected
    }

    selectPiece(row, col) {
        if (this.context.gameOver) {
            this.context.setMessage("Game is over!");
            return { selectedPiece: null, possibleMoves: [] };
        }

        const piece = this.context.board[row][col];
        if (piece === EMPTY || !this.context.isPlayerPiece(piece, this.context.currentPlayer)) {
            this.context.setMessage("That's not your piece or an empty square.");
            return { selectedPiece: null, possibleMoves: [] };
        }

        const mandatoryCaptures = this.context.getMandatoryCaptures(this.context.board, this.context.currentPlayer);
        let validMoves = [];

        if (mandatoryCaptures.length > 0) {
            const capturesForThisPiece = mandatoryCaptures.filter(m => m.from.row === row && m.from.col === col);
            if (capturesForThisPiece.length > 0) {
                validMoves = capturesForThisPiece.map(m => ({ row: m.to.row, col: m.to.col, isCapture: true, captured: m.captured }));
                this.context.setMessage("You must make a capture!");
                this.context.changeState(new PieceSelectedState(this.context, { row, col }, validMoves));
                return { selectedPiece: { row, col }, possibleMoves: validMoves };
            } else {
                this.context.setMessage("You must select a piece that can make a capture!");
                return { selectedPiece: null, possibleMoves: [] };
            }
        } else {
            const allMoves = this.context.getAllMovesForPiece(row, col, this.context.board, this.context.currentPlayer);
            if (allMoves.length > 0) {
                this.context.setMessage('');
                this.context.changeState(new PieceSelectedState(this.context, { row, col }, allMoves));
                return { selectedPiece: { row, col }, possibleMoves: allMoves };
            } else {
                this.context.setMessage("This piece has no valid moves.");
                return { selectedPiece: null, possibleMoves: [] };
            }
        }
    }
}

// Concrete State: A Piece is Selected, awaiting a move or deselection
class PieceSelectedState extends GameState {
    constructor(context, selectedPieceCoords, possibleMoves) {
        super(context);
        this.context.setSelectedPiece(selectedPieceCoords);
        this.context.setPossibleMoves(possibleMoves);
        // Message might be set by NoPieceSelectedState if it was a mandatory capture
    }

    selectPiece(row, col) {
        if (this.context.gameOver) {
            this.context.setMessage("Game is over!");
            return { selectedPiece: null, possibleMoves: [] };
        }

        // If clicking the same piece, deselect it
        if (this.context.selectedPiece && this.context.selectedPiece.row === row && this.context.selectedPiece.col === col) {
            this.deselectPiece();
            return { selectedPiece: null, possibleMoves: [] };
        }

        // Otherwise, try to select a new piece
        const piece = this.context.board[row][col];
        if (piece === EMPTY || !this.context.isPlayerPiece(piece, this.context.currentPlayer)) {
            this.context.setMessage("That's not your piece or an empty square.");
            return { selectedPiece: this.context.selectedPiece, possibleMoves: this.context.possibleMoves }; // Keep current selection
        }

        const mandatoryCaptures = this.context.getMandatoryCaptures(this.context.board, this.context.currentPlayer);
        let validMoves = [];

        if (mandatoryCaptures.length > 0) {
            const capturesForThisPiece = mandatoryCaptures.filter(m => m.from.row === row && m.from.col === col);
            if (capturesForThisPiece.length > 0) {
                validMoves = capturesForThisPiece.map(m => ({ row: m.to.row, col: m.to.col, isCapture: true, captured: m.captured }));
                this.context.setMessage("You must make a capture!");
                this.context.changeState(new PieceSelectedState(this.context, { row, col }, validMoves));
                return { selectedPiece: { row, col }, possibleMoves: validMoves };
            } else {
                this.context.setMessage("You must select a piece that can make a capture!");
                return { selectedPiece: this.context.selectedPiece, possibleMoves: this.context.possibleMoves }; // Keep current selection
            }
        } else {
            const allMoves = this.context.getAllMovesForPiece(row, col, this.context.board, this.context.currentPlayer);
            if (allMoves.length > 0) {
                this.context.setMessage('');
                this.context.changeState(new PieceSelectedState(this.context, { row, col }, allMoves));
                return { selectedPiece: { row, col }, possibleMoves: allMoves };
            } else {
                this.context.setMessage("This piece has no valid moves.");
                return { selectedPiece: this.context.selectedPiece, possibleMoves: this.context.possibleMoves }; // Keep current selection
            }
        }
    }

    makeMove(fromR, fromC, toR, toC) {
        if (this.context.gameOver) {
            this.context.setMessage("Game is over!");
            return false;
        }
        if (!this.context.selectedPiece || this.context.selectedPiece.row !== fromR || this.context.selectedPiece.col !== fromC) {
            this.context.setMessage("Invalid move: Piece not selected or not the correct piece.");
            return false;
        }

        const targetMove = this.context.possibleMoves.find(move => move.row === toR && move.col === toC);

        if (!targetMove) {
            this.context.setMessage("Invalid move: Not a possible move for the selected piece.");
            return false;
        }

        // Execute the move
        const piece = this.context.board[fromR][fromC];
        this.context.board[toR][toC] = piece;
        this.context.board[fromR][fromC] = EMPTY;

        // Handle captures
        if (targetMove.isCapture) {
            const capturedRow = targetMove.captured.row;
            const capturedCol = targetMove.captured.col;
            this.context.board[capturedRow][capturedCol] = EMPTY;

            // Check for further captures with the same piece (multi-capture)
            const furtherCaptures = this.context.getCapturesForPiece(toR, toC, this.context.board, this.context.currentPlayer);
            if (furtherCaptures.length > 0) {
                const possibleFurtherMoves = furtherCaptures.map(m => ({ row: m.to.row, col: m.to.col, isCapture: true, captured: m.captured }));
                this.context.setMessage("You must continue capturing!");
                this.context.changeState(new CapturingState(this.context, { row: toR, col: toC }, possibleFurtherMoves));
                return true; // Move successful, but turn not ended
            }
        }

        // King Promotion
        this.context.promotePiece(toR, toC);

        // If no further captures, or it was a non-capture move, end turn
        this.context.checkGameOver();
        if (!this.context.gameOver) {
            this.context.switchTurn();
            this.context.changeState(new NoPieceSelectedState(this.context));
        } else {
            this.context.changeState(new GameOverState(this.context));
        }
        return true;
    }

    deselectPiece() {
        this.context.changeState(new NoPieceSelectedState(this.context));
    }

    getPossibleMoves() {
        return this.context.possibleMoves;
    }

    getSelectedPiece() {
        return this.context.selectedPiece;
    }
}

// Concrete State: A Piece is in a multi-capture sequence
class CapturingState extends GameState {
    constructor(context, capturingPieceCoords, possibleCaptures) {
        super(context);
        this.context.setSelectedPiece(capturingPieceCoords); // The piece that must continue capturing
        this.context.setPossibleMoves(possibleCaptures); // Only capture moves for this piece
        this.context.setMessage("You must continue capturing!");
    }

    selectPiece(row, col) {
        if (this.context.gameOver) {
            this.context.setMessage("Game is over!");
            return { selectedPiece: null, possibleMoves: [] };
        }
        // Only allow re-selecting the piece that is currently capturing
        if (this.context.selectedPiece && this.context.selectedPiece.row === row && this.context.selectedPiece.col === col) {
            this.context.setMessage("You must continue capturing with this piece!");
            return { selectedPiece: this.context.selectedPiece, possibleMoves: this.context.possibleMoves };
        } else {
            this.context.setMessage("You must continue capturing with the selected piece!");
            return { selectedPiece: this.context.selectedPiece, possibleMoves: this.context.possibleMoves };
        }
    }

    makeMove(fromR, fromC, toR, toC) {
        if (this.context.gameOver) {
            this.context.setMessage("Game is over!");
            return false;
        }
        if (!this.context.selectedPiece || this.context.selectedPiece.row !== fromR || this.context.selectedPiece.col !== fromC) {
            this.context.setMessage("Invalid move: Piece not selected or not the correct piece for multi-capture.");
            return false;
        }

        const targetMove = this.context.possibleMoves.find(move => move.row === toR && move.col === toC && move.isCapture);

        if (!targetMove) {
            this.context.setMessage("Invalid move: You must make a capture with the selected piece.");
            return false;
        }

        // Execute the move
        const piece = this.context.board[fromR][fromC];
        this.context.board[toR][toC] = piece;
        this.context.board[fromR][fromC] = EMPTY;

        // Handle capture
        const capturedRow = targetMove.captured.row;
        const capturedCol = targetMove.captured.col;
        this.context.board[capturedRow][capturedCol] = EMPTY;

        // Check for further captures with the same piece
        const furtherCaptures = this.context.getCapturesForPiece(toR, toC, this.context.board, this.context.currentPlayer);
        if (furtherCaptures.length > 0) {
            const possibleFurtherMoves = furtherCaptures.map(m => ({ row: m.to.row, col: m.to.col, isCapture: true, captured: m.captured }));
            this.context.setMessage("You must continue capturing!");
            this.context.changeState(new CapturingState(this.context, { row: toR, col: toC }, possibleFurtherMoves));
            return true; // Move successful, but turn not ended
        }

        // King Promotion
        this.context.promotePiece(toR, toC);

        // If no further captures, end turn
        this.context.checkGameOver();
        if (!this.context.gameOver) {
            this.context.switchTurn();
            this.context.changeState(new NoPieceSelectedState(this.context));
        } else {
            this.context.changeState(new GameOverState(this.context));
        }
        return true;
    }

    deselectPiece() {
        this.context.setMessage("You must continue capturing with this piece!");
    }

    getPossibleMoves() {
        return this.context.possibleMoves;
    }

    getSelectedPiece() {
        return this.context.selectedPiece;
    }
}

// Concrete State: Game Over
class GameOverState extends GameState {
    constructor(context) {
        super(context);
        this.context.setGameOver(true);
        this.context.setSelectedPiece(null);
        this.context.setPossibleMoves([]);
        // Message should already be set by checkGameOver
    }

    selectPiece(row, col) {
        this.context.setMessage("Game is over! Please reset to play again.");
        return { selectedPiece: null, possibleMoves: [] };
    }

    makeMove(fromR, fromC, toR, toC) {
        this.context.setMessage("Game is over! Please reset to play again.");
        return false;
    }

    deselectPiece() {
        this.context.setMessage("Game is over! Please reset to play again.");
    }
}


// The GameContext manages the internal state of the game and holds the current state object.
class GameContext {
    constructor() {
        this.board = [];
        this.currentPlayer = PLAYER_1;
        this.gameOver = false;
        this.gameMessage = '';
        this.selectedPiece = null; // { row, col }
        this.possibleMoves = []; // Array of { row, col, isCapture }
        this.state = null; // Current state object

        this.initGame(); // Initialize the game on creation
    }

    changeState(newState) {
        this.state = newState;
    }

    // --- Context Setters (for states to update context properties) ---
    setBoard(newBoard) { this.board = newBoard; }
    setCurrentPlayer(player) { this.currentPlayer = player; }
    setGameOver(isOver) { this.gameOver = isOver; }
    setMessage(message) { this.gameMessage = message; }
    setSelectedPiece(piece) { this.selectedPiece = piece; }
    setPossibleMoves(moves) { this.possibleMoves = moves; }

    // --- Core Game Logic (Helpers, independent of current state) ---

    // Helper to check if a piece belongs to a player
    isPlayerPiece(piece, player) {
        if (player === PLAYER_1) return piece === PAWN_1 || piece === KING_1;
        if (player === PLAYER_2) return piece === PAWN_2 || piece === KING_2;
        return false;
    }

    // Helper to check if a piece is an opponent's piece
    isOpponentPiece(piece, player) {
        if (player === PLAYER_1) return piece === PAWN_2 || piece === KING_2;
        if (player === PLAYER_2) return piece === PAWN_1 || piece === KING_1;
        return false;
    }

    // Helper to get all capture moves for a specific piece
    getCapturesForPiece(r, c, currentBoard, player) {
        const captures = [];
        const piece = currentBoard[r][c];
        if (piece === EMPTY || !this.isPlayerPiece(piece, player)) return captures;

        const isKing = (piece === KING_1 || piece === KING_2);
        const directions = isKing ?
            [{ dr: -1, dc: -1 }, { dr: -1, dc: 1 }, { dr: 1, dc: -1 }, { dr: 1, dc: 1 }] :
            (player === PLAYER_1 ? [{ dr: -1, dc: -1 }, { dr: -1, dc: 1 }] : [{ dr: 1, dc: -1 }, { dr: 1, dc: 1 }]);

        for (const dir of directions) {
            const opponentR = r + dir.dr;
            const opponentC = c + dir.dc;
            const jumpR = r + 2 * dir.dr;
            const jumpC = c + 2 * dir.dc;

            // Check if opponent piece is in between and landing spot is empty and within bounds
            if (
                opponentR >= 0 && opponentR < 8 && opponentC >= 0 && opponentC < 8 &&
                jumpR >= 0 && jumpR < 8 && jumpC >= 0 && jumpC < 8 &&
                this.isOpponentPiece(currentBoard[opponentR][opponentC], player) &&
                currentBoard[jumpR][jumpC] === EMPTY
            ) {
                captures.push({ from: { row: r, col: c }, to: { row: jumpR, col: jumpC }, captured: { row: opponentR, col: opponentC } });
            }
        }
        return captures;
    }

    // Helper to get all possible moves (including captures) for a piece
    getAllMovesForPiece(r, c, currentBoard, player) {
        const moves = [];
        const piece = currentBoard[r][c];
        if (piece === EMPTY || !this.isPlayerPiece(piece, player)) return moves;

        const isKing = (piece === KING_1 || piece === KING_2);
        const directions = isKing ?
            [{ dr: -1, dc: -1 }, { dr: -1, dc: 1 }, { dr: 1, dc: -1 }, { dr: 1, dc: 1 }] :
            (player === PLAYER_1 ? [{ dr: -1, dc: -1 }, { dr: -1, dc: 1 }] : [{ dr: 1, dc: -1 }, { dr: 1, dc: 1 }]);

        for (const dir of directions) {
            const newR = r + dir.dr;
            const newC = c + dir.dc;

            // Check bounds for the immediate next cell
            if (newR >= 0 && newR < 8 && newC >= 0 && newC < 8) {
                // Normal move (one step diagonal to an empty cell)
                if (currentBoard[newR][newC] === EMPTY) {
                    moves.push({ row: newR, col: newC, isCapture: false });
                } else {
                    // Check for capture move
                    const opponentPiece = currentBoard[newR][newC];
                    if (this.isOpponentPiece(opponentPiece, player)) {
                        const jumpR = r + 2 * dir.dr; // Landing spot after jump
                        const jumpC = c + 2 * dir.dc;

                        // Check bounds for jump landing spot and if it's empty
                        if (jumpR >= 0 && jumpR < 8 && jumpC >= 0 && jumpC < 8 && currentBoard[jumpR][jumpC] === EMPTY) {
                            moves.push({ row: jumpR, col: jumpC, isCapture: true, captured: { row: newR, col: newC } });
                        }
                    }
                }
            }
        }
        return moves;
    }

    // Get all mandatory capture moves for the current player
    getMandatoryCaptures(currentBoard, player) {
        let allCaptures = [];
        for (let r = 0; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                if (this.isPlayerPiece(currentBoard[r][c], player)) {
                    allCaptures = allCaptures.concat(this.getCapturesForPiece(r, c, currentBoard, player));
                }
            }
        }
        return allCaptures;
    }

    // Initialize the game state
    initGame() {
        this.board = Array(8).fill(0).map(() => Array(8).fill(EMPTY));

        // Place Player 1's pieces (bottom of the board)
        for (let r = 5; r < 8; r++) {
            for (let c = 0; c < 8; c++) {
                if ((r + c) % 2 !== 0) { // Dark squares
                    this.board[r][c] = PAWN_1;
                }
            }
        }

        // Place Player 2's pieces (top of the board)
        for (let r = 0; r < 3; r++) {
            for (let c = 0; c < 8; c++) {
                if ((r + c) % 2 !== 0) { // Dark squares
                    this.board[r][c] = PAWN_2;
                }
            }
        }

        this.currentPlayer = PLAYER_1;
        this.gameOver = false;
        this.gameMessage = '';
        this.selectedPiece = null;
        this.possibleMoves = [];
        this.changeState(new NoPieceSelectedState(this)); // Set initial state
    }

    // Switch current player
    switchTurn() {
        this.currentPlayer = (this.currentPlayer === PLAYER_1) ? PLAYER_2 : PLAYER_1;
        this.gameMessage = ''; // Clear any previous message
    }

    // King Promotion
    promotePiece(row, col) {
        const piece = this.board[row][col];
        const isPlayer1Pawn = (piece === PAWN_1);
        const isPlayer2Pawn = (piece === PAWN_2);
        if (isPlayer1Pawn && row === 0) { // Player 1 (red) reaches top row
            this.board[row][col] = KING_1;
        } else if (isPlayer2Pawn && row === 7) { // Player 2 (blue) reaches bottom row
            this.board[row][col] = KING_2;
        }
    }

    // Check for game over conditions
    checkGameOver() {
        let player1Pieces = 0;
        let player2Pieces = 0;

        this.board.forEach(row => {
            row.forEach(cellValue => {
                if (cellValue === PAWN_1 || cellValue === KING_1) {
                    player1Pieces++;
                } else if (cellValue === PAWN_2 || cellValue === KING_2) {
                    player2Pieces++;
                }
            });
        });

        if (player1Pieces === 0) {
            this.gameOver = true;
            this.gameMessage = 'Game Over! Player 2 Wins!';
        } else if (player2Pieces === 0) {
            this.gameOver = true;
            this.gameMessage = 'Game Over! Player 1 Wins!';
        } else {
            // Check if current player has any valid moves (including captures)
            let hasMoves = false;
            const currentMandatoryCaptures = this.getMandatoryCaptures(this.board, this.currentPlayer);

            if (currentMandatoryCaptures.length > 0) {
                hasMoves = true;
            } else {
                for (let r = 0; r < 8; r++) {
                    for (let c = 0; c < 8; c++) {
                        if (this.isPlayerPiece(this.board[r][c], this.currentPlayer)) {
                            const moves = this.getAllMovesForPiece(r, c, this.board, this.currentPlayer);
                            if (moves.length > 0) {
                                hasMoves = true;
                                break;
                            }
                        }
                    }
                    if (hasMoves) break;
                }
            }

            if (!hasMoves) {
                this.gameOver = true;
                this.gameMessage = `Game Over! Player ${this.currentPlayer === PLAYER_1 ? '2' : '1'} Wins! (Player ${this.currentPlayer} has no valid moves)`;
            }
        }
    }

    // --- Public API for Frontend to interact with the game ---

    selectPiece(row, col) {
        return this.state.selectPiece(row, col);
    }

    makeMove(fromR, fromC, toR, toC) {
        return this.state.makeMove(fromR, fromC, toR, toC);
    }

    deselectPiece() {
        this.state.deselectPiece();
    }

    getCurrentGameState() {
        return {
            board: JSON.parse(JSON.stringify(this.board)), // Deep copy
            currentPlayer: this.currentPlayer,
            selectedPiece: this.state.getSelectedPiece(),
            possibleMoves: this.state.getPossibleMoves(),
            gameOver: this.gameOver,
            gameMessage: this.state.getGameMessage()
        };
    }
}

// Instantiate the GameContext, which will manage the game logic and states
const gameContext = new GameContext();


// --- Frontend UI Logic ---

// Update the UI based on the current game state
function updateUI() {
    // Get the current state from the game context
    currentGameState = gameContext.getCurrentGameState();

    // Update board
    boardElement.innerHTML = ''; // Clear existing board
    currentGameState.board.forEach((row, r) => {
        row.forEach((cellValue, c) => {
            const cell = document.createElement('div');
            cell.classList.add('cell');
            cell.classList.add((r + c) % 2 === 0 ? 'light' : 'dark');
            cell.dataset.row = r;
            cell.dataset.col = c;

            // Add selected highlight to the cell
            if (currentGameState.selectedPiece && currentGameState.selectedPiece.row === r && currentGameState.selectedPiece.col === c) {
                cell.classList.add('selected');
            }

            // Add possible move highlight to the cell
            if (currentGameState.possibleMoves.some(move => move.row === r && move.col === c)) {
                cell.classList.add('possible-move');
            }

            // Add piece if present
            if (cellValue !== EMPTY) {
                const piece = document.createElement('div');
                piece.classList.add('piece');
                if (cellValue === PAWN_1 || cellValue === KING_1) {
                    piece.classList.add('player-1');
                } else {
                    piece.classList.add('player-2');
                }
                if (cellValue === KING_1 || cellValue === KING_2) {
                    piece.classList.add('king');
                }
                // Add selected highlight to piece itself for visual effect
                if (currentGameState.selectedPiece && currentGameState.selectedPiece.row === r && currentGameState.selectedPiece.col === c) {
                    piece.classList.add('selected');
                }
                cell.appendChild(piece);
            }

            cell.addEventListener('click', () => handleCellClick(r, c));
            boardElement.appendChild(cell);
        });
    });

    // Update turn display
    turnDisplay.textContent = `Turn: Player ${currentGameState.currentPlayer}`;
    if (currentGameState.gameOver) {
        turnDisplay.textContent = 'Game Over!';
    }

    // Update message display
    messageDisplay.textContent = currentGameState.gameMessage;

    // Disable board interaction if game is over
    if (currentGameState.gameOver) {
        boardElement.style.pointerEvents = 'none';
        resetButton.style.display = 'block'; // Ensure reset button is visible
    } else {
        boardElement.style.pointerEvents = 'auto';
        resetButton.style.display = 'block';
    }
}

// Handle cell clicks (frontend interaction)
function handleCellClick(row, col) {
    if (currentGameState.gameOver) return;

    // If a piece is currently selected in the UI
    if (currentGameState.selectedPiece) {
        // Check if the clicked cell is a possible move for the selected piece
        const isPossibleMove = currentGameState.possibleMoves.some(move => move.row === row && move.col === col);

        if (isPossibleMove) {
            // Attempt to make the move via game context
            gameContext.makeMove(currentGameState.selectedPiece.row, currentGameState.selectedPiece.col, row, col);
            updateUI(); // Always update UI after a potential move
        } else {
            // If clicked on the same piece, try to deselect (context will handle if multi-capture is active)
            if (currentGameState.selectedPiece.row === row && currentGameState.selectedPiece.col === col) {
                gameContext.deselectPiece();
                updateUI();
            } else {
                // If clicked on another cell (either another piece or an empty invalid spot)
                // Try to select the new piece. Context will validate if it's allowed.
                gameContext.selectPiece(row, col);
                updateUI();
            }
        }
    } else {
        // No piece selected, try to select one via game context
        gameContext.selectPiece(row, col);
        updateUI();
    }
}


// Initialize the game (frontend entry point)
function initFrontendGame() {
    gameContext.initGame(); // Initialize backend state via context
    updateUI(); // Render initial UI
}

// Event listener for reset button
resetButton.addEventListener('click', initFrontendGame);

// Initialize the game when the script loads
initFrontendGame();