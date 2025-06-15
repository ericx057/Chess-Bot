import copy
import multiprocessing
from Functions import evaluate

DIRECTIONS = {
    'N': [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2)],
    'B': [(-1, -1), (-1, 1), (1, -1), (1, 1)],
    'R': [(-1, 0), (1, 0), (0, -1), (0, 1)],
    'Q': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)],
    'K': [(-1, -1), (-1, 1), (1, -1), (1, 1), (-1, 0), (1, 0), (0, -1), (0, 1)]
}

def initial_board():
    return [
        list("rnbqkbnr"),
        list("pppppppp"),
        list("........"),
        list("........"),
        list("........"),
        list("........"),
        list("PPPPPPPP"),
        list("RNBQKBNR")
    ]

def in_bounds(x, y):
    return 0 <= x < 8 and 0 <= y < 8

def is_white(piece):
    return piece.isupper()

def is_black(piece):
    return piece.islower()

def opponent(color):
    return 'black' if color == 'white' else 'white'

def king_pos(board, color):
    k = 'K' if color == 'white' else 'k'
    for x in range(8):
        for y in range(8):
            if board[x][y] == k:
                return (x, y)
    return None

def is_attacked(board, x, y, color):
    opp = opponent(color)
    for i in range(8):
        for j in range(8):
            p = board[i][j]
            if p == '.' or (is_white(p) if color == 'white' else is_black(p)):
                continue
            moves = generate_piece_moves(board, i, j, opp, ignore_checks=True)
            for m in moves:
                if m[2] == x and m[3] == y:
                    return True
    return False

def generate_moves(board, color, castling, en_passant, ignore_checks=False):
    moves = []
    for x in range(8):
        for y in range(8):
            p = board[x][y]
            if p == '.' or (color == 'white' and p.islower()) or (color == 'black' and p.isupper()):
                continue
            moves.extend(generate_piece_moves(board, x, y, color, castling, en_passant, ignore_checks))
    if not ignore_checks:
        legal_moves = []
        for move in moves:
            b2, c2, ep2 = make_move(copy.deepcopy(board), move, color, castling, en_passant)
            if not is_in_check(b2, color):
                legal_moves.append(move)
        return legal_moves
    return moves

def generate_piece_moves(board, x, y, color, castling=None, en_passant=None, ignore_checks=False):
    moves = []
    p = board[x][y]
    if p in 'Pp':
        direction = -1 if p == 'P' else 1
        start_row = 6 if p == 'P' else 1
        nx, ny = x + direction, y
        if in_bounds(nx, ny) and board[nx][ny] == '.':
            if nx == 0 or nx == 7:
                for promo in ['Q', 'R', 'B', 'N']:
                    moves.append((x, y, nx, ny, promo if p == 'P' else promo.lower()))
            else:
                moves.append((x, y, nx, ny, None))
            if x == start_row and board[x + 2 * direction][y] == '.':
                moves.append((x, y, x + 2 * direction, y, None))
        for dy in [-1, 1]:
            nx, ny = x + direction, y + dy
            if in_bounds(nx, ny):
                target = board[nx][ny]
                if target != '.' and ((is_white(p) and is_black(target)) or (is_black(p) and is_white(target))):
                    if nx == 0 or nx == 7:
                        for promo in ['Q', 'R', 'B', 'N']:
                            moves.append((x, y, nx, ny, promo if p == 'P' else promo.lower()))
                    else:
                        moves.append((x, y, nx, ny, None))
        if en_passant:
            ep_x, ep_y = en_passant
            if abs(ep_y - y) == 1 and nx == ep_x and ny == ep_y:
                moves.append((x, y, nx, ny, None))
    elif p in 'Nn':
        for dx, dy in DIRECTIONS['N']:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                target = board[nx][ny]
                if target == '.' or (is_white(p) and is_black(target)) or (is_black(p) and is_white(target)):
                    moves.append((x, y, nx, ny, None))
    elif p in 'Bb':
        for dx, dy in DIRECTIONS['B']:
            for i in range(1, 8):
                nx, ny = x + dx * i, y + dy * i
                if not in_bounds(nx, ny):
                    break
                target = board[nx][ny]
                if target == '.':
                    moves.append((x, y, nx, ny, None))
                elif (is_white(p) and is_black(target)) or (is_black(p) and is_white(target)):
                    moves.append((x, y, nx, ny, None))
                    break
                else:
                    break
    elif p in 'Rr':
        for dx, dy in DIRECTIONS['R']:
            for i in range(1, 8):
                nx, ny = x + dx * i, y + dy * i
                if not in_bounds(nx, ny):
                    break
                target = board[nx][ny]
                if target == '.':
                    moves.append((x, y, nx, ny, None))
                elif (is_white(p) and is_black(target)) or (is_black(p) and is_white(target)):
                    moves.append((x, y, nx, ny, None))
                    break
                else:
                    break
    elif p in 'Qq':
        for dx, dy in DIRECTIONS['Q']:
            for i in range(1, 8):
                nx, ny = x + dx * i, y + dy * i
                if not in_bounds(nx, ny):
                    break
                target = board[nx][ny]
                if target == '.':
                    moves.append((x, y, nx, ny, None))
                elif (is_white(p) and is_black(target)) or (is_black(p) and is_white(target)):
                    moves.append((x, y, nx, ny, None))
                    break
                else:
                    break
    elif p in 'Kk':
        for dx, dy in DIRECTIONS['K']:
            nx, ny = x + dx, y + dy
            if in_bounds(nx, ny):
                target = board[nx][ny]
                if target == '.' or (is_white(p) and is_black(target)) or (is_black(p) and is_white(target)):
                    moves.append((x, y, nx, ny, None))
        if castling and not ignore_checks:
            if color == 'white' and x == 7 and y == 4:
                if castling['K'] and board[7][5] == board[7][6] == '.' and not is_attacked(board, 7, 4, color) and not is_attacked(board, 7, 5, color) and not is_attacked(board, 7, 6, color):
                    moves.append((7, 4, 7, 6, 'castleK'))
                if castling['Q'] and board[7][1] == board[7][2] == board[7][3] == '.' and not is_attacked(board, 7, 2, color) and not is_attacked(board, 7, 3, color) and not is_attacked(board, 7, 4, color):
                    moves.append((7, 4, 7, 2, 'castleQ'))
            if color == 'black' and x == 0 and y == 4:
                if castling['k'] and board[0][5] == board[0][6] == '.' and not is_attacked(board, 0, 4, color) and not is_attacked(board, 0, 5, color) and not is_attacked(board, 0, 6, color):
                    moves.append((0, 4, 0, 6, 'castlek'))
                if castling['q'] and board[0][1] == board[0][2] == board[0][3] == '.' and not is_attacked(board, 0, 2, color) and not is_attacked(board, 0, 3, color) and not is_attacked(board, 0, 4, color):
                    moves.append((0, 4, 0, 2, 'castleq'))
    return moves

