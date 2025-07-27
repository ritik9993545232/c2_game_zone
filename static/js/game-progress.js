/**
 * Game Progress Utility for C2 Game Zone
 * This file provides functions for games to save and load their progress
 */

class GameProgressManager {
    constructor(gameName) {
        this.gameName = gameName;
        this.progressKey = `game_progress_${gameName}`;
        this.currentProgress = this.loadLocalProgress();
    }

    // Load progress from localStorage
    loadLocalProgress() {
        try {
            const stored = localStorage.getItem(this.progressKey);
            return stored ? JSON.parse(stored) : {
                score: 0,
                level: 1,
                lives: 3,
                game_state: {},
                progress_data: {}
            };
        } catch (error) {
            console.error('Error loading local progress:', error);
            return {
                score: 0,
                level: 1,
                lives: 3,
                game_state: {},
                progress_data: {}
            };
        }
    }

    // Save progress to server
    async saveProgress(progressData = {}) {
        const data = {
            game_name: this.gameName,
            score: progressData.score || this.currentProgress.score || 0,
            level: progressData.level || this.currentProgress.level || 1,
            lives: progressData.lives || this.currentProgress.lives || 3,
            game_state: JSON.stringify(progressData.game_state || this.currentProgress.game_state || {}),
            progress_data: JSON.stringify(progressData.progress_data || this.currentProgress.progress_data || {})
        };

        try {
            const response = await fetch('/save_progress', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();
            
            if (result.success) {
                // Update local progress
                this.currentProgress = {
                    score: data.score,
                    level: data.level,
                    lives: data.lives,
                    game_state: progressData.game_state || this.currentProgress.game_state,
                    progress_data: progressData.progress_data || this.currentProgress.progress_data
                };
                
                // Save to localStorage
                localStorage.setItem(this.progressKey, JSON.stringify(this.currentProgress));
                
                console.log(`Progress saved for ${this.gameName}:`, data);
                return true;
            } else {
                console.error('Failed to save progress:', result.error);
                return false;
            }
        } catch (error) {
            console.error('Error saving progress:', error);
            return false;
        }
    }

    // Load progress from server
    async loadProgress() {
        try {
            const response = await fetch(`/get_progress/${this.gameName}`);
            const data = await response.json();
            
            if (data.success) {
                this.currentProgress = {
                    score: data.score || 0,
                    level: data.level || 1,
                    lives: data.lives || 3,
                    game_state: data.game_state ? JSON.parse(data.game_state) : {},
                    progress_data: data.progress_data ? JSON.parse(data.progress_data) : {}
                };
                
                // Save to localStorage
                localStorage.setItem(this.progressKey, JSON.stringify(this.currentProgress));
                
                console.log(`Progress loaded for ${this.gameName}:`, this.currentProgress);
                return this.currentProgress;
            } else {
                console.log('No progress found for', this.gameName);
                return this.currentProgress;
            }
        } catch (error) {
            console.error('Error loading progress:', error);
            return this.currentProgress;
        }
    }

    // Get current progress
    getProgress() {
        return this.currentProgress;
    }

    // Update score
    updateScore(newScore) {
        this.currentProgress.score = newScore;
        this.saveProgress();
    }

    // Update level
    updateLevel(newLevel) {
        this.currentProgress.level = newLevel;
        this.saveProgress();
    }

    // Update lives
    updateLives(newLives) {
        this.currentProgress.lives = newLives;
        this.saveProgress();
    }

    // Update game state
    updateGameState(newState) {
        this.currentProgress.game_state = newState;
        this.saveProgress();
    }

    // Auto-save progress (useful for games that need frequent saves)
    startAutoSave(intervalMs = 30000) { // Default: save every 30 seconds
        this.autoSaveInterval = setInterval(() => {
            this.saveProgress();
        }, intervalMs);
    }

    // Stop auto-save
    stopAutoSave() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
            this.autoSaveInterval = null;
        }
    }

    // Save progress on page unload
    enableUnloadSave() {
        window.addEventListener('beforeunload', () => {
            this.saveProgress();
        });
    }
}

// Global function to create a progress manager for any game
function createGameProgressManager(gameName) {
    return new GameProgressManager(gameName);
}

// Example usage for games:
/*
// In your game's JavaScript file:
const progressManager = createGameProgressManager('Snake');

// Load progress when game starts
progressManager.loadProgress().then(progress => {
    // Initialize game with saved progress
    game.score = progress.score;
    game.level = progress.level;
    game.lives = progress.lives;
    // ... initialize other game state
});

// Save progress when score changes
function updateScore(newScore) {
    game.score = newScore;
    progressManager.updateScore(newScore);
}

// Save progress when level changes
function updateLevel(newLevel) {
    game.level = newLevel;
    progressManager.updateLevel(newLevel);
}

// Save complex game state
function saveGameState() {
    const gameState = {
        snakePosition: snake.body,
        foodPosition: food.position,
        direction: snake.direction,
        // ... other game state
    };
    progressManager.updateGameState(gameState);
}

// Enable auto-save
progressManager.startAutoSave(60000); // Save every minute

// Save on page unload
progressManager.enableUnloadSave();
*/ 