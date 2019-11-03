from random import randrange
from cachetools import LRUCache
from timeit import default_timer


class ConnectFiveBoard:

    """This class offers a template for the game board used in the game of Gomoku a.k.a Connect 5.
    Connect 5 is a perfect information two-player alternating turn-based game played on a 15 by 15 square grid lattices.
    Player 1's pieces are denoted by "X" and Player 2's pieces are denoted by "O".
    The objective of the game is to place your pieces on the board such that you achieve 5 connected pieces in a row or column or on the same diagonal.
    Once you have placed a piece on the board, you may not move it hereafter.
    Once the board is full, a draw will be declared if neither player has won.
    """

    def __init__(self, size=15):

        """This method initialises an instance of the ConnectFiveBoard class.
        Keyword arguments:
        size (int) -- This argument indicates the desired size of the board. In the case of Connect 5, the default size is 15 by 15.
        """

        # self.criteria -- the number of consecutive pieces needed to win
        # self.board -- 2D array representing the board
        # self.undoStack -- array acting as a stack for the undo function
        # self.size (int) -- the size of the game board
        self.size = size

        # self.winningCriteria (int) -- the criteria for winning; 5 connected pieces
        self.winningCriteria = 5

        # self.board (list[list]) -- the 2D list of lists which represents the game board
        self.board = [size * [None] for _ in range(size)]

        # self.undoStack (list) -- a FIFO data structure which holds the moves player by either player
        self.undoStack = []

        # limit (int) -- the highest integer used in the hashKey
        limit = 2 ** 64

        # self.hashKey (int) -- a random number generated to represent the hash key of the empty board position
        # This variable is ONLY used by the AI computer player
        self.hashKey = randrange(0, limit)

        # self.table (LRUCache) -- a cache data structure which holds information about recently visited positions
        # This variable is ONLY used by the AI computer player
        self.table = LRUCache(1572751)

        # self.squareValue (list[list[tuple]]) -- a randomly generated 15 by 15 by 2 table which contains hashKey values for different positions on the board
        self.squareValue = [[(randrange(0, limit), randrange(0, limit)) for _ in range(size)] for _ in range(size)]

    def placePiece(self, row, col, piece):
        """This method places a new piece on the board for the computer.
        Warning: this method does not check whether a move is legal and should only be used by the AI.
        Keyword arguments:
        row (int) -- the row index on the board
        col (int) -- the col index on the board
        piece (str) -- the piece to place on the board "X" or "O"
        """
        # places the piece on the board
        self.board[row][col] = piece

        # pushes the move onto the undo stack
        self.undoStack.append((row, col, piece))

        # updates the hash key of the position
        self.hashKey ^= self.squareValue[row][col][0 if piece == "X" else 1]

    def undoMove(self):
        """This method undoes the most recent move on the board for the computer.
        Warning: this method does not check whether there is a recent move and should only be used by the AI.
        """
        # pops the most recent move off the stack
        row, col, piece = self.undoStack.pop()

        # clears that square
        self.board[row][col] = None

        # updates the hash key of the position
        self.hashKey ^= self.squareValue[row][col][0 if piece == "X" else 1]

    def userPlacePiece(self, row, col, piece):
        """This method first checks if the move is legal and then places a new piece on the board for the human player.
        Keyword arguments:
        row (int) -- the row index on the board
        col (int) -- the col index on the board
        piece (str) -- the piece to place on the board "X" or "O"
        """
        # checks if the move is legal
        if self.isLegalMove(row, col) and (piece == "X" or piece == "O"):

            # places the piece on the board
            self.board[row][col] = piece

            # pushes the move onto the undo stack
            self.undoStack.append((row, col, piece))

            # updates the hash key of the board
            self.hashKey ^= self.squareValue[row][col][0 if piece == "X" else 1]

            # indicates that the move has been made
            return True

        # indicates that the move cannot be made
        return False

    def userUndoMove(self):
        """This method undoes the most recent ply of moves and allows the user to replay the previous move.
        Warning: once deleted, the user can only recover the move by replaying it on the board.
        """
        # for this method to work, at least 2 moves must have been played on the board
        if len(self.undoStack) >= 2:

            # deletes the most recent move
            row, col, piece = self.undoStack.pop()

            # updates the hashKey
            self.hashKey ^= self.squareValue[row][col][0 if piece == "X" else 1]

            # deletes the next recent move
            row, col, piece = self.undoStack.pop()

            # updates the hashKey
            self.hashKey ^= self.squareValue[row][col][0 if piece == "X" else 1]

    def isLegalMove(self, row, col):
        """This method checks if a move on the board is legal by the rule of Gomoku: cannot place a piece off the board or on top of another piece.
        Keyword arguments:
        row (int) -- the row index on the board
        col (int) -- the col index on the board
        """
        # checks if the piece is placed off the board or on top of an existing piece
        if 0 <= row < self.size and 0 <= col < self.size and self.board[row][col] is None:

            # legal move has been detected
            return True

        # illegal move has been detected
        return False

    def isBoardEmpty(self):
        """This method checks if the current board position is empty i.e. does not have a single piece on it."""
        # checks every row
        for row in self.board:

            # checks every square in the row
            for square in row:

                # checks if the square is empty
                if square is not None:

                    # a piece on the board has been found
                    return False

        # the board is empty
        return True

    def isBoardFull(self):
        """This method checks if the current board position is empty i.e. does not have an empty square on it."""
        # checks every row
        for row in self.board:

            # checks every square in the row
            for square in row:

                # checks if the square is empty
                if square is None:

                    # an empty square has been found
                    return False

        # the board is full
        return True

    def getFirstFreeSquare(self):
        """This method retrieves the first empty square which it finds on the board."""
        # checks every row
        for row in range(self.size):

            # checks every square in the row
            for col in range(self.size):

                # checks if the square is empty
                if self.board[row][col] is None:

                    # an empty square is found
                    return row, col

    def selfHasFour(self):
        """This method checks if the current player has a connection of four pieces with an empty square on either end.
        Warning: this check is not 100% definitive. It serves as a quick check for the AI.
        """
        # this is only possible if there has been at least 4 pieces from either player on the board
        if len(self.undoStack) > 8:

            # looks at the second most recent move on the board: logic been that only the most recent move could have resulted in such a combination.
            row, col, piece = self.undoStack[-2]

            # checks the rows, columns and diagonals
            if self.hasRowCombination(row, col, piece, 4, 1) or self.hasColCombination(row, col, piece, 4, 1) \
                    or self.hasLeftDiagonalCombination(row, col, piece, 4, 1) or self.hasRightDiagonalCombination(row, col, piece, 4, 1):

                # a combination of four has been found
                return True

        # a combination of four has not been found
        return False

    def opponentHasFour(self):
        """This method checks if the opponent player has a connection of four pieces with an empty square on either end.
        Warning: this check is not 100% definitive. It serves as a quick check for the AI.
        """
        # At least 3.5 plies must have been made for such a combination to even exist
        if len(self.undoStack) > 6:

            # looks at the most recent move on the board: logic been that only the most recent move could have resulted in such a combination.
            row, col, piece = self.undoStack[-1]

            # checks the rows, columns and diagonals
            if self.hasRowCombination(row, col, piece, 4, 1) or self.hasColCombination(row, col, piece, 4, 1) \
                    or self.hasLeftDiagonalCombination(row, col, piece, 4, 1) or self.hasRightDiagonalCombination(row, col, piece, 4, 1):

                # a combination of four has been found
                return True

        # a combination of four has not been found
        return False

    def findQuickMove(self, row, col, piece):
        """This method assists finding a threatening move or immediately winning move for the AI.
        Warning: this method should only be used under the condition that there exists such a move.
        """
        # the results from the row search
        status, winRow, winCol = self.findQuickRowMove(row, col, piece)
        if status:
            return winRow, winCol

        # the results from the column search
        status, winRow, winCol = self.findQuickColMove(row, col, piece)
        if status:
            return winRow, winCol

        # the results from the left diagonal search
        status, winRow, winCol = self.findQuickLeftDiagonalMove(row, col, piece)
        if status:
            return winRow, winCol

        # the results from the right diagonal search
        status, winRow, winCol = self.findQuickRightDiagonalMove(row, col, piece)
        if status:
            return winRow, winCol

    def findQuickWin(self):
        """This method finds an immediate winning move for the AI.
        Warning: this method should only be used under the condition that there exists a crushing move.
        """
        # looks at the second most recent move
        row, col, piece = self.undoStack[-2]
        return self.findQuickMove(row, col, piece)

    def findForcedBlock(self):
        """This method finds a forced blocking move for the AI.
        Warning: this method should only be used under the condition that there exists a threat from the opponent.
        """
        # looks at the most recent move
        row, col, piece = self.undoStack[-1]
        return self.findQuickMove(row, col, piece)

    def hasWinner(self):
        """This method checks if either player has won the game."""
        # checks if any moves were previously made
        if self.undoStack:

            # only the most recent move may have resulted in a win otherwise the game would be over.
            row, col, piece = self.undoStack[-1]

            # checks the rows/columns/diagonals
            if self.hasRowCombination(row, col, piece) or self.hasColCombination(row, col, piece) or self.hasLeftDiagonalCombination(row, col, piece) \
                    or self.hasRightDiagonalCombination(row, col, piece):

                # a winning board position has been found
                return True

        # a winning board position has not been found
        return False

    def findQuickRowMove(self, row, col, piece):
        """This method finds a quick block or killer move in a row."""
        # consecutive (int) -- number of consecutive pieces in a row
        consecutive = 0

        # searches through all the relevant columns on the board
        for eachCol in range(max(0, col - 3), min(self.size, col + 4)):

            # checks if the grid contains the piece
            if self.board[row][eachCol] == piece:

                # increments the consecutive count
                consecutive += 1

                # checks if there are 4 pieces in a row
                if consecutive == 4:

                    # checks the left end
                    if eachCol - 4 >= 0 and self.board[row][eachCol - 4] is None:
                        return True, row, eachCol - 4

                    # checks the right end
                    if eachCol + 1 < self.size and self.board[row][eachCol + 1] is None:
                        return True, row, eachCol + 1

            # if this section of the code is reached, the square does not contain the piece
            else:

                # resets consecutive
                consecutive = 0

        # 4 in a row not found
        return False, None, None

    def hasRowCombination(self, row, col, piece, criteria=5, blockedEnds=2):
        """This method checks if there are a certain number of connected pieces in a row.
        Keyword arguments:
        row (int) -- the row index of a move on the board
        col (int) -- the column index of a move on the board
        piece (str) -- the piece to check for "X" or "O"
        criteria (int) -- a number from 1-5 (default: 5)
        blockedEnds (int) -- the maximum allowed number of dead ends to the sequence (default: 2)
        """
        # consecutive (int) -- the number of consecutive pieces in a row
        consecutive = 0

        # opponent's piece
        opponent = "X" if piece == "O" else "O"

        # iterates through every relevant column
        for eachCol in range(max(0, col - criteria + 1), min(self.size, col + criteria)):

            # checks if the grid contains the piece
            if self.board[row][eachCol] == piece:
                consecutive += 1

                # checks if there are # pieces in a row
                if consecutive == criteria:

                    # 2 dead ends
                    if blockedEnds == 2:
                        return True

                    # left -- whether the left end is blocked (bool)
                    left = eachCol - criteria >= 0 and self.board[row][eachCol - criteria] != opponent

                    # right -- whether the right end is blocked (bool)
                    right = eachCol + 1 < self.size and self.board[row][eachCol + 1] != opponent

                    # 1 dead end
                    if blockedEnds == 1 and (left or right):
                        return True

                    # 0 dead end
                    if left and right:
                        return True

            # if this section of the code is reached, the square does not contain the piece
            else:

                # resets consecutive
                consecutive = 0

        # 4 in a row not found
        return False

    def findQuickColMove(self, row, col, piece):
        """This method finds a quick block or killer move in a column."""
        # consecutive (int) -- the number of consecutive pieces in a column
        consecutive = 0

        for eachRow in range(max(0, row - 3), min(self.size, row + 4)):

            # checks if the grid contains the piece
            if self.board[eachRow][col] == piece:

                consecutive += 1

                # checks if there are 4 consecutive pieces in a column
                if consecutive == 4:

                    if eachRow - 4 >= 0 and self.board[eachRow - 4][col] is None:
                        return True, eachRow - 4, col

                    if eachRow + 1 < self.size and self.board[eachRow + 1][col] is None:
                        return True, eachRow + 1, col

            # if this section of the code is reached, the square does not contain the piece
            else:
                # resets the count
                consecutive = 0

        return False, None, None

    def hasColCombination(self, row, col, piece, criteria=5, blockedEnds=2):
        """This method checks if there are a certain number of connected pieces in a column.
        Keyword arguments:
        row (int) -- the row index of a move on the board
        col (int) -- the column index of a move on the board
        piece (str) -- the piece to check for "X" or "O"
        criteria (int) -- a number from 1-5 (default: 5)
        blockedEnds (int) -- the maximum allowed number of dead ends to the sequence (default: 2)
        """
        # consecutive -- number of consecutive pieces in a column (int)
        consecutive = 0

        # opponent's piece
        opponent = "X" if piece == "O" else "O"

        for eachRow in range(max(0, row - criteria + 1), min(self.size, row + criteria)):

            # checks if the grid contains the piece
            if self.board[eachRow][col] == piece:
                consecutive += 1

                # checks if there are # consecutive pieces in a column
                if consecutive == criteria:

                    # 2 dead ends
                    if blockedEnds == 2:
                        return True

                    # top -- whether the top end is unblocked (bool)
                    top = eachRow - criteria >= 0 and self.board[eachRow - criteria][col] != opponent

                    # bottom -- whether the bottom end is unblocked (bool)
                    bottom = eachRow + 1 < self.size and self.board[eachRow + 1][col] != opponent

                    # 1 dead end
                    if blockedEnds == 1 and (top or bottom):
                        return True

                    # 0 dead end
                    if top and bottom:
                        return True

            # if this section of the code is reached, the square does not contain the piece
            else:

                # resets the count
                consecutive = 0

        return False

    def findQuickLeftDiagonalMove(self, row, col, piece):
        """This method finds a quick block or killer move in a left slanted diagonal."""
        # consecutive (int) -- number of consecutive pieces on the same left slanted diagonal
        consecutive = 0

        # inc (int) -- increment to the starting index
        for inc in range(-1 * min(row, col, 3), min(self.size - row, self.size - col, 4)):

            # checks if the square contains the piece
            if self.board[row + inc][col + inc] == piece:
                consecutive += 1

                # checks if there are 4 on the same diagonal
                if consecutive == 4:

                    thisRow, thisCol = row + inc, col + inc

                    if thisRow - 4 >= 0 and thisCol - 4 >= 0 and self.board[thisRow - 4][thisCol - 4] is None:
                        return True, thisRow - 4, thisCol - 4

                    if thisRow + 1 < self.size and thisCol + 1 < self.size and self.board[thisRow + 1][thisCol + 1] is None:
                        return True, thisRow + 1, thisCol + 1

            # if this section of the code is reached, the square does not contain the piece
            else:
                # resets consecutive
                consecutive = 0

        return False, None, None

    def hasLeftDiagonalCombination(self, row, col, piece, criteria=5, blockedEnds=2):
        """This method checks if there are a certain number of connected pieces on the same left slanted diagonal.
        Keyword arguments:
        row (int) -- the row index of a move on the board
        col (int) -- the column index of a move on the board
        piece (str) -- the piece to check for "X" or "O"
        criteria (int) -- a number from 1-5 (default: 5)
        blockedEnds (int) -- the maximum allowed number of dead ends to the sequence (default: 2)
        """
        # consecutive (int) -- number of consecutive pieces in a row
        consecutive = 0

        # opponent's piece
        opponent = "X" if piece == "O" else "O"

        # inc (int) -- increment to the starting index
        for inc in range(-1 * min(row, col, criteria - 1), min(self.size - row, self.size - col, criteria)):

            # checks if the square contains the piece
            if self.board[row + inc][col + inc] == piece:

                consecutive += 1

                # checks if there are 5 on the same diagonal
                if consecutive == criteria:

                    # 2 dead ends
                    if blockedEnds == 2:
                        return True

                    thisRow, thisCol = row + inc, col + inc

                    # top -- whether the top end is unblocked (bool)
                    top = (thisRow - criteria >= 0 and thisCol - criteria >= 0) and self.board[thisRow - criteria][thisCol - criteria] != opponent

                    # bottom -- whether the bottom end is unblocked (bool)
                    bottom = (thisRow + 1 < self.size and thisCol + 1 < self.size) and self.board[thisRow + 1][thisCol + 1] != opponent

                    # 1 dead end
                    if blockedEnds == 1 and (top or bottom):
                        return True

                    # 0 dead end
                    if top and bottom:
                        return True

            # if this section of the code is reached, the square does not contain the piece
            else:

                # resets consecutive
                consecutive = 0

        return False

    def findQuickRightDiagonalMove(self, row, col, piece):
        """This method finds a quick block or killer move on a right slanted diagonal."""
        # consecutive (int) -- number of consecutive pieces
        consecutive = 0

        # inc -- increment to the starting index
        for inc in range(-1 * min(row, self.size - col - 1, 3), min(self.size - row, col + 1, 4)):

            # checks if the square contains the piece
            if self.board[row + inc][col - inc] == piece:

                consecutive += 1

                # checks if there are 4 pieces on the same diagonal
                if consecutive == 4:

                    thisRow, thisCol = row + inc, col - inc

                    if thisRow - 4 >= 0 and thisCol + 4 < self.size and self.board[thisRow - 4][thisCol + 4] is None:
                        return True, thisRow - 4, thisCol + 4

                    if thisRow + 1 < self.size and thisCol - 1 >= 0 and self.board[thisRow + 1][thisCol - 1] is None:
                        return True, thisRow + 1, thisCol - 1

            # if this section of the code is reached, the square does not contain the piece
            else:

                # resets consecutive
                consecutive = 0

        return False, None, None

    def hasRightDiagonalCombination(self, row, col, piece, criteria=5, blockedEnds=2):
        """This method checks if there are a certain number of connected pieces on the same right slanted diagonal.
        Keyword arguments:
        row (int) -- the row index of a move on the board
        col (int) -- the column index of a move on the board
        piece (str) -- the piece to check for "X" or "O"
        criteria (int) -- a number from 1-5 (default: 5)
        blockedEnds (int) -- the maximum allowed number of dead ends to the sequence (default: 2)
        """
        # consecutive (int) -- number of consecutive pieces in a column (int)
        consecutive = 0

        # opponent's piece
        opponent = "X" if piece == "O" else "O"

        # inc (int) -- increment to the starting index
        for inc in range(-1 * min(row, self.size - col - 1, criteria - 1), min(self.size - row, col + 1, criteria)):

            # checks if the square contains the piece
            if self.board[row + inc][col - inc] == piece:

                consecutive += 1

                # checks if there are 5 pieces on the same diagonal
                if consecutive == criteria:

                    # 2 dead ends
                    if blockedEnds == 2:
                        return True

                    thisRow, thisCol = row + inc, col - inc

                    # top -- whether the top end is unblocked (bool)
                    top = (thisRow - criteria >= 0 and thisCol + criteria < self.size) and self.board[thisRow - criteria][thisCol + criteria] != opponent

                    # bottom -- whether the bottom end is unblocked (bool)
                    bottom = (thisRow + 1 < self.size and thisCol - 1 >= 0) and self.board[thisRow + 1][thisCol - 1] != opponent

                    # 1 dead end
                    if blockedEnds == 1 and (top or bottom):
                        return True

                    # 0 dead end
                    if top and bottom:
                        return True

            # if this section of the code is reached, the square does not contain the piece
            else:

                # resets consecutive
                consecutive = 0

        return False

    def prettyPrint(self):
        """This method prints the current position of the Gomoku board."""
        # prints the top edge
        self.printEdge()

        # prints each row on the board
        for row in range(self.size):

            self.printContent(row)

            # prints the bottom edge
            self.printEdge()

        # prints the column numbers
        self.printColNumber()

    def printContent(self, row):
        """This method prints one row of the Gomoku board."""

        # content -- string of pieces on the board
        content = "|"

        for square in self.board[row]:

            # checks if the square is empty
            if square is None:

                content += " " * 3 + "|"

            # if this section of the code is reached, the square is not empty
            else:

                content += " " + square + " |"

        # adds in the row number at the end
        content += " " + str(row)

        # prints content
        print(content)

    def printEdge(self):
        """This method prints the horizontal edge of the Gomoku board."""
        print("|---" + "----" * (self.size - 2) + "----|")

    def printColNumber(self):
        """This method prints the column numbers of the board."""
        s = ""
        for i in range(self.size):
            if i < 10:
                s += " "
            s += " {} ".format(i)
        print(s)


