class SnakeGame {
    constructor(gameBoardId, scoreDisplayId, startButtonId, gameOverlayId, gameMessageId) {
        // Initialize DOM elements
        this.gameBoard = document.getElementById(gameBoardId);
        this.ctx = this.gameBoard.getContext('2d');
        this.scoreDisplay = document.getElementById(scoreDisplayId);
        this.startButton = document.getElementById(startButtonId);
        this.gameOverlay = document.getElementById(gameOverlayId);
        this.gameMessage = document.getElementById(gameMessageId);

        // Game constants
        this.BOARD_SIZE = 20; // 20x20 grid
        this.CELL_SIZE = this.gameBoard.width / this.BOARD_SIZE; // Each cell is 20px for a 400x400 canvas

        // Game state variables
        this.snake = [];
        this.food = {};
        this.direction = 'right';
        this.score = 0;
        this.gameOver = false;
        this.gameInterval = null;
        this.gameSpeed = 150; // Milliseconds per frame
        this.changingDirection = false; // To prevent rapid direction changes

        // Initial setup
        this.initEventListeners();
        this.drawGame(); // Initial draw of an empty board
        this.gameMessage.textContent = 'Presiona "Comenzar Juego"';
        this.startButton.textContent = 'Comenzar Juego';
        this.gameOverlay.classList.remove('hidden');
    }

    initEventListeners() {
        document.addEventListener('keydown', this.handleKeyPress.bind(this));
        this.startButton.addEventListener('click', this.startGame.bind(this));
    }

    startGame() {
        this.snake = [
            { x: 10, y: 10 }, // Initial head position
            { x: 9, y: 10 },
            { x: 8, y: 10 }
        ];
        this.direction = 'right';
        this.score = 0;
        this.scoreDisplay.textContent = this.score;
        this.gameOver = false;
        this.gameSpeed = 150; // Initial speed
        this.changingDirection = false;

        this.generateFood();
        this.drawGame(); // Initial draw with snake and food
        
        // Hide overlay and start button, show game board
        this.gameOverlay.classList.add('hidden');
        
        // Clear any existing interval before starting a new one
        if (this.gameInterval) {
            clearInterval(this.gameInterval);
        }
        this.gameInterval = setInterval(this.gameLoop.bind(this), this.gameSpeed);
    }

    gameLoop() {
        if (this.gameOver) {
            clearInterval(this.gameInterval);
            this.showGameOver();
            return;
        }

        this.changingDirection = false; // Reset for next frame
        this.moveSnake();
        this.drawGame();
    }

    drawGame() {
        // Clear canvas
        this.ctx.clearRect(0, 0, this.gameBoard.width, this.gameBoard.height);
        
        // Draw grid lines (optional, but helps visualize)
        // this.drawGrid();

        // Draw food
        this.drawFood();

        // Draw snake
        this.drawSnake();
    }

    drawGrid() {
        this.ctx.strokeStyle = '#333'; // Darker grid lines
        for (let i = 0; i <= this.BOARD_SIZE; i++) {
            this.ctx.beginPath();
            this.ctx.moveTo(i * this.CELL_SIZE, 0);
            this.ctx.lineTo(i * this.CELL_SIZE, this.gameBoard.height);
            this.ctx.stroke();

            this.ctx.beginPath();
            this.ctx.moveTo(0, i * this.CELL_SIZE);
            this.ctx.lineTo(this.gameBoard.width, i * this.CELL_SIZE);
            this.ctx.stroke();
        }
    }

    drawSnake() {
        this.snake.forEach((segment, index) => {
            this.ctx.fillStyle = (index === 0) ? '#2ecc71' : '#27ae60'; // Head is brighter green
            this.ctx.strokeStyle = '#1a7a44'; // Darker border
            this.ctx.fillRect(segment.x * this.CELL_SIZE, segment.y * this.CELL_SIZE, this.CELL_SIZE, this.CELL_SIZE);
            this.ctx.strokeRect(segment.x * this.CELL_SIZE, segment.y * this.CELL_SIZE, this.CELL_SIZE, this.CELL_SIZE);
        });
    }

