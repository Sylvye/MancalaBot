"""
TODO: Make minimax algorithm hunt typically better moves first & search them deeper. (ex. moves where you can play again or capture)
TODO: optimization! parallelism?
"""

import random
import time
from copy import deepcopy

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def printBoard(slots, player):
    cellWidth = max(2, len(str(max(slots))))
    indent = 6

    def formatRow(row):
        return " ".join(f"{slots[i]:>{cellWidth}}" for i in row)
        # return " ".join(f"{i:>{cellWidth}}" for i in row)

    if player == 1:
        topRow = range(13, 7, -1)
        botRow = range(1, 7)
        leftGoal = 0
        rightGoal = 7
        topLabel = "P2"
        botLabel = "P1"
    else:
        topRow = range(6, 0, -1)
        botRow = range(8, 14)
        leftGoal = 7
        rightGoal = 0
        topLabel = "P1"
        botLabel = "P2"

    topStr = formatRow(topRow)
    botStr = formatRow(botRow)

    leftGoalStr = f"{slots[leftGoal]:>{cellWidth}}"
    rightGoalStr = f"{slots[rightGoal]:>{cellWidth}}"

    innerSpace = len(topStr) - len(leftGoalStr) - len(rightGoalStr) + 4
    if innerSpace < 1:
        innerSpace = 1

    labelPad = indent + max(0, (len(topStr) - len(topLabel)) // 2)

    print()
    print(" " * labelPad + topLabel)
    print(" " * indent + topStr)
    print(" " * (indent-2) + leftGoalStr + (" " * innerSpace) + rightGoalStr)
    print(" " * indent + botStr)
    print(" " * labelPad + botLabel)
    print()


def convertRelativeIndex(index, player):
    if not 0 < index < 7:
        print("Enter a valid slot index [1-6]")
        return None
    row = range(1, 7) if player == 1 else range(8, 14)
    return row[index-1]


def isGameOver(slots):
    for i in range(1, 7):
        if slots[i] > 0:
            for j in range(8, 14):
                if slots[j] > 0:
                    return False, -1
            return True, 2
    return True, 1


def getPlayableMoves(slots, turn):
    row = range(1, 7) if turn == 1 else range(8, 14)
    return [k + 1 for k, i in enumerate(row) if slots[i] > 0]


# returns if the player can play again (T/F), if the game is over
def move(slots, index, player):
    if slots[index] == 0:
        print("You can't move an empty slot!")
        return True, False

    marbles = slots[index]
    slots[index] = 0
    s = index

    while marbles > 0:
        s = (s + 1) % 14
        if (player == 1 and s == 0) or (player == 2 and s == 7):
            continue
        slots[s] += 1
        marbles -= 1

    playAgain = s in [0, 7]

    if not playAgain and slots[s] == 1 and slots[14-s] > 0: # capture if lands in empty slot and opposite slot has marbles
        if player == 1 and 0 < s < 7:
            slots[7] += slots[s] + slots[14-s]
            slots[s] = 0
            slots[14-s] = 0
            # print("Captured!")
        elif player == 2 and 7 < s < 14:
            slots[0] += slots[s] + slots[14-s]
            slots[s] = 0
            slots[14-s] = 0
            # print("Captured!")

    gameOver, empty = isGameOver(slots)
    if gameOver:  # when one side runs out, claims all remaining marbles for the other side
        if empty == 1:
            for j in range(8, 14):
                slots[0] += slots[j]
                slots[j] = 0
        else:
            for j in range(1, 7):
                slots[7] += slots[j]
                slots[j] = 0

    return playAgain, gameOver


def evaluate(slots, playAs):
    score = (slots[7] - slots[0]) if playAs == 1 else (slots[0] - slots[7])

    p1_side = sum(slots[1:7])
    p2_side = sum(slots[8:14])
    side_adv = (p1_side - p2_side) if playAs == 1 else (p2_side - p1_side)

    return 3 * score + side_adv


def miniMax(slots, turn, playAs, depth=8, alpha=-999, beta=999):
    if depth == 0:
        return evaluate(slots, playAs)

    moves = getPlayableMoves(slots, turn)
    if not moves:
        return evaluate(slots, playAs)

    if turn == playAs:  # maximizing player
        bestScore = -999

        for m in moves:
            copy = deepcopy(slots)
            playAgain, gameOver = move(copy, convertRelativeIndex(m, turn), turn)
            nextTurn = turn if playAgain and not gameOver else (2 if turn == 1 else 1)

            if gameOver:
                score = (copy[7] - copy[0]) if playAs == 1 else (copy[0] - copy[7])
            else:
                score = miniMax(copy, nextTurn, playAs, depth - 1, alpha, beta)

            bestScore = max(bestScore, score)
            alpha = max(alpha, bestScore)

            if alpha >= beta:
                break  # prune

        return bestScore

    else:  # minimizing player
        bestScore = 999

        for m in moves:
            copy = deepcopy(slots)
            playAgain, gameOver = move(copy, convertRelativeIndex(m, turn), turn)
            nextTurn = turn if playAgain and not gameOver else (2 if turn == 1 else 1)

            if gameOver:
                score = (copy[7] - copy[0]) if playAs == 1 else (copy[0] - copy[7])
            else:
                score = miniMax(copy, nextTurn, playAs, depth - 1, alpha, beta)

            bestScore = min(bestScore, score)
            beta = min(beta, bestScore)

            if alpha >= beta:
                break  # prune

        return bestScore


def pickMove(slots, turn, playAs):
    start_time = time.perf_counter()

    bestMove = -1
    bestScore = -999
    alpha = -999
    beta = 999

    for m in getPlayableMoves(slots, turn):
        copy = deepcopy(slots)
        playAgain, gameOver = move(copy, convertRelativeIndex(m, turn), turn)

        if gameOver:
            score = copy[7] - copy[0] if playAs == 1 else copy[0] - copy[7]
        else:
            nextTurn = turn if playAgain else (2 if turn == 1 else 1)
            score = miniMax(copy, nextTurn, playAs, depth=8, alpha=alpha, beta=beta)

        if score > bestScore:
            bestScore = score
            bestMove = m

        alpha = max(alpha, bestScore)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Execution time: {elapsed_time:.4f} seconds")

    return bestMove



print("Starting game of Mancala")

help = "\n           MY SIDE\n       6  5  4  3  2  1\nMine>X                  X<Yours\n       1  2  3  4  5  6\n          YOUR SIDE\n"
print("Help board (type \"help\" at any point to return to it.")
print(help)
print("When asked for an index, respond with a number 1-6 corresponding to the shown slots on the Mancala board")

player = input("Do you want to play first? (y/n): ")
while not player in ["y", "n"]:
    player = input("Do you want to play first? (y/n): ")

if player == "y":
    player = 1
    bot = 2
else:
    player = 2
    bot = 1

print(f"Player = P{player}, Bot = P{bot}")

slots = [4] * 14
slots[0] = 0 # p2 goal
slots[7] = 0 # p1 goal

turn = 1

printBoard(slots, player)

gameOver = False

while not gameOver:
    print(f"It is player {turn}'s turn")
    if turn == player:
        canPlay = True
        while canPlay and not gameOver:
            moveIndex = -1
            while not moveIndex in range(1, 14):
                userInput = input("Which slot do you want to move? ")
                while not userInput in ["1", "2", "3", "4", "5", "6", "help", "hint"]:
                    userInput = input("Which slot do you want to move? ")
                if userInput == "hint":
                    hint = pickMove(slots, turn, player)
                    print(f"Best slot to move is: {hint}")
                elif userInput == "help":
                    print(help)
                if is_int(userInput):
                    moveIndex = convertRelativeIndex(int(userInput), turn)
            canPlay, gameOver = move(slots, moveIndex, turn)
            printBoard(slots, player)
    else:
        canPlay = True
        while canPlay and not gameOver:
            moveIndex = -1
            while not moveIndex in range(1, 14):
                # relativeIndex = random.randint(1, 6) # is inclusive for some reason
                userInput = pickMove(slots, turn, bot)
                print(f"> I want to move the marble in my slot #{userInput}!")
                moveIndex = convertRelativeIndex(userInput, turn)
            canPlay, gameOver = move(slots, moveIndex, turn)
            printBoard(slots, player)

    print(f"Player {turn}'s turn is over")

    if not gameOver:
        turn = 2 if turn == 1 else 1


print("Game is over!")
print(f"Score: {slots[7]}-{slots[0]}")
if slots[0] == slots[7]:
    print("It was a tie!")
else:
    print(f"Player {1 if slots[7] > slots[0] else 2} wins!")