class ConnectFiveEngine:

    """This class create AI players in the game of Connect 5 to play against human players or other AI players.
    In this version, the AI player uses the miniMax algorithm with alpha beta pruning, a transposition table and iterative deepening search.
    """

    def __init__(self, board, depth, timeLimit):
        """This method initialises an instance of the ConnectFiveEngine class.
        Keyword arguments:
        board (ConnectFiveBoard class) -- An instance of ConnectFiveBoard class is given to the AI upon initialisation.
        Note: "X" is taken to be the maximising player and "O" is taken to be the minimising player.
        """
        # self.game -- an instance of the ConnectFiveBoard class representing the live game
        self.game = board

        # self.board -- allows quick access to the board attribute of the live game
        self.board = self.game.board

        # self.size -- size of the board
        self.size = len(self.board)

        # self.timeLimit -- time cap given to the AI to make a move
        self.timeLimit = timeLimit

        # self.criteria -- the criteria for winning the game i.e. 5 connected pieces
        self.criteria = 5

        # depth - the depth of the search engine
        self.depth = depth

        # self.combinationScore -- heuristic score for different streak combinations (hash map)
        # keys (tuples) -- tuples of the form (Consecutive, BlockedEnds, CurrentTurn)
        # values (float) -- an evaluation of different positions
        self.combinationScore = {(5, 0, True): 200000000, (5, 0, False): 200000000, (5, 1, True): 200000000, (5, 1, False): 200000000, (5, 2, True): 200000000,
                                 (5, 2, False): 200000000, (4, 0, True): 100000000, (4, 0, False): 50000000, (4, 1, True): 100000000, (4, 1, False): 50,
                                 (3, 0, True): 10000, (3, 0, False): 50, (3, 1, True): 12.5, (3, 1, False): 7.5, (2, 0, True): 7.5, (2, 0, False): 5,
                                 (2, 1, True): 2, (2, 1, False): 2, (1, 0, True): 1, (1, 0, False): 1, (1, 1, True): 0.5, (1, 1, False): 0.5}

    def overallHeuristicScore(self, turn):
        """This method gets the total heuristic score for a position on the board."""
        # overall heuristic score of the position
        return self.horizontalHeuristic(turn) + self.leftDiagonalHeuristic(turn) + self.verticalHeuristic(turn) + self.rightDiagonalHeuristic(turn)

    def getHeuristicScore(self, sequence, turn):
        """This method gets the heuristic score for a single row or column or diagonal.
        Keyword arguments:
        sequence (list) -- a list of row or column or diagonal entries with None as an extra dummy entry in the end.
        """
        # total (float) -- heuristic value total
        # count (int) -- the number of consecutive pieces
        # piece (str) -- piece in the current square
        count, total, piece = 0, 0, None

        # sequence has a dummy None entry as last entry for convenience
        for index, square in enumerate(sequence):

            # square -- current square
            # index -- column index of square
            # checks if the current square contains the same piece as the previous square
            if square == piece:

                # checks if the previous square is empty
                if piece is None:
                    continue

                # if this section of the code is reached, there is a piece in the previous square
                count += 1

            # if this section of the code is reached, the piece in the previous square is different to the piece in the current square
            else:

                # checks if the previous piece exists
                if piece is not None and count > 0:

                    # blockedEnds -- the number of blocked ends to the sequence (int)
                    # start -- the starting index of the sequence
                    blockedEnds, start = 0, index - count - 1

                    # checks if a piece is blocking the right end
                    if square is not None or index >= len(sequence) - 1:
                        blockedEnds += 1

                    # checks if the sequence starts at the edge of the board
                    if start < 0:
                        blockedEnds += 1

                    # checks if a piece is blocking the left end
                    elif sequence[start] is not None:
                        blockedEnds += 1

                    # info -- a collection of information required to determine the heuristic score (tuple)
                    info = (count, blockedEnds, turn == piece)

                    # checks if the current status yields any increase in the heuristic value
                    if info in self.combinationScore:
                        # updates the total heuristic score
                        total = total + self.combinationScore[info] if piece == "X" else total - self.combinationScore[info]

                # updates count and piece as a different piece was found
                piece = square
                count = 0 if piece is None else 1

        # total -- heuristic score (float)
        return total

    def horizontalHeuristic(self, turn):
        """This method calculates the total heuristic score of horizontal streaks on the board."""
        # total (float) -- heuristic value total
        total = 0

        for row in self.board:

            # adds a dummy None entry at the end of the row as padding
            total += self.getHeuristicScore(row + [None], turn)

        return total

    def verticalHeuristic(self, turn):
        """This method calculates the total heuristic score of vertical streaks on the board."""
        # total (float) -- heuristic value total
        total = 0

        for col in range(self.size):

            # column (list) - a list of column entries
            column = self.getColumn(col)

            total += self.getHeuristicScore(column, turn)

        return total

    def leftDiagonalHeuristic(self, turn):
        """This method calculates the total heuristic score of left-slanted diagonal streaks on the board."""
        # total (float) -- heuristic value total
        # endRow (int) -- the last row where the diagonal will be at least length 5
        # startingSquares (array[tuple]) -- starting coordinates for diagonals
        total, endRow = 0, self.size - self.criteria + 1
        startingSquares = [(row, 0) for row in range(endRow)] + [(0, col) for col in range(1, endRow)]

        for row, col in startingSquares:

            # diagonal (list) -- a list of diagonal entries
            diagonal = self.getLeftDiagonal(row, col)

            total += self.getHeuristicScore(diagonal, turn)

        return total

    def rightDiagonalHeuristic(self, turn):
        """This method calculates the total heuristic score of right-slanted diagonal streaks on the board."""
        # total (float) -- heuristic value total
        # initialRow -- starting row of the first diagonal
        # endColumn -- starting column of the last diagonal
        # startingSquares (array[tuple]) -- starting coordinates for diagonals
        total, initialRow, endColumn = 0, self.criteria - 1, self.size - self.criteria + 1
        startingSquares = [(row, 0) for row in range(initialRow, self.size)] + [(self.size - 1, col) for col in range(1, endColumn)]

        for row, col in startingSquares:

            # diagonal (list) -- a list of diagonal entries
            diagonal = self.getRightDiagonal(row, col)

            total += self.getHeuristicScore(diagonal, turn)

        return total

    def findNeighbourSquares(self):
        """This method finds legal moves on the board which are adjacent to occupied squares."""
        # available (set) -- a set that stores relevant squares for the next move
        available = set()

        for row in range(self.size):

            for col in range(self.size):

                # checks if the current square is occupied
                if self.board[row][col] is not None:

                    # merge the new coordinates with the set
                    available.update(self.getFreeAdjacentSquares(row, col))

        return available

    def getFreeAdjacentSquares(self, row, col):
        """This method retrieves all the empty adjacent squares to board[row][col]."""
        # adj (list) -- holds all the empty adjacent squares to board[row][col]
        adj = set()

        # checks if the row above is still on the board
        if row - 1 >= 0:

            # above (int) -- the index of the row above
            above = row - 1

            # checks if board[row - 1][col - 1] is free
            if col - 1 >= 0 and self.board[above][col - 1] is None:
                adj.add((above, col - 1))

            # checks if board[row - 1][col] is free
            if self.board[above][col] is None:
                adj.add((above, col))

            # checks if board[row - 1][col + 1] is free
            if col + 1 < self.size and self.board[above][col + 1] is None:
                adj.add((above, col + 1))

        # checks if the row below is still on the board
        if row + 1 < self.size:

            # below (int) -- index of the row below
            below = row + 1

            # checks if board[row + 1][col - 1] is free
            if col - 1 >= 0 and self.board[below][col - 1] is None:
                adj.add((below, col - 1))

            # checks if board[row + 1][col] is free
            if self.board[below][col] is None:
                adj.add((below, col))

            # checks if board[row + 1][col + 1] is free
            if col + 1 < self.size and self.board[below][col + 1] is None:
                adj.add((below, col + 1))

        # checks if board[row][col - 1] is free
        if col - 1 >= 0 and self.board[row][col - 1] is None:
            adj.add((row, col - 1))

        # checks if board[row][col + 1] is free
        if col + 1 < self.size and self.board[row][col + 1] is None:
            adj.add((row, col + 1))

        return adj

    def getColumn(self, col):
        """This method places the entries from column board[:][col] into an list with a dummy None entry at the end."""
        column = [None] * (self.size + 1)

        for row in range(self.size):
            column[row] = self.board[row][col]

        return column

    def getLeftDiagonal(self, row, col):
        """This method places the entries along the left-slanted diagonal starting from board[row][col] into an array with a dummy None entry at the end."""
        # n (int) -- number of entries on the diagonal
        n = self.size - max(row, col)
        diagonal = [None] * (n + 1)

        # inc (int) -- different increment to the starting index
        for inc in range(n):
            diagonal[inc] = self.board[row + inc][col + inc]

        return diagonal

    def getRightDiagonal(self, row, col):
        """This method places the entries along the right-slanted diagonal starting from board[row][col] into an array with a dummy None entry at the end."""
        # n (int) -- number of entries on the diagonal
        n = row + 1 if col == 0 else self.size - col
        diagonal = [None] * (n + 1)

        # inc (int) -- increment to the starting index
        for inc in range(n):
            diagonal[inc] = self.board[row - inc][col + inc]

        return diagonal

    def findNextMove(self, turn):
        """This method finds the next decent move to play for the AI player."""
        # if the board is empty, we simply go for the middle position.
        if self.game.isBoardEmpty():

            # the middle square on the board is the best starting move
            row = col = self.size // 2

            # updates board temporarily to find the heuristic score
            self.game.placePiece(row, col, turn)

            # heuristic (float) -- heuristic score of the position
            heuristic = self.overallHeuristicScore("X" if turn == "O" else "O")

            # restores the board after the heuristic score has been calculated
            self.game.undoMove()

            # returns the result to the main game
            return heuristic, row, col

        # if there is a crushing move, play it
        if self.game.selfHasFour():

            # searches for the winning move
            winRow, winCol = self.game.findQuickWin()

            # returns the winning move to the main game
            return 200000000 if turn == "X" else -200000000, winRow, winCol

        # resorts to iterated deepening search
        return self.iteratedDeepeningSearch(turn)

    def iteratedDeepeningSearch(self, turn):
        """This method calls miniMax with increasing depth and stores the results in the cache table."""
        available, alpha, beta, timeLimit = self.findNeighbourSquares(), float("-inf"), float("inf"), 20

        if turn == "X":

            bestHeuristic, bestRow, bestCol, start = alpha, None, None, default_timer()
            for dp in range(1, self.depth + 1):

                currHeuristic, currRow, currCol = self.maxSearch(available, dp, dp, alpha, beta, start)
                if default_timer() - start >= self.timeLimit:
                    break

                bestHeuristic, bestRow, bestCol = currHeuristic, currRow, currCol
                if bestHeuristic >= 400000000:
                    break
        else:

            bestHeuristic, bestRow, bestCol, start = beta, None, None, default_timer()
            for dp in range(1, self.depth + 1):

                currHeuristic, currRow, currCol = self.minSearch(available, dp, dp, alpha, beta, start)
                if default_timer() - start >= self.timeLimit:
                    break

                bestHeuristic, bestRow, bestCol = currHeuristic, currRow, currCol
                if bestHeuristic <= -400000000:
                    break

        return bestHeuristic, bestRow, bestCol

    def maxSearch(self, available, depth, requiredDepth, alpha, beta, start):
        """This method searches the best move for the maximiser."""
        if default_timer() - start >= self.timeLimit:
            return 200000000

        # checks for killer moves
        if depth != requiredDepth and self.game.selfHasFour():

            # saves the killer move
            self.game.table[self.game.hashKey] = (0, None, None, 400000000)

            # returns the heuristic value
            return 400000000

        # checks if the maximum depth has been reached
        if depth == 0:

            # checks if the hashKey is stored in the transposition table and moreover if the keys match
            if self.game.hashKey in self.game.table:

                # return the previously calculated heuristic score
                return self.game.table[self.game.hashKey][3]

            # calculates the heuristic score
            res = self.overallHeuristicScore("X")

            # stores the heuristic score
            self.game.table[self.game.hashKey] = (0, None, None, res)

            # returns the heuristic score
            return res

        # bestHeuristic -- keeps track of the best score for the maximiser
        bestHeuristic, bestRow, bestCol, prevTuple = alpha, None, None, (None, None)

        # checks if the position has been visited before
        if self.game.hashKey in self.game.table:

            prevDepth, prevRow, prevCol, evaluation = self.game.table[self.game.hashKey]

            # makes sure that the previous best move is playable in this position
            if (prevRow, prevCol) in available:

                if prevDepth >= depth:

                    if depth == requiredDepth:
                        return evaluation, prevRow, prevCol

                    else:
                        return evaluation

                prevTuple = (prevRow, prevCol)

                # makes the current move on the board
                self.game.placePiece(prevRow, prevCol, "X")

                # candidate -- all the available moves to play next
                candidate = available.union(self.getFreeAdjacentSquares(prevRow, prevCol))

                # remove the move just played
                candidate.remove(prevTuple)

                # nextHeuristic -- heuristic score obtained from the next deeper level (float)
                nextHeuristic = self.minSearch(candidate, depth - 1, requiredDepth, bestHeuristic, beta, start)

                # undoes the current move on the board
                self.game.undoMove()

                # checks if a better move was found
                if nextHeuristic > bestHeuristic:

                    # replace the best move with the new move
                    bestHeuristic, bestRow, bestCol = nextHeuristic, prevRow, prevCol

        # Search non-principle moves
        for move in available:

            if default_timer() - start >= self.timeLimit:
                break

            if move == prevTuple:
                continue

            # row, col -- current row and column index (int)
            row, col = move

            # makes the current move on the board
            self.game.placePiece(row, col, "X")

            # candidate -- all the available moves to play next
            candidate = available.union(self.getFreeAdjacentSquares(row, col))

            # removes the current square as it is no longer available
            candidate.remove(move)

            # updates bestHeuristic
            nextHeuristic = self.minSearch(candidate, depth - 1, requiredDepth, bestHeuristic, beta, start)

            # undoes the current move on the board
            self.game.undoMove()

            # checks if a better move was found
            if nextHeuristic > bestHeuristic:

                # replace the best move with the new move
                bestHeuristic, bestRow, bestCol = nextHeuristic, row, col

            # if alpha >= beta, prune the game tree
            if beta <= bestHeuristic:
                break

        # stores the result in the transposition table
        if default_timer() - start < self.timeLimit:
            self.game.table[self.game.hashKey] = (depth, bestRow, bestCol, bestHeuristic)

        # returns the result
        if depth == requiredDepth:
            return bestHeuristic, bestRow, bestCol

        else:
            return bestHeuristic

    def minSearch(self, available, depth, requiredDepth, alpha, beta, start):
        """This method searches the best move for the minimiser."""
        if default_timer() - start >= self.timeLimit:
            return -200000000

        if depth != requiredDepth and self.game.selfHasFour():

            # saves the killer move
            self.game.table[self.game.hashKey] = (0, None, None, -400000000)

            # returns the heuristic value
            return -400000000

        # checks if the maximum depth has been reached
        if depth == 0:

            # checks if the hashKey is stored in the transposition table and moreover if the keys match
            if self.game.hashKey in self.game.table:

                # return the previously calculated heuristic score
                return self.game.table[self.game.hashKey][3]

            # calculates the heuristic score
            res = self.overallHeuristicScore("O")

            # stores the heuristic score
            self.game.table[self.game.hashKey] = (0, None, None, res)

            # returns the heuristic score
            return res

        # bestHeuristic -- keeps track of the best score for the maximiser
        bestHeuristic, bestRow, bestCol, prevTuple = beta, None, None, (None, None)

        # checks if the position has been visited before
        if self.game.hashKey in self.game.table:

            prevDepth, prevRow, prevCol, evaluation = self.game.table[self.game.hashKey]

            # makes sure that the previous best move is playable in this position
            if (prevRow, prevCol) in available:

                if prevDepth >= depth:

                    if depth == requiredDepth:
                        return evaluation, prevRow, prevCol

                    else:
                        return evaluation

                prevTuple = (prevRow, prevCol)

                # makes the current move on the board
                self.game.placePiece(prevRow, prevCol, "O")

                # candidate -- all the available moves to play next
                candidate = available.union(self.getFreeAdjacentSquares(prevRow, prevCol))

                # removes the move which we just made
                candidate.remove(prevTuple)

                # nextHeuristic -- heuristic score obtained from the next deeper level (float)
                nextHeuristic = self.maxSearch(candidate, depth - 1, requiredDepth, alpha, bestHeuristic, start)

                # undoes the current move on the board
                self.game.undoMove()

                # checks if a better move was found
                if nextHeuristic < bestHeuristic:

                    # replace the best move with the new move
                    bestHeuristic, bestRow, bestCol = nextHeuristic, prevRow, prevCol

        for move in available:

            if default_timer() - start >= self.timeLimit:
                break

            if move == prevTuple:
                continue

            row, col = move

            # makes the current move on the board
            self.game.placePiece(row, col, "O")

            # candidate -- all the available moves to play next
            candidate = available.union(self.getFreeAdjacentSquares(row, col))

            # removes the current square as it is no longer available
            candidate.remove(move)

            # updates bestHeuristic
            nextHeuristic = self.maxSearch(candidate, depth - 1, requiredDepth, alpha, bestHeuristic, start)

            # undoes the current move on the board
            self.game.undoMove()

            # checks if a better move was found
            if nextHeuristic < bestHeuristic:

                # replace the best move with the new move
                bestHeuristic, bestRow, bestCol = nextHeuristic, row, col

            # if beta <= alpha, prune the game tree
            if bestHeuristic <= alpha:
                break

        # stores the result in the transposition table
        if default_timer() - start < self.timeLimit:
            self.game.table[self.game.hashKey] = (depth, bestRow, bestCol, bestHeuristic)

        # returns the result
        if depth == requiredDepth:
            return bestHeuristic, bestRow, bestCol

        else:
            return bestHeuristic