    drawFood() {
        this.ctx.fillStyle = '#e74c3c'; // Red food
        this.ctx.strokeStyle = '#c0392b'; // Darker red border
        this.ctx.fillRect(this.food.x * this.CELL_SIZE, this.food.y * this.CELL_SIZE, this.CELL_SIZE, this.CELL_SIZE);
        this.ctx.strokeRect(this.food.x * this.CELL_SIZE, this.food.y * this.CELL_SIZE, this.CELL_SIZE, this.CELL_SIZE);
    }

    moveSnake() {
        const head = { x: this.snake[0].x, y: this.snake[0].y };

        switch (this.direction) {
            case 'up':
                head.y--;
                break;
            case 'down':
                head.y++;
                break;
            case 'left':
                head.x--;
                break;
            case 'right':
                head.x++;
                break;
        }

        // Check for collisions BEFORE adding new head
        if (this.checkCollision(head)) {
            this.gameOver = true;
            return;
        }

        this.snake.unshift(head); // Add new head

        // Check if food was eaten
        if (head.x === this.food.x && head.y === this.food.y) {
            this.score += 10;
            this.scoreDisplay.textContent = this.score;
            this.generateFood();
            // Increase speed slightly
            if (this.gameSpeed > 50) { // Don't go below a certain speed
                this.gameSpeed -= 5;
                clearInterval(this.gameInterval);
                this.gameInterval = setInterval(this.gameLoop.bind(this), this.gameSpeed);
            }
        } else {
            this.snake.pop(); // Remove tail if no food eaten
        }
    }

    checkCollision(head) {
        // Wall collision
        const hitLeftWall = head.x < 0;
        const hitRightWall = head.x >= this.BOARD_SIZE;
        const hitTopWall = head.y < 0;
        const hitBottomWall = head.y >= this.BOARD_SIZE;

        if (hitLeftWall || hitRightWall || hitTopWall || hitBottomWall) {
            return true;
        }

        // Self-collision (check if head collides with any body segment)
        for (let i = 1; i < this.snake.length; i++) {
            if (head.x === this.snake[i].x && head.y === this.snake[i].y) {
                return true;
            }
        }

        return false;
    }

    generateFood() {
        let newFoodPosition;
        let collisionWithSnake;

        do {
            newFoodPosition = {
                x: Math.floor(Math.random() * this.BOARD_SIZE),
                y: Math.floor(Math.random() * this.BOARD_SIZE)
            };
            collisionWithSnake = this.snake.some(segment =>
                segment.x === newFoodPosition.x && segment.y === newFoodPosition.y
            );
        } while (collisionWithSnake); // Keep generating until it's not on the snake

        this.food = newFoodPosition;
    }

    handleKeyPress(event) {
        if (this.changingDirection) return; // Prevent multiple direction changes in one frame
        this.changingDirection = true;

        const keyPressed = event.key;
        const goingUp = this.direction === 'up';
        const goingDown = this.direction === 'down';
        const goingLeft = this.direction === 'left';
        const goingRight = this.direction === 'right';

        // Prevent immediate reverse
        if (keyPressed === 'ArrowUp' && !goingDown) {
            this.direction = 'up';
        } else if (keyPressed === 'ArrowDown' && !goingUp) {
            this.direction = 'down';
        } else if (keyPressed === 'ArrowLeft' && !goingRight) {
            this.direction = 'left';
        } else if (keyPressed === 'ArrowRight' && !goingLeft) {
            this.direction = 'right';
        }
    }

    showGameOver() {
        this.gameMessage.textContent = '¡Juego Terminado!';
        this.startButton.textContent = 'Volver a Jugar';
        this.gameOverlay.classList.remove('hidden');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    new SnakeGame('game-board', 'score', 'start-button', 'game-overlay', 'game-message');
});