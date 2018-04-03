#
#   CS6613 Artificial Intelligence
#   Project 1 Mini-Checkers Game
#   Shang-Hung Tsai
#

import copy
import math

class AIPlayer():
    def __init__(self, game, difficulty):
        self.game = game
        self.difficulty = difficulty
        if self.difficulty == 3:
            self.depthLimit = 15

    def getNextMove(self):
        if self.difficulty == 1:
            return self.getNextMoveEasy()
        elif self.difficulty == 3:
            return self.getNextMoveHard()

    # Simple AI, returns the first found legal move
    def getNextMoveEasy(self):
        directions = [[1, -1], [1, 1], [2, -2], [2, 2]]
        for checker in self.game.opponentCheckers:
            position = self.game.checkerPositions[checker]
            print("Current checker: " + str(position))
            row = position[0]
            col = position[1]
            for dir in directions:
                print(str(row + dir[0]) + " " + str(col + dir[1]))
                if self.game.isValidMove(row, col, row + dir[0], col + dir[1], False):
                    print("----------------")

                    return row, col, row + dir[0], col + dir[1]

    # Hard AI, returns the best move found by alpha-beta search
    def getNextMoveHard(self):
        state = AIGameState(self.game)
        nextMove = self.alphaBetaSearch(state)
        return nextMove[0], nextMove[1], nextMove[2], nextMove[3]

    def alphaBetaSearch(self, state):
        self.numNodes = 0
        self.bestMove = []
        v = self.maxValue(state, -1000, 1000, self.depthLimit)
        print("selected value " + str(v))
        print(self.numNodes)
        return self.bestMove

    # For AI player (MAX)
    def maxValue(self, state, alpha, beta, depthLimit):
        self.numNodes += 1
        if state.terminalTest():
            return state.computeUtilityValue()
        if depthLimit < 0:
            return state.computeHeuristic()
        v = -math.inf
        for a in state.getActions(False):
            # return captured checker if it is a capture move
            captured = state.applyAction(a)
            # state.printBoard()
            if state.humanCanContinue():
                next = self.minValue(state, alpha, beta, depthLimit - 1)
            else:  # human cannot move, AI gets one more move
                next = self.maxValue(state, alpha, beta, depthLimit - 1)
            if next > v:
                v = next
                # Keep track of the best move so far at the top level
                if depthLimit == self.depthLimit:
                    self.bestMove = a
            state.resetAction(a, captured)
            # alpha-beta pruning
            if v >= beta:
                return v
            alpha = max(alpha, v)
        return v

    # For human player (MIN)
    def minValue(self, state, alpha, beta, depthLimit):
        self.numNodes += 1
        if state.terminalTest():
            return state.computeUtilityValue()
        if depthLimit < 0:
            return state.computeHeuristic()
        v = math.inf
        for a in state.getActions(True):
            captured = state.applyAction(a)
            # state.printBoard()
            if state.AICanContinue():
                next = self.maxValue(state, alpha, beta, depthLimit - 1)
            else:  # AI cannot move, human gets one more move
                next = self.minValue(state, alpha, beta, depthLimit - 1)
            if next < v:
                v = next
            state.resetAction(a, captured)

            #alpha-beta pruning
            if v <= alpha:
                return v
            beta = min(beta, v)
        return v

