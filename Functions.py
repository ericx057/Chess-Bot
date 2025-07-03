PIECE_VALUES = {
    'P': 100, 'N': 320, 'B': 330, 'R': 500, 'Q': 900, 'K': 20000,
    'p': -100, 'n': -320, 'b': -330, 'r': -500, 'q': -900, 'k': -20000
}

# Position tables for better evaluation
PAWN_TABLE = [
    [0,  0,  0,  0,  0,  0,  0,  0],
    [50, 50, 50, 50, 50, 50, 50, 50],
    [10, 10, 20, 30, 30, 20, 10, 10],
    [5,  5, 10, 25, 25, 10,  5,  5],
    [0,  0,  0, 20, 20,  0,  0,  0],
    [5, -5,-10,  0,  0,-10, -5,  5],
    [5, 10, 10,-20,-20, 10, 10,  5],
    [0,  0,  0,  0,  0,  0,  0,  0]
]

KNIGHT_TABLE = [
    [-50,-40,-30,-30,-30,-30,-40,-50],
    [-40,-20,  0,  0,  0,  0,-20,-40],
    [-30,  0, 10, 15, 15, 10,  0,-30],
    [-30,  5, 15, 20, 20, 15,  5,-30],
    [-30,  0, 15, 20, 20, 15,  0,-30],
    [-30,  5, 10, 15, 15, 10,  5,-30],
    [-40,-20,  0,  5,  5,  0,-20,-40],
    [-50,-40,-30,-30,-30,-30,-40,-50]
]

def evaluate(board):
    """Enhanced evaluation function with positional considerations"""
    score = 0

    # Material evaluation
    for x in range(8):
        for y in range(8):
            piece = board[x][y]
            if piece != '.':
                score += PIECE_VALUES.get(piece, 0)

                # Positional evaluation
                if piece in 'Pp':
                    pos_score = PAWN_TABLE[x][y]
                    if piece == 'p':
                        pos_score = -PAWN_TABLE[7-x][y]
                    score += pos_score
                elif piece in 'Nn':
                    pos_score = KNIGHT_TABLE[x][y]
                    if piece == 'n':
                        pos_score = -KNIGHT_TABLE[7-x][y]
                    score += pos_score

    # Center control bonus
    center_squares = [(3,3), (3,4), (4,3), (4,4)]
    for x, y in center_squares:
        piece = board[x][y]
        if piece != '.':
            if piece.isupper():
                score += 10
            else:
                score -= 10

    # Piece development (knights and bishops off back rank)
    if board[7][1] != 'N':  # White knight developed
        score += 10
    if board[7][6] != 'N':  # White knight developed
        score += 10
    if board[7][2] != 'B':  # White bishop developed
        score += 10
    if board[7][5] != 'B':  # White bishop developed
        score += 10

    if board[0][1] != 'n':  # Black knight developed
        score -= 10
    if board[0][6] != 'n':  # Black knight developed
        score -= 10
    if board[0][2] != 'b':  # Black bishop developed
        score -= 10
    if board[0][5] != 'b':  # Black bishop developed
        score -= 10

    return score
