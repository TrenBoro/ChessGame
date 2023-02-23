# User input and current game state
import ChessEngine, ChessAI
import pygame as pg
import sys
from multiprocessing import Queue, Process

# Global variables
DIMENSION = 8 # Board is 8x8
BOARD_WIDTH = BOARD_HEIGHT = 800 # Screen size
LOG_SCREEN_WIDTH = 300
LOG_SCREEN_HEIGHT = BOARD_HEIGHT
SQ_SIZE = BOARD_WIDTH // DIMENSION
MAX_FPS = 144
IMAGES = {}
BLACK = (0, 0, 0)

def main():
    pg.init() # Initialize pygame
    screen = pg.display.set_mode((BOARD_WIDTH + LOG_SCREEN_WIDTH, BOARD_HEIGHT)) # Set screen size
    clock = pg.time.Clock() # Enable time in game
    screen.fill(pg.Color("white")) # Fill screen with background color
    moveLogFont = pg.font.SysFont('Arial', 16, False, False)
    pg.display.set_caption('Chess')

    gs = ChessEngine.GameState() # This is where we initialze the game state
    loadImages() # Load images in only once before the main loop

    legalMoves = gs.getLegalMoves() # List of legal moves
    moveMade = False # Flag for move made
    animate = False # Flag for when the animation should run
    selectedSquare = () # Currently selected square
    clicks = [] # All clicks made by the player
    gameOver = False
    playerOne = True # If a human is playing white, then this is true. If an AI is playing white, then it's false
    playerTwo = False # Same as above, but for black
    AIThinking = False
    moveFinderProcess = None

    while True:
        # If it's white's move and playerOne is true, then playerOne is a human. Same for black's move
        humanTurn = (gs.whiteMove and playerOne) or (not gs.whiteMove and playerTwo)

        # Quit game
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # Mouse handler
            elif event.type == pg.MOUSEBUTTONDOWN:
                if not gameOver: # If it's not game over and it's the human's turn, the player can use click events
                    location = pg.mouse.get_pos() # (x, y) location of mouse pointer
                    col = location[0] // SQ_SIZE
                    row = location[1] // SQ_SIZE # Divided by square size because we're measuring square spaces
                    if selectedSquare == (row, col) or col >= 8: # Is the same square selected?
                        selectedSquare = () # Deselect
                        clicks = [] # Reset player clicks
                    else:
                        selectedSquare = (row, col) # Get the selected square location
                        clicks.append(selectedSquare) # Append it to the moves list
                        
                    if len(clicks) == 2 and humanTurn: # Move the piece after the second click
                        move = ChessEngine.Move(clicks[0], clicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(legalMoves)):
                            if move == legalMoves[i]:
                                gs.makeMove(legalMoves[i], humanTurn) # Make a move after 2nd click
                                moveMade = True
                                animate = True
                                selectedSquare = () # After 2nd click, deselect
                                clicks = [] # After 2nd click, end turn, 0 moves
                        if not moveMade:
                            clicks = [selectedSquare]
            
            # Key handler
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_z: # Undo a move
                    gs.undoMove()
                    moveMade = True
                    animate = False
                    gameOver = False
                if event.key == pg.K_r: # Reset game
                    gs = ChessEngine.GameState()
                    legalMoves = gs.getLegalMoves()
                    selectedSquare = ()
                    clicks = []
                    moveMade = False
                    animate = False
                    gameOver = False
        
        # AI move finder
        if not gameOver and not humanTurn:
            if not AIThinking:
                AIThinking = True
                print('Thinking...')
                retrunQueue = Queue()
                moveFinderProcess = Process(target=ChessAI.getBestMove, args=(gs, legalMoves, retrunQueue))
                moveFinderProcess.start()

            if not moveFinderProcess.is_alive():
                print("Done thinking")
                AIMove = retrunQueue.get()
                if AIMove is None:
                    AIMove = ChessAI.getRandomMove(legalMoves, gs)
                gs.makeMove(AIMove)
                moveMade = True
                animate = True
                AIThinking = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            moveMade = False
            animate = False
            legalMoves = gs.getLegalMoves()

        # These need to be in the loop to generate the display, tick and game state so the game can run
        drawGameState(screen, gs, legalMoves, selectedSquare, moveLogFont)

        if gs.checkmate or gs.stalemate:
            gameOver = True
            drawGameOverText(screen, 'Stalemate' if gs.stalemate else 'White wins by checkmate' if not gs.whiteMove else 'Black wins by checkmate')
        if gs.draw:
            gameOver = True
            drawGameOverText(screen, 'Draw')

        clock.tick(MAX_FPS)
        pg.display.flip()

def loadImages():
    pieces = ["bP", "bR", "bN", "bB", "bQ", "bK", "wP", "wR", "wN", "wB", "wQ", "wK"]
    for piece in pieces:
        # Load chest pieces into IMAGES by transforming their size into 8x8
        IMAGES[piece] = pg.transform.scale(pg.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))

