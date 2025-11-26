# Implementation Plan

- [x] 1. Set up project structure and core data models


  - Create directory structure: src/models, src/ai, src/ui, src/controllers
  - Implement Board class with 2D array representation and basic stone placement
  - Implement Move dataclass for representing game moves
  - Implement GameState dataclass for tracking game state
  - _Requirements: 5.1, 5.2, 5.4_


- [ ] 2. Implement board logic and Go rules
  - [ ] 2.1 Implement liberty calculation using flood-fill algorithm
    - Write get_liberties() method to count empty adjacent intersections
    - Write get_group() method to find connected stones of same color

    - Handle edge cases for corner and edge positions
    - _Requirements: 2.1, 2.2_
  - [ ] 2.2 Implement capture detection and removal
    - Write find_captured_stones() to identify groups with zero liberties

    - Write remove_stones() to remove captured stones from board
    - Update captured stone counters
    - _Requirements: 2.1, 2.5_
  - [x] 2.3 Implement move validation logic

    - Write is_valid_move() to check if position is empty
    - Implement self-capture prevention (reject moves that result in self-capture without capturing opponent)
    - Implement Ko rule using board state hashing
    - _Requirements: 2.2, 2.3_
  - [ ] 2.4 Implement board cloning for AI simulation
    - Write clone() method for deep copying board state
    - Write get_empty_positions() for move generation
    - _Requirements: 3.2_
  - [ ]* 2.5 Write unit tests for board logic
    - Test liberty calculation on various board configurations
    - Test capture detection for single stones and groups


    - Test Ko rule enforcement
    - Test self-capture prevention
    - _Requirements: 2.1, 2.2, 2.3_


- [ ] 3. Implement game controller
  - [ ] 3.1 Create GameController class with game state management
    - Initialize board, players, and game state

    - Implement start_game() to reset game state
    - Track current player, move history, and captured stones
    - _Requirements: 5.1, 5.2_
  - [ ] 3.2 Implement turn management and move execution
    - Write make_move() to validate and execute player moves
    - Implement automatic turn alternation after valid moves
    - Handle stone placement and capture processing
    - _Requirements: 1.3, 2.5_
  - [ ] 3.3 Implement game end conditions and scoring
    - Write pass_turn() and track consecutive passes
    - Write resign() to end game immediately
    - Implement calculate_score() using territory counting


    - Write is_game_over() to detect end conditions
    - _Requirements: 2.4_

  - [ ]* 3.4 Write unit tests for game controller
    - Test turn alternation
    - Test game end detection
    - Test score calculation

    - _Requirements: 2.4, 2.5_

- [ ] 4. Implement heuristic evaluator for AI
  - [x] 4.1 Create HeuristicEvaluator class structure

    - Implement evaluate() method as main entry point
    - Define weight constants for each heuristic component
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_
  - [x] 4.2 Implement territory evaluation

    - Write evaluate_territory() using influence mapping
    - Count empty intersections closer to player's stones
    - Use distance-based influence calculation
    - _Requirements: 6.1_
  - [ ] 4.3 Implement group strength evaluation
    - Write evaluate_groups() to assess group health
    - Calculate (liberties × group_size) for each group
    - Sum values for all player's groups
    - _Requirements: 6.2_
  - [ ] 4.4 Implement capture evaluation
    - Write evaluate_captures() to count captured stones


    - Identify potential captures (opponent groups with 1 liberty)
    - Calculate difference between player and opponent captures
    - _Requirements: 6.3_

  - [ ] 4.5 Implement strategic position evaluation
    - Write evaluate_strategic_positions() for positional bonuses
    - Assign values: corners (3), edges (2), center (1)
    - Apply bonuses only in early game (>60 empty positions)

    - _Requirements: 6.4_
  - [ ]* 4.6 Write unit tests for heuristic evaluator
    - Test each heuristic component independently
    - Verify heuristic values on known board positions

    - Test weight balancing
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 5. Implement Minimax AI algorithm
  - [ ] 5.1 Create MinimaxAI class with alpha-beta pruning
    - Implement minimax() recursive method with alpha-beta parameters
    - Implement maximizing and minimizing player logic
    - Return heuristic evaluation at leaf nodes
    - _Requirements: 3.2, 3.3_
  - [ ] 5.2 Implement move generation and ordering
    - Write get_possible_moves() to generate valid moves
    - Implement move filtering (adjacent to existing stones after opening)
    - Order moves by priority (captures, threats, strategic positions)


    - _Requirements: 3.2_
  - [x] 5.3 Implement adaptive depth limit selection

    - Write method to count empty positions on board
    - Set depth=2 for >60 empty, depth=3 for 30-60 empty, depth=4 for <30 empty
    - Allow manual depth override for testing

    - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5_
  - [ ] 5.4 Implement find_best_move() as main AI interface
    - Iterate through all possible moves
    - Call minimax() for each move with initial alpha-beta values
    - Return move with highest evaluation score
    - Add timeout mechanism (5 seconds maximum)


    - _Requirements: 3.2, 3.4_
  - [ ]* 5.5 Write unit tests for Minimax algorithm
    - Test alpha-beta pruning correctness

    - Test depth limiting
    - Verify best move selection on simple positions
    - Test timeout handling
    - _Requirements: 3.2, 3.4_