def make_move(board, move, color, castling, en_passant):
    x1, y1, x2, y2, promo = move
    piece = board[x1][y1]
    new_castling = copy.deepcopy(castling)
    new_en_passant = None
    board[x1][y1] = '.'
    if promo == 'castleK':
        board[7][6] = 'K'
        board[7][5] = 'R'
        board[7][4] = board[7][7] = '.'
        new_castling['K'] = new_castling['Q'] = False
    elif promo == 'castleQ':
        board[7][2] = 'K'
        board[7][3] = 'R'
        board[7][4] = board[7][0] = '.'
        new_castling['K'] = new_castling['Q'] = False
    elif promo == 'castlek':
        board[0][6] = 'k'
        board[0][5] = 'r'
        board[0][4] = board[0][7] = '.'
        new_castling['k'] = new_castling['q'] = False
    elif promo == 'castleq':
        board[0][2] = 'k'
        board[0][3] = 'r'
        board[0][4] = board[0][0] = '.'
        new_castling['k'] = new_castling['q'] = False
    else:
        if piece in 'Pp' and y1 != y2 and board[x2][y2] == '.':
            board[x2][y2] = piece
            board[x1][y2] = '.'
        else:
            board[x2][y2] = piece if not promo else promo
        if piece == 'P' and x1 == 6 and x2 == 4:
            new_en_passant = (5, y1)
        elif piece == 'p' and x1 == 1 and x2 == 3:
            new_en_passant = (2, y1)
        if piece == 'K':
            new_castling['K'] = new_castling['Q'] = False
        if piece == 'k':
            new_castling['k'] = new_castling['q'] = False
        if piece == 'R' and x1 == 7 and y1 == 0:
            new_castling['Q'] = False
        if piece == 'R' and x1 == 7 and y1 == 7:
            new_castling['K'] = False
        if piece == 'r' and x1 == 0 and y1 == 0:
            new_castling['q'] = False
        if piece == 'r' and x1 == 0 and y1 == 7:
            new_castling['k'] = False
    return board, new_castling, new_en_passant

def is_in_check(board, color):
    kpos = king_pos(board, color)
    if not kpos:
        return True
    return is_attacked(board, kpos[0], kpos[1], color)

def is_checkmate(board, color, castling, en_passant):
    if not is_in_check(board, color):
        return False
    moves = generate_moves(board, color, castling, en_passant)
    return len(moves) == 0

def is_stalemate(board, color, castling, en_passant):
    if is_in_check(board, color):
        return False
    moves = generate_moves(board, color, castling, en_passant)
    return len(moves) == 0

def search(board, color, castling, en_passant, depth, alpha, beta, maximizing, node_limit, node_counter):
    if node_counter[0] > node_limit:
        return evaluate(board)
    if depth == 0:
        node_counter[0] += 1
        return evaluate(board)
    moves = generate_moves(board, color, castling, en_passant)
    if not moves:
        if is_in_check(board, color):
            return -999999 if maximizing else 999999
        else:
            return 0
    if maximizing:
        value = -9999999
        for move in moves:
            b2, c2, ep2 = make_move(copy.deepcopy(board), move, color, castling, en_passant)
            score = search(b2, opponent(color), c2, ep2, depth - 1, alpha, beta, False, node_limit, node_counter)
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value
    else:
        value = 9999999
        for move in moves:
            b2, c2, ep2 = make_move(copy.deepcopy(board), move, color, castling, en_passant)
            score = search(b2, opponent(color), c2, ep2, depth - 1, alpha, beta, True, node_limit, node_counter)
            value = min(value, score)
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value

def root_search_worker(args):
    board, move, color, castling, en_passant, depth, node_limit = args
    b2, c2, ep2 = make_move(copy.deepcopy(board), move, color, castling, en_passant)
    node_counter = [0]
    score = search(b2, opponent(color), c2, ep2, depth - 1, -9999999, 9999999, False, node_limit, node_counter)
    return (move, score)

def best_move(board, color, castling, en_passant, depth, node_limit=1000000):
    moves = generate_moves(board, color, castling, en_passant)
    if not moves:
        return None
    pool = multiprocessing.Pool(processes=4)
    args = [(board, move, color, castling, en_passant, depth, node_limit) for move in moves]
    results = pool.map(root_search_worker, args)
    pool.close()
    pool.join()
    if color == 'white':
        best = max(results, key=lambda x: x[1])
    else:
        best = min(results, key=lambda x: x[1])
    return best[0]
