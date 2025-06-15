
PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
}

def evaluate(board):
    score = 0
    for row in board:
        for p in row:
            score += PIECE_VALUES.get(p, 0)
    return score