- [ ] 6. Implement player classes
  - [ ] 6.1 Create abstract Player base class
    - Define abstract get_move() method
    - Store player color attribute
    - _Requirements: 5.3_

  - [ ] 6.2 Implement HumanPlayer class
    - Implement get_move() to return move from UI input queue
    - Handle waiting for user input
    - _Requirements: 1.2, 5.3_
  - [ ] 6.3 Implement AIPlayer class
    - Integrate MinimaxAI into AIPlayer

    - Implement get_move() to call AI algorithm
    - Pass board state to AI for move calculation
    - _Requirements: 3.1, 3.2, 5.3_

- [x] 7. Implement user interface with Pygame

  - [ ] 7.1 Create GameUI class and Pygame window
    - Initialize Pygame and create display surface (800x600 pixels)
    - Set up game clock for frame rate control (60 FPS)
    - Create board surface (600x600) and info panel surface (200x600)
    - _Requirements: 1.1, 4.1_
  - [ ] 7.2 Implement board and grid rendering
    - Write draw_grid() to render 9x9 grid lines using pygame.draw.line()

    - Calculate intersection positions with proper spacing
    - Draw star points (handicap positions) as small filled circles
    - Use wood texture or tan color for board background
    - _Requirements: 1.1_
  - [ ] 7.3 Implement stone rendering
    - Write draw_stone() to render black and white stones using pygame.draw.circle()
    - Position stones at intersection points
    - Add subtle shadows using semi-transparent circles
    - Use anti-aliasing for smooth stone edges
    - _Requirements: 1.2_
  - [ ] 7.4 Implement mouse interaction with Pygame events
    - Write handle_click() in main game loop to process MOUSEBUTTONDOWN events
    - Convert pixel coordinates to board coordinates
    - Implement hover effect using MOUSEMOTION events to preview stone placement
    - Highlight valid move positions on hover with semi-transparent stone
    - Call controller.make_move() on valid clicks
    - _Requirements: 1.2, 1.4, 4.3_
  - [ ] 7.5 Implement game information display
    - Write show_turn_indicator() to render current player text and colored circle
    - Write show_captured_count() to display captured stones count
    - Use pygame.font to render text in info panel
    - Add visual distinction between black and white turn indicators
    - _Requirements: 4.1, 4.2_
  - [ ] 7.6 Implement game controls with clickable buttons
    - Create Button class for Pygame UI elements
    - Add "New Game" button to restart
    - Add "Pass" button to skip turn
    - Add "Resign" button to end game
    - Add mode selection buttons (Human vs Human / Human vs AI)
    - Handle button clicks in event loop
    - _Requirements: 4.4_
  - [ ] 7.7 Implement game over overlay
    - Write show_game_over() to render semi-transparent overlay
    - Display final scores and winner announcement
    - Show "New Game" button on overlay
    - Handle overlay click events
    - _Requirements: 4.5_

- [ ] 8. Integrate all components and wire together
  - [x] 8.1 Create main application entry point


    - Write main.py to initialize Pygame, GameController, and GameUI
    - Set up player instances based on selected mode
    - Create main game loop with event handling
    - _Requirements: 5.1, 5.5_
  - [x] 8.2 Implement Pygame game loop coordination

    - Process Pygame events (QUIT, MOUSEBUTTONDOWN, MOUSEMOTION)
    - Handle human player moves through mouse clicks
    - Trigger AI move calculation on AI player's turn (run in separate thread to avoid blocking)
    - Update and render UI at 60 FPS using clock.tick()
    - Process captures and update display
    - _Requirements: 1.3, 3.2_

  - [ ] 8.3 Add error handling and edge cases
    - Handle invalid move attempts with user feedback
    - Implement timeout for AI moves (fallback to random move)
    - Add exception handling for UI rendering errors
    - _Requirements: 1.4_
  - [ ]* 8.4 Perform integration testing
    - Test complete human vs human game flow
    - Test complete human vs AI game flow
    - Test game end scenarios (pass, resign, scoring)
    - Verify UI responsiveness and feedback
    - _Requirements: 1.1, 1.2, 1.3, 3.1, 3.2, 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 9. Optimize performance and polish
  - [x] 9.1 Optimize AI performance


    - Implement transposition table for position caching
    - Add move ordering optimization (evaluate promising moves first)
    - Profile AI execution time and optimize bottlenecks
    - _Requirements: 3.2, 3.4_



  - [ ] 9.2 Enhance UI visual polish
    - Add smooth animations for stone placement
    - Add visual feedback for captured stones (fade out animation)
    - Improve color scheme and visual aesthetics
    - Add last move indicator (small marker on last played stone)

    - _Requirements: 4.1, 4.3_
  - [ ] 9.3 Add code documentation
    - Write docstrings for all classes and public methods
    - Add inline comments for complex algorithms
    - Create README with setup and usage instructions
    - _Requirements: 5.1, 5.2_
