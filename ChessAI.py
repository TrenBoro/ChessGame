import random

pieceValues = {'K' : 0, 'P' : 1, 'N' : 3, 'B' : 3, 'R' : 5, 'Q' : 9}
CHECKMATE = 10000
DRAW = 0
STALEMATE = 0
DEPTH = 4

knightPositionValues = [[0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0],
                        [0.1, 0.3, 0.5, 0.5, 0.5, 0.5, 0.3, 0.1],
                        [0.2, 0.5, 0.6, 0.65, 0.65, 0.6, 0.5, 0.2],
                        [0.2, 0.55, 0.65, 0.7, 0.7, 0.65, 0.55, 0.2],
                        [0.2, 0.5, 0.65, 0.7, 0.7, 0.65, 0.5, 0.2],
                        [0.2, 0.55, 0.6, 0.65, 0.65, 0.6, 0.55, 0.2],
                        [0.1, 0.3, 0.5, 0.55, 0.55, 0.5, 0.3, 0.1],
                        [0.0, 0.1, 0.2, 0.2, 0.2, 0.2, 0.1, 0.0]]

bishopPositionValues = [[0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0],
                        [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                        [0.2, 0.4, 0.5, 0.6, 0.6, 0.5, 0.4, 0.2],
                        [0.2, 0.5, 0.5, 0.6, 0.6, 0.5, 0.5, 0.2],
                        [0.2, 0.4, 0.6, 0.6, 0.6, 0.6, 0.4, 0.2],
                        [0.2, 0.6, 0.6, 0.6, 0.6, 0.6, 0.6, 0.2],
                        [0.2, 0.5, 0.4, 0.4, 0.4, 0.4, 0.5, 0.2],
                        [0.0, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.0]]

rookPositionValues = [[0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25],
                        [0.5, 0.75, 0.75, 0.75, 0.75, 0.75, 0.75, 0.5],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.0, 0.25, 0.25, 0.25, 0.25, 0.25, 0.25, 0.0],
                        [0.25, 0.25, 0.25, 0.5, 0.5, 0.25, 0.25, 0.25]]

queenPositionValues = [[0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0],
                        [0.2, 0.4, 0.4, 0.4, 0.4, 0.4, 0.4, 0.2],
                        [0.2, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                        [0.3, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                        [0.4, 0.4, 0.5, 0.5, 0.5, 0.5, 0.4, 0.3],
                        [0.2, 0.5, 0.5, 0.5, 0.5, 0.5, 0.4, 0.2],
                        [0.2, 0.4, 0.5, 0.4, 0.4, 0.4, 0.4, 0.2],
                        [0.0, 0.2, 0.2, 0.3, 0.3, 0.2, 0.2, 0.0]]

pawnPositionValues = [[0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8, 0.8],
                        [0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7, 0.7],
                        [0.3, 0.3, 0.4, 0.5, 0.5, 0.4, 0.3, 0.3],
                        [0.25, 0.25, 0.3, 0.45, 0.45, 0.3, 0.25, 0.25],
                        [0.2, 0.2, 0.2, 0.4, 0.4, 0.2, 0.2, 0.2],
                        [0.25, 0.15, 0.1, 0.2, 0.2, 0.1, 0.15, 0.25],
                        [0.25, 0.3, 0.3, 0.0, 0.0, 0.3, 0.3, 0.25],
                        [0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2, 0.2]]

piecePostitionValues = {"wN": knightPositionValues,
                         "bN": knightPositionValues[::-1],
                         "wB": bishopPositionValues,
                         "bB": bishopPositionValues[::-1],
                         "wQ": queenPositionValues,
                         "bQ": queenPositionValues[::-1],
                         "wR": rookPositionValues,
                         "bR": rookPositionValues[::-1],
                         "wP": pawnPositionValues,
                         "bP": pawnPositionValues[::-1]}

'''
Get a random move
'''
def getRandomMove(legalMoves, gs):
    print('RANDOM move by WHITE') if not gs.whiteMove else print('RANDOM move by BLACK')
    return legalMoves[random.randint(0, len(legalMoves)-1)]

'''
Helper function for first call of recursive minmax, also better for arguments
'''
def getBestMove(gs, legalMoves, returnQueue):
    global nextMove
    print('BEST move according to WHITE') if not gs.whiteMove else print('BEST move according to BLACK')
    nextMove = None
    random.shuffle(legalMoves)
    findNegaMaxAlphaBetaMove(gs, legalMoves, DEPTH, -CHECKMATE, CHECKMATE, 1 if gs.whiteMove else -1)
    returnQueue.put(nextMove)

'''
Recursive algorithm for finding best move (Nega Max with Alpha Beta Pruning)
'''
def findNegaMaxAlphaBetaMove(gs, legalMoves, depth, alpha, beta, turnMultiplier):
    global nextMove
    if depth == 0:
        return turnMultiplier * scoreBoard(gs)
    
    maxScore = -CHECKMATE
    for move in legalMoves:
        gs.makeMove(move)
        nextMoves = gs.getLegalMoves()
        score = -findNegaMaxAlphaBetaMove(gs, nextMoves, depth - 1, -beta, -alpha, -turnMultiplier)
        if score > maxScore:
            maxScore = score
            if depth == DEPTH:
                nextMove = move
        gs.undoMove()
        if maxScore > alpha: # Pruning
            alpha = maxScore
        if alpha >= beta:
            break
    return maxScore

'''
A positive score is good for white, a negative score is good for black
'''
def scoreBoard(gs):
    if gs.checkmate:
        if gs.whiteMove:
            return -CHECKMATE # Black wins
        else:
            return CHECKMATE # White wins
    elif gs.stalemate:
        return STALEMATE # No one wins
    elif gs.draw:
        return DRAW

    score = 0
    for row in range(len(gs.board)):
        for col in range(len(gs.board[row])):
            piece = gs.board[row][col]
            if piece != '--':
                pieceScore = 0
                if piece[1] != 'K':
                    pieceScore = piecePostitionValues[piece][row][col]
                if piece[0] == 'w':
                    score += pieceValues[piece[1]] + pieceScore
                elif piece[0] == 'b':
                    score -= pieceValues[piece[1]] + pieceScore
    return score