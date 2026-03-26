"""
TODO: Make minimax algorithm hunt typically better moves first & search them deeper (ex. moves where you can play again or capture)
TODO: Optimization! Parallelism?
TODO: Add a print when capturing occurs? OR otherwise visually represent it
TODO: Add some way to type a command before the game begins (if you are P2)
"""

import random
import time
from copy import deepcopy
from colorama import init, Fore, Style
init()

# prints the board fancily
from colorama import Fore, Style

def printBoard(slots, perspective, lastSlots=None):
    cellWidth = max(2, len(str(max(slots))))
    indent = 6

    def colorSlot(i):
        changed = lastSlots is not None and slots[i] != lastSlots[i]

        if i in topRow or i == leftGoal:
            base = Fore.LIGHTYELLOW_EX
        else:
            base = Fore.LIGHTBLUE_EX

        return (Style.BRIGHT + base) if changed else base

    def formatCell(i):
        return f"{colorSlot(i)}{slots[i]:>{cellWidth}}{Style.RESET_ALL}"

    def formatRow(row):
        return " ".join(formatCell(i) for i in row)

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

    leftGoalStr = formatCell(leftGoal)
    rightGoalStr = formatCell(rightGoal)

    # Visible width should ignore ANSI escape codes, so use plain text widths
    plainTopStr = " ".join(f"{slots[i]:>{cellWidth}}" for i in topRow)
    plainLeftGoalStr = f"{slots[leftGoal]:>{cellWidth}}"
    plainRightGoalStr = f"{slots[rightGoal]:>{cellWidth}}"

    innerSpace = len(plainTopStr) - len(plainLeftGoalStr) - len(plainRightGoalStr) + 4
    if innerSpace < 1:
        innerSpace = 1

    labelPad = indent + max(0, (len(plainTopStr) - len(topLabel)) // 2)

    print()
    print(" " * labelPad + topLabel)
    print(" " * indent + topStr)
    print(" " * (indent - 2) + leftGoalStr + (" " * innerSpace) + rightGoalStr)
    print(" " * indent + botStr)
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
        print(f"{Fore.LIGHTRED_EX}You can't move an empty slot!{Style.RESET_ALL}")
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


print(f"{Fore.GREEN}Starting game of Mancala{Style.RESET_ALL}")

help = (f"Help board (type \"help\" at any point to return to it.)\n" +
        f"\n           {Fore.LIGHTWHITE_EX}MY SIDE{Style.RESET_ALL}" +
        f"\n       {Fore.LIGHTYELLOW_EX}6  5  4  3  2  1" +
        f"\n{Fore.LIGHTYELLOW_EX}Mine>X                  {Fore.LIGHTBLUE_EX}X<Yours{Style.RESET_ALL}" +
        f"\n       {Fore.LIGHTBLUE_EX}1  2  3  4  5  6" +
        f"\n          {Fore.LIGHTWHITE_EX}YOUR SIDE{Style.RESET_ALL}" +
        f"\n"
)
commands = (
        f"\n{Fore.LIGHTGREEN_EX}Commands:{Style.RESET_ALL}" +
        f"\n- {Fore.GREEN}\"help\"{Style.RESET_ALL} - Prints the help message" +
        f"\n- {Fore.GREEN}\"list\"{Style.RESET_ALL} - Prints this command list" +
        f"\n- {Fore.GREEN}\"board\"{Style.RESET_ALL} - Re-prints the current board" +
        f"\n- {Fore.LIGHTYELLOW_EX}\"hint\"{Style.RESET_ALL} - The algorithm hints the player with what it thinks is the best move" +
        f"\n- {Fore.LIGHTMAGENTA_EX}\"depth\"{Style.RESET_ALL} - Changes the maximum depth of the algorithm" +
        f"\n"
)
print(help)
print(f"Enter command: {Fore.GREEN}\"list\"{Style.RESET_ALL} to get a list of helpful commands")

player = input(f"{Fore.LIGHTWHITE_EX}Do you want to play first? (y/n): {Style.RESET_ALL}")
while not player in ["y", "n"]:
    player = input("Do you want to play first? (y/n): ")

if player == "y":
    player = 1
    bot = 2
else:
    player = 2
    bot = 1

print(f"{Fore.LIGHTBLUE_EX}Player = P{player}{Style.RESET_ALL}, {Fore.LIGHTYELLOW_EX}Bot = P{bot}{Style.RESET_ALL}")

slots = [4] * 14
slots[0] = 0 # p2 goal
slots[7] = 0 # p1 goal
lastSlots = deepcopy(slots)

depth = 8

turn = 1

printBoard(slots, player)

gameOver = False

while not gameOver:
    print(f"It is {Fore.LIGHTBLUE_EX if turn == player else Fore.LIGHTYELLOW_EX}P{turn}{Style.RESET_ALL}'s turn.")
    startScores = [slots[7],slots[0]]
    if turn == player:
        canPlay = True
        while canPlay and not gameOver:
            moveIndex = -1
            userInput = None
            while not moveIndex in range(1, 14):
                userInput = None
                while not userInput in ["1", "2", "3", "4", "5", "6", "help", "list", "hint", "depth", "board"]:
                    if userInput is not None:
                        print(f"{Fore.LIGHTRED_EX}Not a valid command{Style.RESET_ALL}")
                    userInput = input(f"{Fore.LIGHTWHITE_EX}Enter a slot number or a command: {Style.RESET_ALL}")
                if userInput == "hint":
                    hint = pickMove(slots, player, depth=depth)
                    print(f"{Fore.LIGHTYELLOW_EX}> I think that the best slot to move is: {hint}{Style.RESET_ALL}")
                elif userInput == "depth":
                    print(f"Current depth: {Fore.LIGHTMAGENTA_EX}{depth}{Style.RESET_ALL}")
                    userInput = None
                    while not userInput in [str(n) for n in range(1, 11)]: # 1 = min depth, 10 = max
                        userInput = input(f"{Fore.LIGHTWHITE_EX}What depth do you want to cap the solver at? {Fore.LIGHTMAGENTA_EX}[1-10] {Style.RESET_ALL}")
                    depth = int(userInput)
                    print(f"Depth was set to {Fore.LIGHTMAGENTA_EX}{depth}{Style.RESET_ALL}.")
                elif userInput == "board":
                    printBoard(slots, player, lastSlots=lastSlots)
                elif userInput == "help":
                    print(help)
                elif userInput == "list":
                    print(commands)
                else: # if the player entered a relative index to move
                    moveIndex = convertRelativeIndex(int(userInput), turn)
            canPlay, gameOver = move(slots, moveIndex, turn)
            printBoard(slots, player, lastSlots=lastSlots)
    else:
        canPlay = True
        while canPlay and not gameOver:
            moveIndex = -1
            while not moveIndex in range(1, 14):
                # relativeIndex = random.randint(1, 6) # is inclusive for some reason
                relativeIndex = pickMove(slots, bot, depth)
                moveIndex = convertRelativeIndex(relativeIndex, turn)
                num = slots[moveIndex]
                plural = "s" if num > 1 else ""
                print(f"{Fore.LIGHTYELLOW_EX}> I want to move the {num} marble{plural} in my slot #{relativeIndex}!{Style.RESET_ALL}")
            canPlay, gameOver = move(slots, moveIndex, turn)
            printBoard(slots, player, lastSlots=lastSlots)

    endScores = [slots[7], slots[0]]

    p1gain = endScores[0] - startScores[0]
    p2gain = endScores[1] - startScores[1]
    p1Color = Fore.LIGHTBLUE_EX if player == 1 else Fore.LIGHTYELLOW_EX
    p2Color = Fore.LIGHTBLUE_EX if player == 2 else Fore.LIGHTYELLOW_EX
    p1gainStr = f"({p1Color}+{p1gain}{Style.RESET_ALL})" if p1gain > 0 else ""
    p2gainStr = f"({p2Color}+{p2gain}{Style.RESET_ALL})" if p2gain > 0 else ""
    spacer = " " if p1gain > 0 and p2gain > 0 else ""

    print(f"{Fore.LIGHTBLUE_EX if turn == player else Fore.LIGHTYELLOW_EX}P{turn}{Style.RESET_ALL}'s turn is over. {p1gainStr + spacer + p2gainStr}")

    if not gameOver:
        turn = 2 if turn == 1 else 1
        lastSlots = deepcopy(slots)


print(f"{Fore.GREEN}The game has ended!{Style.RESET_ALL}")
print(f"Score: {Fore.LIGHTBLUE_EX}{slots[7]}{Style.RESET_ALL}-{Fore.LIGHTYELLOW_EX}{slots[0]}{Style.RESET_ALL}")
if slots[0] == slots[7]:
    print("It was a tie!")
else:
    winner = 1 if slots[7] > slots[0] else 2
    print(f"{Fore.LIGHTBLUE_EX if winner == player else Fore.LIGHTYELLOW_EX}P{winner}{Style.RESET_ALL} wins!")
