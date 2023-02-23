# Game info, valid moves, moves log

class GameState():
    def __init__(self):
        """
        Board is 8x8 2D list of strings
        First character represents color
        Second character represents piece
        Double dash represents empty space
        """
        self.board = [
                    ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["--", "--", "--", "--", "--", "--", "--", "--"],
                    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
                    ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]

        self.whiteMove = True
        self.moveLog = []
        self.whiteKingLoc = (7, 4)
        self.blackKingLoc = (0, 4)
        self.check = False
        self.checks = []
        self.pins = []
        self.checkmate = False
        self.draw = False
        self.stalemate = False
        self.enPassantPossible = () # Coordinates or square where en passant is applied
        self.enPassantPossibleLog = [self.enPassantPossible]
        self.promotePiece = 'Q' # Set as default for AI
        self.moveCountWhite = 0
        self.moveCountBlack = 0
        
        # Castling
        self.currentCastleRights = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                               self.currentCastleRights.wqs, self.currentCastleRights.bqs)]
        
        self.moveFunctions = {'P' : self.getPawnMoves, 'R' : self.getRookMoves, 'N' : self.getKnightMoves,
                                'B' : self.getBishopMoves, 'Q' : self.getQueenMoves, 'K' : self.getKingMoves}

    '''
    Make a move
    '''
    def makeMove(self, move, human=False):
        self.board[move.startRow][move.startCol] = '--' # When a piece is moved an empty space is left on its location
        self.board[move.endRow][move.endCol] = move.pieceMoved # The starting row and col of the moved piece are saved at the end location
        self.moveLog.append(move) # Save move in move log so we can undo it later

        self.whiteMove = not self.whiteMove

        # Update king's location
        if move.pieceMoved == 'wK':
            self.whiteKingLoc = (move.endRow, move.endCol)
        elif move.pieceMoved == 'bK':
            self.blackKingLoc = (move.endRow, move.endCol)
        
        # Pawn promotion
        if move.isPromotion:
            if human:
                self.promotePiece = input("Promote to [Q]ueen, [R]ook, [B]ishop or K[n]ight: ").upper()
                if self.promotePiece.upper() not in move.allowedPromotions:
                    print("You can't promote a pawn to that\n")
                    while self.promotePiece.upper() not in move.allowedPromotions:
                        self.promotePiece = input("Promote to [Q]ueen, [R]ook, [B]ishop or K[n]ight: ").upper()
                        if self.promotePiece.upper() not in move.allowedPromotions:
                            print("You can't promote a pawn to that\n")
                        else:
                            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + self.promotePiece.upper()
                            break
                else:
                    self.board[move.endRow][move.endCol] = move.pieceMoved[0] + self.promotePiece.upper()
            else:
                self.board[move.endRow][move.endCol] = move.pieceMoved[0] + self.promotePiece.upper()
        
        # En passant
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = '--' # Capturing piece with en passant
        if move.pieceMoved[1] == 'P' and abs(move.startRow - move.endRow) == 2: # If a pawn moves 2 squares
            self.enPassantPossible = ((move.startRow + move.endRow)//2, move.startCol) # En passant square is one row before final advance in the same column
        else:
            self.enPassantPossible = () # Reset if any other move is made
        
        # Castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2: # Kingside castle move
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] # Copy Rook to left of king
                self.board[move.endRow][move.endCol+1] = '--' # Remove right Rook from original position
            else: # Queenside castle move
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] # Copy Rook to right of king
                self.board[move.endRow][move.endCol-2] = '--' # Remove left Rook from original position
        
        self.enPassantPossibleLog.append(self.enPassantPossible)

        # Update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                            self.currentCastleRights.wqs, self.currentCastleRights.bqs))
        
        # Update move count for draw
        if not move.isCapture and not self.whiteMove:
            self.moveCountWhite += 1
        elif not move.isCapture and self.whiteMove:
            self.moveCountBlack += 1
        elif move.isCapture and not self.whiteMove:
            self.moveCountWhite = 0
        elif move.isCapture and self.whiteMove:
            self.moveCountBlack = 0
    
    '''
    Undo a move
    '''
    def undoMove(self):
        if len(self.moveLog) != 0:
            move = self.moveLog.pop() # Remove and save the last made move
            self.board[move.startRow][move.startCol] = move.pieceMoved # Put piece in its previous position
            self.board[move.endRow][move.endCol] = move.pieceCaptured # Put back captured piece if there is one
            self.whiteMove = not self.whiteMove
            
            # Update king's location
            if move.pieceMoved == 'wK':
                self.whiteKingLoc = (move.startRow, move.startCol)
            elif move.pieceMoved == 'bK':
                self.blackKingLoc = (move.startRow, move.startCol)
            
            # Undo enpassant
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enPassantPossibleLog.pop()
            self.enPassantPossible = self.enPassantPossibleLog[-1]

            # Undo castle rights
            self.castleRightsLog.pop() # Get rid of the new castle rights
            self.currentCastleRights = self.castleRightsLog[-1] # Set the current castle rights as the last logged rights

            # Undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2: # Kingside
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1] # Return right rook to original position
                    self.board[move.endRow][move.endCol-1] = '--' # Clear square left of king
                else: # Queenside
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1] # Return left rook to original position
                    self.board[move.endRow][move.endCol+1] = '--' # Clear square right of king
            
            self.checkmate = False
            self.draw = False
            self.stalemate = False
            self.moveCountWhite -= 1
            self.moveCountBlack -= 1
    
    def squareUnderAttack(self, r, c):
        self.whiteMove = not self.whiteMove # Switch moves
        oppMoves = self.getAllMoves()
        self.whiteMove = not self.whiteMove # Switch moves back
        for move in oppMoves:
            if move.endRow == r and move.endCol == c:
                return True
        return False

    def inCheck(self):
        if self.whiteMove:
            return self.squareUnderAttack(self.whiteKingLoc[0], self.whiteKingLoc[1])
        else:
            return self.squareUnderAttack(self.blackKingLoc[0], self.blackKingLoc[1])
    
    def updateCastleRights(self, move):
        if move.pieceMoved == 'wK':
            self.currentCastleRights.wks = False
            self.currentCastleRights.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastleRights.bks = False
            self.currentCastleRights.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0: # Left Rook
                    self.currentCastleRights.wqs = False
                elif move.startCol == 7: # Right Rook
                    self.currentCastleRights.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0: # Left Rook
                    self.currentCastleRights.bqs = False
                elif move.startCol == 7: # Right Rook
                    self.currentCastleRights.bks = False
        
        if move.pieceCaptured == "wR":
            if move.endCol == 0:  # left rook
                self.currentCastleRights.wqs = False
            elif move.endCol == 7:  # right rook
                self.currentCastleRights.wks = False
        elif move.pieceCaptured == "bR":
            if move.endCol == 0:  # left rook
                self.currentCastleRights.bqs = False
            elif move.endCol == 7:  # right rook
                self.currentCastleRights.bks = False
    
    def getCastleMoves(self, r, c, moves):
        inCheck = self.squareUnderAttack(r, c)
        if inCheck:
            return # Can't castle while in check
        if (self.whiteMove and self.currentCastleRights.wks) or (not self.whiteMove and self.currentCastleRights.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteMove and self.currentCastleRights.wqs) or (not self.whiteMove and self.currentCastleRights.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r, c), (r, c+2), self.board, isCastleMove=True))
    
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r, c), (r, c-2), self.board, isCastleMove=True))
    
    '''
    Get all legal moves
    '''
    def getLegalMoves(self):
        tempCastleRights = CastleRights(self.currentCastleRights.wks, self.currentCastleRights.bks,
                                            self.currentCastleRights.wqs, self.currentCastleRights.bqs)

        # Advanced algorithm
        moves = []
        self.in_check, self.pins, self.checks = self.pinsAndChecks()

        if self.whiteMove:
            kingRow = self.whiteKingLoc[0]
            kingCol = self.whiteKingLoc[1]
        else:
            kingRow = self.blackKingLoc[0]
            kingCol = self.blackKingLoc[1]
        if self.in_check:
            if len(self.checks) == 1:  # only 1 check, block the check or move the king
                moves = self.getAllMoves()
                # to block the check you must put a piece into one of the squares between the enemy piece and your king
                check = self.checks[0]  # check information
                checkRow = check[0]
                checkCol = check[1]
                piece_checking = self.board[checkRow][checkCol]
                valid_squares = []  # squares that pieces can move to
                # if knight, must capture the knight or move your king, other pieces can be blocked
                if piece_checking[1] == "N":
                    valid_squares = [(checkRow, checkCol)]
                else:
                    for i in range(1, 8):
                        valid_square = (kingRow + check[2] * i,
                                        kingCol + check[3] * i)  # check[2] and check[3] are the check directions
                        valid_squares.append(valid_square)
                        if valid_square[0] == checkRow and valid_square[1] == checkCol:  # once you get to piece and check
                            break
                # get rid of any moves that don't block check or move king
                for i in range(len(moves) - 1, -1, -1):  # iterate through the list backwards when removing elements
                    if moves[i].pieceMoved[1] != "K":  # move doesn't move king so it must block or capture
                        if not (moves[i].endRow, moves[i].endCol) in valid_squares:  # move doesn't block or capture piece
                            moves.remove(moves[i])
            else:  # double check, king has to move
                self.getKingMoves(kingRow, kingCol, moves)
        else:  # not in check - all moves are fine
            moves = self.getAllMoves()
            if self.whiteMove:
                self.getCastleMoves(self.whiteKingLoc[0], self.whiteKingLoc[1], moves)
            else:
                self.getCastleMoves(self.blackKingLoc[0], self.blackKingLoc[1], moves)

        # Checkmate and stalemate
        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else:
                self.stalemate = True
        else:
            self.checkmate = False
            self.stalemate = False
        
        # Draw by 3 consecutive moves
        if len(self.moveLog) >= 8:
            for i in range(len(self.moveLog) - 8):
                if self.moveLog[i] == self.moveLog[i+4] == self.moveLog[i+8]:
                    self.draw = True
                    break
        
        # Draw by 50 moves
        if self.moveCountWhite == 50 or self.moveCountBlack == 50:
            self.draw = True
        
        self.currentCastleRights = tempCastleRights
        return moves

    '''
    Get all possible moves
    '''
    def getAllMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                pieceColor = self.board[r][c][0]
                if (pieceColor == 'w' and self.whiteMove) or (pieceColor == 'b' and not self.whiteMove):
                    pieceType = self.board[r][c][1]
                    self.moveFunctions[pieceType](r, c, moves) # A very elegant way of calling all the move functions
        return moves
    
    '''
    Get all possible moves for a pawn located at (r, c) location
    ''' 
    def getPawnMoves(self, row, col, moves):
        piece_pinned = False
        pin_direction = ()
        for i in range(len(self.pins) - 1, -1, -1):
            if self.pins[i][0] == row and self.pins[i][1] == col:
                piece_pinned = True
                pin_direction = (self.pins[i][2], self.pins[i][3])
                self.pins.remove(self.pins[i])
                break

        if self.whiteMove:
            move_amount = -1
            start_row = 6
            enemy_color = "b"
            king_row, king_col = self.whiteKingLoc
        else:
            move_amount = 1
            start_row = 1
            enemy_color = "w"
            king_row, king_col = self.blackKingLoc

        if self.board[row + move_amount][col] == "--":  # 1 square pawn advance
            if not piece_pinned or pin_direction == (move_amount, 0):
                moves.append(Move((row, col), (row + move_amount, col), self.board))
                if row == start_row and self.board[row + 2 * move_amount][col] == "--":  # 2 square pawn advance
                    moves.append(Move((row, col), (row + 2 * move_amount, col), self.board))
        if col - 1 >= 0:  # capture to the left
            if not piece_pinned or pin_direction == (move_amount, -1):
                if self.board[row + move_amount][col - 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col - 1), self.board))
                if (row + move_amount, col - 1) == self.enPassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col - 1)
                            outside_range = range(col + 1, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col, -1)
                            outside_range = range(col - 2, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col - 1), self.board, isEnpassantMove=True))
        if col + 1 <= 7:  # capture to the right
            if not piece_pinned or pin_direction == (move_amount, +1):
                if self.board[row + move_amount][col + 1][0] == enemy_color:
                    moves.append(Move((row, col), (row + move_amount, col + 1), self.board))
                if (row + move_amount, col + 1) == self.enPassantPossible:
                    attacking_piece = blocking_piece = False
                    if king_row == row:
                        if king_col < col:  # king is left of the pawn
                            # inside: between king and the pawn;
                            # outside: between pawn and border;
                            inside_range = range(king_col + 1, col)
                            outside_range = range(col + 2, 8)
                        else:  # king right of the pawn
                            inside_range = range(king_col - 1, col + 1, -1)
                            outside_range = range(col - 1, -1, -1)
                        for i in inside_range:
                            if self.board[row][i] != "--":  # some piece beside en-passant pawn blocks
                                blocking_piece = True
                        for i in outside_range:
                            square = self.board[row][i]
                            if square[0] == enemy_color and (square[1] == "R" or square[1] == "Q"):
                                attacking_piece = True
                            elif square != "--":
                                blocking_piece = True
                    if not attacking_piece or blocking_piece:
                        moves.append(Move((row, col), (row + move_amount, col + 1), self.board, isEnpassantMove=True))

    '''
    Get all possible moves for a rook located at (r, c) location
    '''
    def getRookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1))
        enemy = 'b' if self.whiteMove else 'w'

        pinned = False
        pinDir = ()

        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pinDir = (self.pins[i][2], self.pins[i][3])
                if self.board[r][c][1] != 'Q':
                    self.pins.remove(self.pins[i])
                break

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not pinned or pinDir == d or pinDir == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece[0] == enemy:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break # Break so that the check stops at the enemy
                        elif endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            # No break since we're checking for empty spaces
                        else:
                            break # Break since we can't jump friendly pieces
                else:
                    break # Break when we reach the borders

    '''
    Get all possible moves for a bishop located at (r, c) location
    '''
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1))
        enemy = 'b' if self.whiteMove else 'w'

        pinned = False
        pinDir = ()

        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                pinDir = (self.pins[i][2], self.pins[i][3])
                #if self.board[r][c][1] != 'Q':
                self.pins.remove(self.pins[i])
                break

        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    if not pinned or pinDir == d or pinDir == (-d[0], -d[1]):
                        endPiece = self.board[endRow][endCol]
                        if endPiece[0] == enemy:
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            break # Break so that the check stops at the enemy
                        elif endPiece == '--':
                            moves.append(Move((r, c), (endRow, endCol), self.board))
                            # No break since we're checking for empty spaces
                        else:
                            break # Break since we can't jump friendly pieces
                    else:
                        break # Break when we reach the borders

    '''
    Get all possible moves for a knight located at (r, c) location
    '''
    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2))
        ally = 'w' if self.whiteMove else 'b'

        pinned = False

        for i in range(len(self.pins) -1, -1, -1):
            if self.pins[i][0] == r and self.pins[i][1] == c:
                pinned = True
                self.pins.remove(self.pins[i])
                break

        for i in knightMoves:
            endRow = r + i[0]
            endCol = c + i[1]
            if 0 <= endCol < 8 and 0 <= endRow < 8:
                if not pinned:
                    endPiece = self.board[endRow][endCol]
                    if endPiece[0] != ally:
                        moves.append(Move((r, c), (endRow, endCol), self.board))


    '''
    Get all possible moves for a king located at (r, c) location
    '''
    def getKingMoves(self, r, c, moves):
        rowMoves = (-1, -1, -1, 0, 0, 1, 1, 1)
        colMoves = (-1, 0, 1, -1, 1, -1, 0, 1)
        ally = 'w' if self.whiteMove else 'b'

        for i in range(8):
            endRow = r + rowMoves[i]
            endCol = c + colMoves[i]
            if 0 <= endCol < 8 and 0 <= endRow < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != ally:
                    if ally == 'w':
                        self.whiteKingLoc = (endRow, endCol)
                    else:
                        self.blackKingLoc = (endRow, endCol)
                    inCheck, checks, pins = self.pinsAndChecks()
                    if not inCheck:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    if ally == 'w':
                        self.whiteKingLoc = (r, c)
                    else:
                        self.blackKingLoc = (r, c)
                    

    '''
    Get all possible moves for a queen located at (r, c) location
    '''
    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    '''
    Return if king is in check, a list of checks and pins
    '''
    def pinsAndChecks(self):
        pins = []  # squares pinned and the direction its pinned from
        checks = []  # squares where enemy is applying a check
        in_check = False
        if self.whiteMove:
            enemy = "b"
            ally_color = "w"
            start_row = self.whiteKingLoc[0]
            start_col = self.whiteKingLoc[1]
        else:
            enemy = "w"
            ally_color = "b"
            start_row = self.blackKingLoc[0]
            start_col = self.blackKingLoc[1]
        # check outwards from king for pins and checks, keep track of pins
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1), (-1, -1), (-1, 1), (1, -1), (1, 1))
        for j in range(len(directions)):
            direction = directions[j]
            possible_pin = ()  # reset possible pins
            for i in range(1, 8):
                end_row = start_row + direction[0] * i
                end_col = start_col + direction[1] * i
                if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                    end_piece = self.board[end_row][end_col]
                    if end_piece[0] == ally_color and end_piece[1] != "K":
                        if possible_pin == ():  # first allied piece could be pinned
                            possible_pin = (end_row, end_col, direction[0], direction[1])
                        else:  # 2nd allied piece - no check or pin from this direction
                            break
                    elif end_piece[0] == enemy:
                        enemy_type = end_piece[1]
                        # 5 possibilities in this complex conditional
                        # 1.) orthogonally away from king and piece is a rook
                        # 2.) diagonally away from king and piece is a bishop
                        # 3.) 1 square away diagonally from king and piece is a pawn
                        # 4.) any direction and piece is a queen
                        # 5.) any direction 1 square away and piece is a king
                        if (0 <= j <= 3 and enemy_type == "R") or (4 <= j <= 7 and enemy_type == "B") or (
                                i == 1 and enemy_type == "P" and (
                                (enemy == "w" and 6 <= j <= 7) or (enemy == "b" and 4 <= j <= 5))) or (
                                enemy_type == "Q") or (i == 1 and enemy_type == "K"):
                            if possible_pin == ():  # no piece blocking, so check
                                in_check = True
                                checks.append((end_row, end_col, direction[0], direction[1]))
                                break
                            else:  # piece blocking so pin
                                pins.append(possible_pin)
                                break
                        else:  # enemy piece not applying checks
                            break
                else:
                    break  # off board
        # check for knight checks
        knight_moves = ((-2, -1), (-2, 1), (-1, 2), (1, 2), (2, -1), (2, 1), (-1, -2), (1, -2))
        for move in knight_moves:
            end_row = start_row + move[0]
            end_col = start_col + move[1]
            if 0 <= end_row <= 7 and 0 <= end_col <= 7:
                end_piece = self.board[end_row][end_col]
                if end_piece[0] == enemy and end_piece[1] == "N":  # enemy knight attacking a king
                    in_check = True
                    checks.append((end_row, end_col, move[0], move[1]))
        return in_check, pins, checks


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs

