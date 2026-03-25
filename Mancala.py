"""
TODO: Make minimax algorithm hunt typically better moves first & search them deeper (ex. moves where you can play again or capture)
TODO: Optimization! Parallelism?
TODO: Color pits that have recently changed
TODO: Add a print when capturing occurs? OR otherwise visually represent it
"""

import random
import time
from copy import deepcopy
from colorama import init, Fore, Style
init()

# prints the board fancily
def printBoard(slots, perspective):
    cellWidth = max(2, len(str(max(slots))))
    indent = 6

    def formatRow(row):
        return " ".join(f"{slots[i]:>{cellWidth}}" for i in row)
        # return " ".join(f"{i:>{cellWidth}}" for i in row)

    if perspective == 1:
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
    print(" " * indent + Fore.LIGHTYELLOW_EX + topStr + Style.RESET_ALL)
    print(" " * (indent-2) + Fore.YELLOW + leftGoalStr + (" " * innerSpace) + Fore.BLUE + rightGoalStr + Style.RESET_ALL)
    print(" " * indent + Fore.LIGHTBLUE_EX + botStr + Style.RESET_ALL)
    print(" " * labelPad + botLabel)
    print()


# converts a relative index [1-6] to an absolute index [0-13], given the player
def convertRelativeIndex(index, perspective):
    if not 0 < index < 7:
        print("Enter a valid slot index [1-6]")
        return None
    row = range(1, 7) if perspective == 1 else range(8, 14)
    return row[index-1]


# returns whether the game is over or not, and which side needs to be cleared of remaining marbles
def isGameOver(slots):
    for i in range(1, 7):
        if slots[i] > 0:
            for j in range(8, 14):
                if slots[j] > 0:
                    return False, -1
            return True, 2
    return True, 1


# returns a list of all legal moves given a board state
def getPlayableMoves(slots, perspective):
    row = range(1, 7) if perspective == 1 else range(8, 14)
    return [k + 1 for k, i in enumerate(row) if slots[i] > 0]


# returns if the player can play again (T/F), if the game is over
def move(slots, index, perspective):
    if slots[index] == 0:
        print("You can't move an empty slot!")
        return True, False

    marbles = slots[index]
    slots[index] = 0
    s = index

    while marbles > 0:
        s = (s + 1) % 14
        if (perspective == 1 and s == 0) or (perspective == 2 and s == 7):
            continue
        slots[s] += 1
        marbles -= 1

    playAgain = s in [0, 7]

    if not playAgain and slots[s] == 1 and slots[14-s] > 0: # capture if lands in empty slot and opposite slot has marbles
        if perspective == 1 and 0 < s < 7:
            slots[7] += slots[s] + slots[14-s]
            slots[s] = 0
            slots[14-s] = 0
            # print("Captured!")
        elif perspective == 2 and 7 < s < 14:
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


# returns estimated score of a board state
def evaluate(slots, perspective):
    score = (slots[7] - slots[0]) if perspective == 1 else (slots[0] - slots[7])

    p1_side = sum(slots[1:7])
    p2_side = sum(slots[8:14])
    side_adv = (p1_side - p2_side) if perspective == 1 else (p2_side - p1_side)

    return 3 * score + side_adv


# returns the minimax value of a board
def miniMax(slots, turn, perspective, depth=8, alpha=-999, beta=999):
    if depth == 0:
        return evaluate(slots, perspective)

    moves = getPlayableMoves(slots, turn)
    if not moves:
        return evaluate(slots, perspective)

    if turn == perspective: # maximizing player
        bestScore = -999

        for m in moves:
            copy = deepcopy(slots)
            playAgain, gameOver = move(copy, convertRelativeIndex(m, turn), turn)
            nextTurn = turn if playAgain and not gameOver else (2 if turn == 1 else 1)

            if gameOver:
                score = (copy[7] - copy[0]) if perspective == 1 else (copy[0] - copy[7])
            else:
                score = miniMax(copy, nextTurn, perspective, depth - 1, alpha, beta)

            bestScore = max(bestScore, score)
            alpha = max(alpha, bestScore)

            if alpha >= beta:
                break  # prune

        return bestScore

    else: # minimizing player
        bestScore = 999

        for m in moves:
            copy = deepcopy(slots)
            playAgain, gameOver = move(copy, convertRelativeIndex(m, turn), turn)
            nextTurn = turn if playAgain and not gameOver else (2 if turn == 1 else 1)

            if gameOver:
                score = (copy[7] - copy[0]) if perspective == 1 else (copy[0] - copy[7])
            else:
                score = miniMax(copy, nextTurn, perspective, depth - 1, alpha, beta)

            bestScore = min(bestScore, score)
            beta = min(beta, bestScore)

            if alpha >= beta:
                break  # prune

        return bestScore