def highlightMoves(screen, gs, legalMoves, selectedSquare):
    if selectedSquare != (): # If the selected square is not empty
        r, c = selectedSquare
        if gs.board[r][c][0] == ('w' if gs.whiteMove else 'b'): # Selected square is a piece that can be moved
            # Highlight selected square
            s = pg.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100) # Transparency. 0 means fully transparent. 255 not transparent at all
            s.fill(pg.Color('blue'))
            screen.blit(s, (SQ_SIZE*c, SQ_SIZE*r))
            # Highlight valid moves
            s.fill(pg.Color('yellow'))
            for move in legalMoves:
                if move.startRow == r and move.startCol == c:
                    screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE))

def drawGameState(screen, gs, legalMoves, selectedSquare, moveLogFont):
    drawBoard(screen)
    highlightMoves(screen, gs, legalMoves, selectedSquare)
    drawPieces(screen, gs.board)
    drawMoveLog(screen, gs, moveLogFont)

def drawBoard(screen):
    global colors
    colors = [pg.Color("white"), pg.Color("gray")]
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            color = colors[((col + row) % 2)] # Odd sum means white tile, even sum means gray tile
            pg.draw.rect(screen, color, pg.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))            

def drawPieces(screen, board):
    for row in range(DIMENSION):
        for col in range(DIMENSION):
            piece = board[row][col]
            if piece != '--':
                screen.blit(IMAGES[piece], pg.Rect(col*SQ_SIZE, row*SQ_SIZE, SQ_SIZE, SQ_SIZE))

def animateMove(move, screen, board, clock):
    global colors
    dR = move.endRow - move.startRow # Change in row
    dC = move.endCol - move.startCol # Change in column
    framesPerSquare = 10 # How many frames will it take for the piece to move one square
    framesCount = (abs(dR) + abs(dC)) * framesPerSquare # How many frames will the animation be -> squares to move times framesPerSquare
    for frame in range(framesCount + 1):
        '''
        Save the coordinates in r, c.
        If frame is 0, the starting position is saved.
        If frame is 1 and i.e. the player is moving a knight. The piece has to move 3 squares or 3 * framesPerSquare frames.
        So, 1/30 of the coordinates is saved. Then, 2/30 of the coordinates, then 3/30 and so on until 30/30 when the piece gets to it's ending location
        '''
        r, c = (move.startRow + dR*frame/framesCount, move.startCol + dC*frame/framesCount)
        drawBoard(screen)
        drawPieces(screen, board) # Drawing the board and pieces of the ending position
        
        # Erase the piece moved from its ending square
        color = colors[((move.endRow + move.endCol) % 2)]
        endSquare = pg.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        pg.draw.rect(screen, color, endSquare) # Draw over the piece at the ending position

        # Draw captured piece onto rectangle
        if move.pieceCaptured != '--':
            if move.isEnpassantMove:
                enPassantRow = move.endRow + 1 if move.pieceCaptured[0] == 'b' else move.endRow - 1
                endSquare = pg.Rect(move.endCol*SQ_SIZE, enPassantRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        
        # Draw moving piece
        screen.blit(IMAGES[move.pieceMoved], pg.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        pg.display.flip()
        clock.tick(MAX_FPS)

def drawGameOverText(screen, text):
    font = pg.font.SysFont('Helvetica', 32, True, False)
    textObject = font.render(text, 0, pg.Color('Gray'))
    textLocation = pg.Rect(0, 0, BOARD_WIDTH, BOARD_HEIGHT).move(BOARD_WIDTH/2 - textObject.get_width()/2 , BOARD_HEIGHT/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)
    textObject = font.render(text, 0, pg.Color('Black'))
    screen.blit(textObject, textLocation.move(2, 2))

def drawMoveLog(screen, gs, font):
    moveLogRect = pg.Rect(BOARD_WIDTH, 0, LOG_SCREEN_WIDTH, LOG_SCREEN_HEIGHT)
    pg.draw.rect(screen, pg.Color('Black'), moveLogRect)
    moveLog = gs.moveLog
    moveText = []
    for i in range(0, len(moveLog), 2):
        moveString = str(i//2 + 1) + '. ' + str(moveLog[i]) + ' '
        if i+1 < len(moveLog):
            moveString += str(moveLog[i+1]) + '    '
        moveText.append(moveString)
    
    movesPerRow = 3
    padding = 15
    lineSpacing = 2
    textY = padding
    for i in range(0, len(moveText), movesPerRow):
        text = ''
        for j in range(movesPerRow):
            if i+j < len(moveText):
                text += moveText[i+j]
        textObject = font.render(text, 0, pg.Color('White'))
        textLocation = moveLogRect.move(padding, textY)
        screen.blit(textObject, textLocation)
        textY += textObject.get_height() + lineSpacing


if __name__ == "__main__":
    main()
