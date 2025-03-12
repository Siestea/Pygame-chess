class GameState: #initialize Game board
    def __init__(self):
        self.board = [["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
                      ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["--", "--", "--", "--", "--", "--", "--", "--"],
                      ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
                      ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]]
        self.moveFunctions = {'p': self.pawnMoves, 'R': self.rookMoves, 'N': self.knightMoves,
                              'B': self.bishopMoves, 'Q': self.queenMoves, 'K': self.kingMoves}                                                               
        
        self.whiteTurn = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkmate = False
        self.stalemate = False

        #pawn promotion
        self.pawnPromotion = False

        #en.passant
        self.enpassantCoord = ()
        self.enpassantLog = [self.enpassantCoord]

        #castle
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]                                   


    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved #move the piece
        self.moveLog.append(move)  #save the move to undo if in need
        self.whiteTurn = not self.whiteTurn  #swap player
        #update king's location if needed
        if move.pieceMoved == "wK" :
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)

        #pawn promotion
        if move.pawnPromotionPossible:
            self.pawnPromotion = True

        #en.passant
        if move.enpassant:
            self.board[move.startRow][move.endCol] = "--"

        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantCoord = ((move.startRow + move.endRow)//2, move.endCol)
        else:
            self.enpassantCoord = None
            
        self.enpassantLog.append(self.enpassantCoord)
        
        #castle    
        if move.castle:
            if move.pieceMoved[1] == 'K':
                if move.endCol - move.startCol == 2: #king side
                    self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1] #move the rook
                    self.board[move.endRow][move.endCol+1] = "--" #erase old rook
                else: #queen side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2] #move the rook
                    self.board[move.endRow][move.endCol-2] = "--"

        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, 
                                                 self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))
        
       


    def undoMove(self): #similar to makeMove
        if len(self.moveLog) != 0:
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteTurn = not self.whiteTurn
            self.checkmate = False
            self.stalemate = False

            #update king's location if needed
            if move.pieceMoved == "wK" :
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)

            #pawn promotion
            if move.pawnPromotionPossible:
                self.pawnPromotion = False

            #en.passant
            if move.enpassant:
                    self.board[move.endRow][move.endCol] = "--"
                    self.board[move.startRow][move.endCol] = move.pieceCaptured
            
            self.enpassantLog.pop()
            self.enpassantCoord = self.enpassantLog[-1]
            
            #undo castling
            if move.castle:
                if move.endCol - move.startCol == 2: #king side
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = "--"
                else: #queen side
                    self.board[move.endRow][move.endCol-2] = self.board[move.endRow][move.endCol+1]
                    self.board[move.endRow][move.endCol+1] = "--"
                    
            '''
            self.castleRightsLog.pop()
            self.currentCastlingRight = self.castleRightLog[-1]
            '''
        
            self.castleRightsLog.pop() #discard the lastest move we did
            newRights = self.castleRightsLog[-1]
            self.currentCastlingRight = CastleRights(newRights.wks, newRights.bks, newRights.wqs, newRights.bqs) #set the current castle rights to the last one in the list


    def updateCastleRights(self, move):
        if move.pieceMoved == "wK":
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == "bK":
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == "wR":
            if move.startRow == 7:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == "bR":
            if move.startRow == 0:
                if move.startCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7: #right rook
                    self.currentCastlingRight.bks = False

        if move.pieceCaptured == 'wR':
            if move.endRow == 7:
                if move.endCol == 0: #left rook
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7: #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0: #left rook
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7: #right rook
                    self.currentCastlingRight.bks = False

    

    def currentValidMoves(self): #filter vaild move from allPossibleMoves, implement every moves from it
        tempEnpassant = self.enpassantCoord
        tempCastleRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                        self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        moves = self.allPossibleMoves() 
        
        if self.whiteTurn:
            self.castleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.castleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        
        for i in range(len(moves)-1, -1, -1): #prevent the remove defect
            self.makeMove(moves[i])
            self.whiteTurn = not self.whiteTurn #change to enemy move
            if self.inCheck(): #if do the move, and the enemy can check our king in next move, the move is invaild
                moves.remove(moves[i]) #remove invaild move 
            self.whiteTurn = not self.whiteTurn
            self.undoMove()

        if len(moves) == 0:
            if self.inCheck():
                self.checkmate = True
            else: 
                self.stalemate = True

        self.enpassantCoord = tempEnpassant
        self.currentCastlingRight = tempCastleRights
        return moves


    def allPossibleMoves(self): #generate all possible moves
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteTurn) or (turn == 'b' and not self.whiteTurn):
                    piece = self.board[r][c][1]
                    self.moveFunctions[piece](r, c, moves)
        return moves

    
    def inCheck(self): #detect if the current player is in checks
        if self.whiteTurn:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])


    def squareUnderAttack(self, r, c): #detect if the enemy can attack the square (r, c)
        self.whiteTurn = not self.whiteTurn
        oppMoves = self.allPossibleMoves()
        self.whiteTurn = not self.whiteTurn
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: #square is under attack
                return True
        return False
    

    def pawnMoves(self, r, c, moves):
        if self.whiteTurn: #white pawn moves
            if self.board[r-1][c] == "--":  
                moves.append(Move((r, c), (r-1, c), self.board))
                if r == 6 and self.board[r-2][c] == "--":
                    moves.append(Move((r, c), (r-2, c), self.board))
            #capture enemy
            if c-1 >= 0: #capture left enemy
                if self.board[r-1][c-1][0] == 'b':
                    moves.append(Move((r, c) , (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantCoord:  #player is allowed to do enpassant move
                    moves.append(Move((r, c) , (r-1, c-1), self.board, enpassant=True))
            if c+1 <= 7: #capture right enemy
                if self.board[r-1][c+1][0] == 'b':
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantCoord:  #player is allowed to do enpassant move
                    moves.append(Move((r, c), (r-1, c+1), self.board, enpassant=True))

        else: #black pawn moves
            if self.board[r+1][c] == "--": 
                moves.append(Move((r, c), (r+1, c), self.board))
                if r == 1 and self.board[r+2][c] == "--":
                    moves.append(Move((r, c), (r+2, c), self.board)) 
            if c-1 >= 0: #capture left enemy
                if self.board[r+1][c-1][0] == 'w':
                    moves.append(Move((r, c) ,(r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantCoord: #player is allowed to do enpassant move
                    moves.append(Move((r, c), (r+1, c-1), self.board, enpassant=True))
            if c+1 <= 7: #capture right enemy
                if self.board[r+1][c+1][0] == 'w':
                    moves.append(Move((r, c) ,(r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantCoord: #player is allowed to do enpassant move
                    moves.append(Move((r, c), (r+1, c+1), self.board, enpassant=True))

    
    def rookMoves(self, r, c, moves):
        directions = ((-1, 0), (0, -1), (1, 0), (0, 1)) #up, down, left, right
        enemyColor = 'b' if self.whiteTurn else 'w' 
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty space valid 
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #enemy piece is the max distance 
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #not enemy
                        break
                else:
                    break
    

    def knightMoves(self, r, c, moves):
        directions = ((-1, 2), (2, -1), (1, 2), (2, 1), (-1, -2), (-2, -1), (1, -2), (-2, 1))
        allyColor = 'w' if self.whiteTurn else 'b' 
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))


    def bishopMoves(self, r, c, moves):
        directions = ((-1, -1), (1, -1), (1, 1), (-1, 1)) #up, down, left, right
        enemyColor = 'b' if self.whiteTurn else 'w' 
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": #empty space 
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor: #enemy piece is the max distance
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else: #ally
                        break
                else:
                    break


    def queenMoves(self, r, c, moves): #queen = rook + bishop
        self.rookMoves(r, c, moves)
        self.bishopMoves(r, c, moves)


    def kingMoves(self, r, c, moves):
        directions = ((1, -1), (1, 1), (-1, -1), (-1, 1), (-1, 0), (0, -1), (1, 0), (0, 1))
        allyColor = 'w' if self.whiteTurn else 'b' 
        for d in directions:
            endRow = r + d[0]
            endCol = c + d[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                    moves.append(Move((r, c), (endRow, endCol), self.board))
    
    

    def castleMoves(self, r, c, moves):
        if self.squareUnderAttack(r, c): #where the bug at
            return #can not castle while in check
        if (self.whiteTurn and self.currentCastlingRight.wks) or (not self.whiteTurn and self.currentCastlingRight.bks):
            self.kingSideCastleMoves(r, c, moves)
        if (self.whiteTurn and self.currentCastlingRight.wqs) or (not self.whiteTurn and self.currentCastlingRight.bqs):
            self.queenSideCastleMoves(r, c, moves)


    def kingSideCastleMoves(self, r, c, moves):
        if self.board[r][c+1] == "--" and self.board[r][c+2] == "--":
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2): #if king side not being attacked
                moves.append(Move((r, c), (r, c+2), self.board, castle=True))


    def queenSideCastleMoves(self, r, c, moves):    
        if self.board[r][c-1] == "--" and self.board[r][c-2] == "--" and self.board[c][r-3] == "--": 
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2): #if queen side not being attacked
                moves.append(Move((r, c), (r, c-2), self.board, castle=True))     
                

class CastleRights:
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs


class Move:
    ranksToRows = {"1": 7, "2": 6, "3": 5, "4": 4,
                   "5": 3, "6": 2, "7": 1, "8": 0}
    rowsToRanks = {v: k for k, v in ranksToRows.items()}
    filesToCols = {"a": 0, "b": 1, "c": 2, "d": 3,
                   "e": 4, "f": 5, "g": 6, "h": 7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, enpassant=False, castle=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]  
        self.pieceCaptured = board[self.endRow][self.endCol]
        #pawn promotion
        self.pawnPromotionPossible = (self.pieceMoved == "wp" and self.endRow == 0) or (self.pieceMoved == "bp" and self.endRow == 7)
        #en.passant
        self.enpassant = enpassant
        if enpassant:
            self.pieceCaptured = "wp" if self.pieceMoved == "bp"  else "bp"
        #castling
        self.castle = castle

        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol


    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False


    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]