# picks the best move of a board state using miniMax
def pickMove(slots, perspective, depth=8):
    start_time = time.perf_counter()

    bestMove = -1
    bestScore = -999
    alpha = -999
    beta = 999

    for m in getPlayableMoves(slots, perspective):
        copy = deepcopy(slots)
        playAgain, gameOver = move(copy, convertRelativeIndex(m, perspective), perspective)

        if gameOver:
            score = copy[7] - copy[0] if perspective == 1 else copy[0] - copy[7]
        else:
            nextTurn = perspective if playAgain else (2 if perspective == 1 else 1)
            score = miniMax(copy, nextTurn, perspective, depth, alpha=alpha, beta=beta)

        if score > bestScore:
            bestScore = score
            bestMove = m

        alpha = max(alpha, bestScore)

    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    print(f"Execution time: {elapsed_time:.4f} seconds")

    return bestMove



print(f"{Fore.LIGHTGREEN_EX}Starting game of Mancala{Style.RESET_ALL}")

help = f"\n           {Fore.LIGHTWHITE_EX}MY SIDE{Style.RESET_ALL}\n       {Fore.LIGHTYELLOW_EX}6  5  4  3  2  1\n{Fore.YELLOW}Mine>X                  {Fore.BLUE}X<Yours\n       {Fore.LIGHTBLUE_EX}1  2  3  4  5  6\n          {Fore.LIGHTWHITE_EX}YOUR SIDE\n{Style.RESET_ALL}"
print(f"{Fore.GREEN}Help board (type \"help\" at any point to return to it.){Style.RESET_ALL}")
print(help)
print(f"{Fore.GREEN}When asked for an index, respond with a number 1-6 corresponding to the shown slots on the Mancala board{Style.RESET_ALL}")

player = input(f"{Fore.LIGHTWHITE_EX}Do you want to play first? (y/n): {Style.RESET_ALL}")
while not player in ["y", "n"]:
    player = input("Do you want to play first? (y/n): ")

if player == "y":
    player = 1
    bot = 2
else:
    player = 2
    bot = 1

print(f"{Fore.GREEN}Player = P{player}, Bot = P{bot}{Style.RESET_ALL}")

slots = [4] * 14
slots[0] = 0 # p2 goal
slots[7] = 0 # p1 goal

turn = 1

printBoard(slots, player)

gameOver = False

while not gameOver:
    print(f"{Fore.GREEN}It is player {turn}'s turn.{Style.RESET_ALL}")
    if turn == player:
        canPlay = True
        while canPlay and not gameOver:
            moveIndex = -1
            while not moveIndex in range(1, 14):
                userInput = input(f"{Fore.LIGHTWHITE_EX}Which slot do you want to move? {Style.RESET_ALL}")
                while not userInput in ["1", "2", "3", "4", "5", "6", "help", "hint"]:
                    userInput = input(f"{Fore.LIGHTWHITE_EX}Which slot do you want to move? {Style.RESET_ALL}")
                if userInput == "hint":
                    hint = pickMove(slots, player)
                    print(f"{Fore.LIGHTYELLOW_EX}Best slot to move is: {hint}{Style.RESET_ALL}")
                elif userInput == "help":
                    print(help)
                else:
                    moveIndex = convertRelativeIndex(int(userInput), turn)
            canPlay, gameOver = move(slots, moveIndex, turn)
            printBoard(slots, player)
    else:
        canPlay = True
        while canPlay and not gameOver:
            moveIndex = -1
            while not moveIndex in range(1, 14):
                # relativeIndex = random.randint(1, 6) # is inclusive for some reason
                relativeIndex = pickMove(slots, bot)
                moveIndex = convertRelativeIndex(relativeIndex, turn)
                num = slots[moveIndex]
                plural = "s" if num > 1 else ""
                print(f"{Fore.LIGHTYELLOW_EX}> I want to move the {num} marble{plural} in my slot #{relativeIndex}!{Style.RESET_ALL}")
            canPlay, gameOver = move(slots, moveIndex, turn)
            printBoard(slots, player)

    print(f"{Fore.GREEN}Player {turn}'s turn is over.{Style.RESET_ALL}")

    if not gameOver:
        turn = 2 if turn == 1 else 1


print(f"{Fore.LIGHTGREEN_EX}Game is over!{Style.RESET_ALL}")
print(f"{Fore.GREEN}Score: {Fore.LIGHTBLUE_EX}{slots[7]}{Style.RESET_ALL}-{Fore.LIGHTYELLOW_EX}{slots[0]}{Style.RESET_ALL}")
if slots[0] == slots[7]:
    print("It was a tie!")
else:
    print(f"{Fore.LIGHTGREEN_EX}Player {1 if slots[7] > slots[0] else 2} wins!{Style.RESET_ALL}")
