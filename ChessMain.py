import pygame as p
import ChessEngine

Width = Height = 512 #screen size
Dimension = 8 #chess is 8*8 square
SQ_SIZE = Height // Dimension #size of square
MaxFps = 15
IMAGES = {}

def loadImages():
    pieces = ['wp', 'wR', 'wN', 'wB', 'wK', 'wQ', 'bp', 'bR', 'bN', 'bB', 'bK', 'bQ']
    for piece in pieces:
        IMAGES[piece] = p.transform.scale(p.image.load("images/" + piece + ".png"), (SQ_SIZE, SQ_SIZE))


def main():
    p.init()

    screen = p.display.set_mode((Width, Height))
    screen.fill(p.Color("white"))
    clock = p.time.Clock()
    gs = ChessEngine.GameState()
    vaildMoves = gs.currentValidMoves()
    moveMade = False #flag varaiable for when a move is made 
    animate = False
    promotion = () #used for pawn promotion

    loadImages()
    running = True
    sqSelected = ()
    playerClicks = []
    gameOver = False
    
    while running:
        for e in p.event.get():
            if e.type == p.QUIT:
                running = False
            elif e.type == p.MOUSEBUTTONDOWN:
                if not gameOver:
                    location = p.mouse.get_pos()  #(x, y) location of user mouse
                    col = location[0]//SQ_SIZE
                    row = location[1]//SQ_SIZE
                    if sqSelected == (row, col):  #the user clicked the same square twice
                        sqSelected = ()  #deselect
                        playerClicks = []  #clear player clicks
                    else:
                        sqSelected = (row, col)
                        playerClicks.append(sqSelected)  #append for both 1st and 2nd clicks
                    if len(playerClicks) == 2:
                        move = ChessEngine.Move(playerClicks[0], playerClicks[1], gs.board)
                        print(move.getChessNotation())
                        for i in range(len(vaildMoves)):
                            if move == vaildMoves[i]:
                                gs.makeMove(vaildMoves[i])
                                #pawn promotion
                                if gs.pawnPromotion:
                                    promotion = (vaildMoves[i].endRow, vaildMoves[i].endCol)
                                    gs.whiteTurn = not gs.whiteTurn
                                    drawPawnPromotion(screen, gs, promotion)
                                    gs.pawnPromotion = False
                                    gs.whiteTurn = not gs.whiteTurn
                                moveMade = True
                                animate = True
                                if vaildMoves[i].castle:
                                    animate = False
                                sqSelected = ()  #reset player clicks
                                playerClicks = []
                        if not moveMade:
                            playerClicks = [sqSelected]
            elif e.type == p.KEYDOWN:
                if e.key == p.K_z: #undo when 'z' is pressed
                    gs.undoMove()
                    moveMade = True
                    animate = False
                elif e.key == p.K_r: #reset the board when 'r' is pressed
                    gs = ChessEngine.GameState()
                    vaildMoves = gs.currentValidMoves()
                    sqSelected = ()
                    playerClicks = []
                    moveMade = False
                    gameOver = False

        if moveMade:
            if animate:
                animateMove(gs.moveLog[-1], screen, gs.board, clock)
            vaildMoves = gs.currentValidMoves()
            moveMade = False
            animate = False

        drawGameState(screen, gs, vaildMoves, sqSelected)

        #game over
        if gs.checkmate:
            gameOver = True
            if gs.whiteTurn:
                drawText(screen, "Black wins!")
            else:
                drawText(screen, "White wins!")
        elif gs.stalemate:
            gameOver = True
            drawText(screen, "Stalemate...")
        clock.tick(MaxFps)
        p.display.flip()