class Move():
    rankToRow = {'1' : 7, '2' : 6, '3' : 5, '4' : 4,
                '5' : 3, '6' : 2, '7' : 1, '8' : 0} # Ranks defined by rows
    rowToRank = {v:k for k, v in rankToRow.items()} # Returns chess notation of rank (row 7, rank 1), (row 5, rank 3)
    
    fileToCol = {'a' : 0, 'b' : 1, 'c' : 2, 'd' : 3,
                'e' : 4, 'f' : 5, 'g' : 6, 'h' : 7} # Files defined by columns
    colToFile = {v:k for k, v in fileToCol.items()} # Returns chess notation of file (col 3, file d), (col 7, file h)
    
    def __init__(self, startSq, endSq, board, isEnpassantMove = False, isCastleMove = False):
        self.startRow = startSq[0] # Move from this position
        self.startCol = startSq[1]
        self.endRow = endSq[0] # To this position
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]
        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol

        # Pawn promotion
        self.isPromotion = ((self.pieceMoved == 'wP' and self.endRow == 0) or (self.pieceMoved == 'bP' and self.endRow == 7))
        self.allowedPromotions = ['Q', 'N', 'B', 'R']

        # En passant
        self.isEnpassantMove = isEnpassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'bP' if self.pieceMoved == 'wP' else 'wP'
        
        #Piece Captured
        self.isCapture = self.pieceCaptured != '--'
        
        # Castling
        self.isCastleMove = isCastleMove

    # Overloading the equals function because we can't compare two objects of different types
    def __eq__(self, other): 
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False
    
    def __str__(self):
        # Castle move
        if self.isCastleMove:
            return 'O-O' if self.endCol == 6 else 'O-O-O'
        
        endSquare = self.getFileRank(self.endRow, self.endCol)

        # Pawn moves
        if self.pieceMoved[1] == 'P':
            if self.isCapture and self.isPromotion:
                return self.colToFile[self.startCol] + 'x' + endSquare + GameState().promotePiece
            elif self.isCapture:
                return self.colToFile[self.startCol] + 'x' + endSquare
            elif self.isPromotion:
                return endSquare + GameState().promotePiece
            else:
                return endSquare
        
        # Other piece moves
        moveString = self.pieceMoved[1]
        if GameState().checkmate:
            print('checkmate')
            moveString += 'X'
        elif GameState().check:
            print('inCheck')
            moveString += '+'
        elif self.isCapture:
            moveString += 'x'
        
        return moveString + endSquare
    
    def getChessNotation(self):
        # This method returns (a0, h0) which is not like real chess but it's close
        return self.getFileRank(self.startRow, self.startCol) + self.getFileRank(self.endRow, self.endCol)

    def getFileRank(self, row, col):
        return self.colToFile[col] + self.rowToRank[row]