# initialises a game of Gomoku
if __name__ == "__main__":

    # dimension (int) -- size of the board
    # searchDepth (int) -- depth of AI's search for a move
    # timeCap (int) -- time limit for A.I's search
    dimension, searchDepth, timeCap = 15, 4, 15
    gameBoard = ConnectFiveBoard(dimension)
    gameEngine = ConnectFiveEngine(gameBoard, searchDepth, timeCap)
    gameBoard.prettyPrint()

    # continues the game until a player has won
    while True:

        # prompts user to enter move
        print("\nIt's your turn to move.")

        def promptUser(message):
            prompt = True
            while prompt:
                try:
                    userInput = input(message)
                    if not userInput.isdigit():
                        raise ValueError
                    userInput = int(userInput)
                    return userInput
                except ValueError:
                    print("Invalid entry! Try again!\n")

        # validMove -- whether the user's move is valid (bool)
        validMove = False

        # checks if the user has made a valid move
        while not validMove:

            # r, c -- row, col
            r = promptUser("Enter row number (any integer between 0 and {}): ".format(dimension - 1))
            c = promptUser("Enter col number (any integer between 0 and {}): ".format(dimension - 1))

            # makes user's move on the board
            if not gameBoard.userPlacePiece(r, c, "X"):
                print("Invalid move! Try again!\n")
            else:
                validMove = True

        # checks the board for winning streaks
        if gameBoard.hasWinner():
            gameBoard.prettyPrint()
            print("\nCongrats! You have beat the computer!")
            break

        # checks the board draw
        if gameBoard.isBoardFull():
            gameBoard.prettyPrint()
            print("\nGame Over! The board is full and a draw has been declared!")
            break

        # computer searches for move at depth 4
        _, r, c = gameEngine.findNextMove("O")

        # computer plays the move
        gameBoard.placePiece(r, c, "O")

        # checks the board for winning streaks
        if gameBoard.hasWinner():
            gameBoard.prettyPrint()
            print("\nThe computer plays ({}, {})!!!".format(r, c))
            print("\nGame Over! The computer has won!")
            break

        # checks the board draw
        if gameBoard.isBoardFull():
            gameBoard.prettyPrint()
            print("\nGame Over! The board is full and a draw has been declared!")
            break

        # prints the board for user to see
        gameBoard.prettyPrint()
        print("\nThe computer plays ({}, {})!!!".format(r, c))