def highlightSquares(screen, gs, vaildMoves, sqSelected):
    global colors
    if sqSelected != ():
        r, c = sqSelected
        if gs.board[r][c][0] == ('w' if gs.whiteTurn else 'b'):
            #highlight selected square
            s = p.Surface((SQ_SIZE, SQ_SIZE))
            s.set_alpha(100)
            s.fill(p.Color(126, 182, 108))
            screen.blit(s, (c * SQ_SIZE, r * SQ_SIZE))
            s.fill(p.Color(130, 151, 105))
            s.set_alpha(200)
            #highlight the square where piece can move
            for move in vaildMoves:
                if move.startRow == r and move.startCol == c:
                    if gs.board[move.endRow][move.endCol] == "--": #highlight the square that no piece on it with green dot
                        p.draw.circle(screen, (130, 151, 105), (move.endCol*SQ_SIZE + SQ_SIZE // 2, move.endRow*SQ_SIZE+ SQ_SIZE // 2), 7)
                    else:
                        screen.blit(s, (move.endCol * SQ_SIZE, move.endRow * SQ_SIZE)) #highlight the square that no piece on it with green outline
                        p.draw.circle(screen, colors[((move.endRow + move.endCol) % 2)], (move.endCol*SQ_SIZE + SQ_SIZE // 2, move.endRow*SQ_SIZE+ SQ_SIZE // 2), 32)
    
    #highlight the king is being attacked
    if gs.inCheck(): 
        kingLocation = gs.whiteKingLocation if gs.whiteTurn else gs.blackKingLocation

        s = p.Surface((SQ_SIZE, SQ_SIZE), p.SRCALPHA)  # allow to use rgdb
        #漸層比較好看
        p.draw.circle(s, (227, 74, 64, 75), (SQ_SIZE // 2, SQ_SIZE // 2), 32)  # (R, G, B, Alpha)
        p.draw.circle(s, (227, 74, 64, 100), (SQ_SIZE // 2, SQ_SIZE // 2), 30)
        p.draw.circle(s, (227, 74, 64, 150), (SQ_SIZE // 2, SQ_SIZE // 2), 28)
        p.draw.circle(s, (227, 74, 64, 170), (SQ_SIZE // 2, SQ_SIZE // 2), 26)
        screen.blit(s, (kingLocation[1] * SQ_SIZE, kingLocation[0] * SQ_SIZE))
                    
            
                        

def drawGameState(screen, gs, vaildMoves, sqSelected):
    drawBoard(screen)
    highlightSquares(screen, gs, vaildMoves, sqSelected)
    drawPieces(screen, gs.board)


def drawBoard(screen):
    global colors
    colors = [p.Color(240,217,181), p.Color(182,137,100)]
    for r in range(Dimension):
        for c in range(Dimension): 
            color = colors[((r + c) % 2)]
            p.draw.rect(screen, color, p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawPieces(screen, board):
    for r in range(Dimension):
        for c in range(Dimension):
            piece = board[r][c]
            if piece != "--":
                screen.blit(IMAGES[piece], p.Rect(c * SQ_SIZE, r * SQ_SIZE, SQ_SIZE, SQ_SIZE))


def drawText(screen, text):
    font = p.font.SysFont("Helvitca", 32, False, False)

    textObject = font.render(text, 0, p.Color("Gray")) #use grey font to highlight black font
    textLocation = p.Rect(0, 0, Width, Height).move(Width/2 - textObject.get_width()/2, Height/2 - textObject.get_height()/2)
    screen.blit(textObject, textLocation)

    textObject = font.render(text, 0, p.Color("Black"))
    screen.blit(textObject, textLocation.move(2, 2))


def drawPawnPromotion(screen, gs, promotion):
    pieceRow, pieceCol = promotion
    #draw the black background to highlight promotion UI
    s = p.Surface((Width, Height))
    s.set_alpha(175)
    s.fill(p.Color("Black")) 
    screen.blit(s, (0, 0))

    promotionPieces = ['Q', 'N', 'R', 'B']
    promotionColor = 'w' if gs.whiteTurn else 'b'

    for i in range(4):
        row_offset = i if gs.whiteTurn else -i 
        currentRow = (pieceRow + row_offset) * SQ_SIZE #the row where choice UI display
        p.draw.circle(screen, ("silver"), (pieceCol*SQ_SIZE + SQ_SIZE // 2, currentRow + SQ_SIZE // 2), 32)
        screen.blit(IMAGES[promotionColor + promotionPieces[i]], p.Rect(pieceCol * SQ_SIZE, currentRow, SQ_SIZE, SQ_SIZE))

    p.display.flip() #update the screen to show UI

    choosing = True
    while choosing:
        for e in p.event.get():
            if e.type == p.QUIT:
                p.quit()
                exit()
            elif e.type == p.MOUSEBUTTONDOWN: #choosing the type of piece
                mouse_pos = p.mouse.get_pos()
                if pieceCol*SQ_SIZE <= mouse_pos[0] < (pieceCol+1)*SQ_SIZE: 
                    index = (mouse_pos[1] - pieceRow * SQ_SIZE) // SQ_SIZE
                    if not gs.whiteTurn:
                        index = 3 - index 
                    gs.board[pieceRow][pieceCol] = promotionColor + promotionPieces[index]
                    choosing = False

    drawBoard(screen)
    drawPieces(screen, gs.board)


def animateMove(move, screen, board, clock):
    global colors    
    dR = move.endRow - move.startRow
    dC = move.endCol - move.startCol
    framesPerSquare = 10 #frames to move one square
    if abs(dR) + abs(dC) > 5:
        framesPerSquare = 5 
    frameCount = (abs(dR) + abs(dC)) * framesPerSquare
    for frame in range(frameCount + 1):
        r, c = (move.startRow + dR*frame/frameCount, move.startCol + dC*frame/frameCount)
        drawBoard(screen)
        drawPieces(screen, board)
        #erase the piece moved from its ending square
        color = colors[(move.endRow + move.endCol)%2]
        endSquare = p.Rect(move.endCol*SQ_SIZE, move.endRow*SQ_SIZE, SQ_SIZE, SQ_SIZE)
        p.draw.rect(screen, color, endSquare)
        #draw captured piece onto rectangle
        if move.pieceCaptured != "--":
            screen.blit(IMAGES[move.pieceCaptured], endSquare)
        #draw moving piece
        screen.blit(IMAGES[move.pieceMoved], p.Rect(c*SQ_SIZE, r*SQ_SIZE, SQ_SIZE, SQ_SIZE))
        p.display.flip()
        clock.tick(60)

main()