# a class for AI to simulate game state
class AIGameState():
    def __init__(self, game):
        self.board = copy.deepcopy(game.getBoard())

        self.AICheckers = set()
        for checker in game.opponentCheckers:
            self.AICheckers.add(checker)
        self.humanCheckers = set()
        for checker in game.playerCheckers:
            self.humanCheckers.add(checker)
        self.checkerPositions = {}
        for checker, position in game.checkerPositions.items():
            self.checkerPositions[checker] = position

    # Check if the human player can cantinue.
    def humanCanContinue(self):
        directions = [[-1, -1], [-1, 1], [-2, -2], [-2, 2]]
        for checker in self.humanCheckers:
            position = self.checkerPositions[checker]
            row = position[0]
            col = position[1]
            for dir in directions:
                if self.isValidMove(row, col, row + dir[0], col + dir[1], True):
                    return True
        return False

    # Check if the AI player can cantinue.
    def AICanContinue(self):
        directions = [[1, -1], [1, 1], [2, -2], [2, 2]]
        for checker in self.AICheckers:
            position = self.checkerPositions[checker]
            row = position[0]
            col = position[1]
            for dir in directions:
                if self.isValidMove(row, col, row + dir[0], col + dir[1], False):
                    return True
        return False

    # Neither player can can continue, thus game over
    def terminalTest(self):
        if len(self.humanCheckers) == 0 or len(self.AICheckers) == 0:
            return True
        else:
            return (not self.AICanContinue()) and (not self.humanCanContinue())

    # Check if current move is valid
    def isValidMove(self, oldrow, oldcol, row, col, humanTurn):
        # invalid index
        if oldrow < 0 or oldrow > 5 or oldcol < 0 or oldcol > 5 \
                or row < 0 or row > 5 or col < 0 or col > 5:
            return False
        # No checker exists in original position
        if self.board[oldrow][oldcol] == 0:
            return False
        # Another checker exists in destination position
        if self.board[row][col] != 0:
            return False

        # human player's turn
        if humanTurn:
            if row - oldrow == -1:   # regular move
                return abs(col - oldcol) == 1
            elif row - oldrow == -2:  # capture move
                #  \ direction or / direction
                return (col - oldcol == -2 and self.board[row+1][col+1] < 0) \
                       or (col - oldcol == 2 and self.board[row+1][col-1] < 0)
            else:
                return False
        # opponent's turn
        else:
            if row - oldrow == 1:   # regular move
                return abs(col - oldcol) == 1
            elif row - oldrow == 2: # capture move
                # / direction or \ direction
                return (col - oldcol == -2 and self.board[row-1][col+1] > 0) \
                       or (col - oldcol == 2 and self.board[row-1][col-1] > 0)
            else:
                return False

    # compute utility value of terminal state
    # utility value = difference in # of checkers * 500 + # of AI checkers * 50
    def computeUtilityValue(self):
        utility = (len(self.AICheckers) - len(self.humanCheckers)) * 500 \
                  + len(self.AICheckers) * 50
        print("Utility value = {0:d} :: {1:d} AI vs {2:d} Human".format(utility, len(self.AICheckers), len(self.humanCheckers)))
        return utility

    def computeHeuristic(self):
        heurisitc = (len(self.AICheckers) - len(self.humanCheckers)) * 50 \
                    + self.countSafeAICheckers() * 10 + len(self.AICheckers)
        print("Heuristic value = {0:d} :: {1:d} AI vs {2:d} Human".format(heurisitc, len(self.AICheckers), len(self.humanCheckers)))
        return heurisitc


    # Count the number of safe AI checker.
    # A safe AI checker is one checker that no opponent can capture.
    def countSafeAICheckers(self):
        count = 0
        for AIchecker in self.AICheckers:
            AIrow = self.checkerPositions[AIchecker][0]
            safe = True
            for humanchecker in self.humanCheckers:
                if AIrow < self.checkerPositions[humanchecker][0]:
                    safe = False
                    break
            if safe:
                count += 1
        return count

    # get all possible actions for the current player
    def getActions(self, humanTurn):
        if humanTurn:
            checkers = self.humanCheckers
            # directions = [[-1, -1], [-1, 1], [-2, -2], [-2, 2]]
            regularDirs = [[-1, -1], [-1, 1]]
            captureDirs = [[-2, -2], [-2, 2]]
        else:
            checkers = self.AICheckers
            # directions = [[1, -1], [1, 1], [2, -2], [2, 2]]
            regularDirs = [[1, -1], [1, 1]]
            captureDirs = [[2, -2], [2, 2]]

        regularMoves = []
        captureMoves = []
        for checker in checkers:
            oldrow = self.checkerPositions[checker][0]
            oldcol = self.checkerPositions[checker][1]
            for dir in regularDirs:
                if self.isValidMove(oldrow, oldcol, oldrow+dir[0], oldcol+dir[1], humanTurn):
                    regularMoves.append([oldrow, oldcol, oldrow+dir[0], oldcol+dir[1]])
            for dir in captureDirs:
                if self.isValidMove(oldrow, oldcol, oldrow+dir[0], oldcol+dir[1], humanTurn):
                    captureMoves.append([oldrow, oldcol, oldrow+dir[0], oldcol+dir[1]])

        # must take capture move if possible
        if captureMoves:
            return captureMoves
        else:
            return regularMoves

    # Apply given action to the game board.
    # :param action: [oldrow, oldcol, newrow, newcol]
    # :return: the label of the captured checker. 0 if none.
    def applyAction(self, action):
        oldrow = action[0]
        oldcol = action[1]
        row = action[2]
        col = action[3]
        captured = 0

        # move the checker
        toMove = self.board[oldrow][oldcol]
        self.checkerPositions[toMove] = (row, col)
        self.board[row][col] = toMove
        self.board[oldrow][oldcol] = 0

        # capture move, remove captured checker
        if abs(oldrow - row) == 2:
            captured = self.board[(oldrow + row) // 2][(oldcol + col) // 2]
            if captured > 0:
                self.humanCheckers.remove(captured)
            else:
                self.AICheckers.remove(captured)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = 0
            self.checkerPositions.pop(captured, None)

        return captured

    # Reset given action to the game board. Restored captured checker if any.
    # :param action: [oldrow, oldcol, newrow, newcol]
    # :return: the label of the captured checker. 0 if none.
    def resetAction(self, action, captured):
        oldrow = action[0]
        oldcol = action[1]
        row = action[2]
        col = action[3]

        # move the checker
        toMove = self.board[row][col]
        self.checkerPositions[toMove] = (oldrow, oldcol)
        self.board[oldrow][oldcol] = toMove
        self.board[row][col] = 0

        # capture move, remove captured checker
        if abs(oldrow - row) == 2:
            if captured > 0:
                self.humanCheckers.add(captured)
            else:
                self.AICheckers.add(captured)
            self.board[(oldrow + row) // 2][(oldcol + col) // 2] = captured
            self.checkerPositions[captured] = ((oldrow + row) // 2, (oldcol + col) // 2)

    def printBoard(self):
        for i in range(len(self.board)):
            for j in range(len(self.board[i])):
                check = self.board[i][j]
                if (check < 0):
                    print(check,end=' ')
                else:
                    print(' ' + str(check),end=' ')

            print()
        print('------------------------')
