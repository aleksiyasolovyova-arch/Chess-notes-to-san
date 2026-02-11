import chess

SAN_PIECE_MAP = {"N": chess.KNIGHT, "B": chess.BISHOP, "R": chess.ROOK,
                 "Q": chess.QUEEN, "K": chess.KING}

TRANSLATIONS = {
    "en": {
        "pieces": {
            chess.PAWN: "pawn", chess.KNIGHT: "knight", chess.BISHOP: "bishop",
            chess.ROOK: "rook", chess.QUEEN: "queen", chess.KING: "king",
        },
        "pieces_def": {
            chess.PAWN: "the pawn", chess.KNIGHT: "the knight", chess.BISHOP: "the bishop",
            chess.ROOK: "the rook", chess.QUEEN: "the queen", chess.KING: "the king",
        },
        "colors": {chess.WHITE: "White", chess.BLACK: "Black"},
        "no_piece": "{color} has no {piece} on the board",
        "no_piece_disambig_file": "{color} has no {piece} on file {disambig}",
        "no_piece_disambig_rank": "{color} has no {piece} on rank {disambig}",
        "no_piece_disambig_square": "{color} has no {piece} on {disambig}",
        "cant_reach": "{color}'s {piece} on {from_sq} can't reach {to_sq}",
        "blocked_by": "{color}'s {piece} on {from_sq} can't reach {to_sq}, path is blocked by {blocker_color}'s {blocker_piece} on {blocker_sq}",
        "leaves_check": "{color}'s {piece} on {from_sq} could reach {to_sq}, but that would leave the king in check",
        "castle_in_check": "{color} can't castle out of check",
        "castle_blocked": "{color} can't castle (king or rook already moved, or path blocked/attacked)",
        "no_legal_way": "{color} to move, no legal way to play {san}",
        "not_valid_notation": "not valid chess notation",
    },
    "fr": {
        "pieces": {
            chess.PAWN: "pion", chess.KNIGHT: "cavalier", chess.BISHOP: "fou",
            chess.ROOK: "tour", chess.QUEEN: "dame", chess.KING: "roi",
        },
        "pieces_def": {
            chess.PAWN: "le pion", chess.KNIGHT: "le cavalier", chess.BISHOP: "le fou",
            chess.ROOK: "la tour", chess.QUEEN: "la dame", chess.KING: "le roi",
        },
        "colors": {chess.WHITE: "Blancs", chess.BLACK: "Noirs"},
        "no_piece": "les {color} n'ont pas de {piece} sur l'échiquier",
        "no_piece_disambig_file": "les {color} n'ont pas de {piece} sur la colonne {disambig}",
        "no_piece_disambig_rank": "les {color} n'ont pas de {piece} sur la rangée {disambig}",
        "no_piece_disambig_square": "les {color} n'ont pas de {piece} sur {disambig}",
        "cant_reach": "{def_piece} des {color} sur {from_sq} ne peut pas atteindre {to_sq}",
        "blocked_by": "{def_piece} des {color} sur {from_sq} ne peut pas atteindre {to_sq}, le chemin est bloqué par {def_blocker} des {blocker_color} sur {blocker_sq}",
        "leaves_check": "{def_piece} des {color} sur {from_sq} pourrait atteindre {to_sq}, mais cela mettrait le roi en échec",
        "castle_in_check": "les {color} ne peuvent pas roquer hors d'un échec",
        "castle_blocked": "les {color} ne peuvent pas roquer (roi ou tour déjà déplacé, ou chemin bloqué/attaqué)",
        "no_legal_way": "les {color} au trait, pas de coup légal pour {san}",
        "not_valid_notation": "notation d'échecs non valide",
    },
    "nl": {
        "pieces": {
            chess.PAWN: "pion", chess.KNIGHT: "paard", chess.BISHOP: "loper",
            chess.ROOK: "toren", chess.QUEEN: "dame", chess.KING: "koning",
        },
        "pieces_def": {
            chess.PAWN: "de pion", chess.KNIGHT: "het paard", chess.BISHOP: "de loper",
            chess.ROOK: "de toren", chess.QUEEN: "de dame", chess.KING: "de koning",
        },
        "colors": {chess.WHITE: "Wit", chess.BLACK: "Zwart"},
        "no_piece": "{color} heeft geen {piece} op het bord",
        "no_piece_disambig_file": "{color} heeft geen {piece} op lijn {disambig}",
        "no_piece_disambig_rank": "{color} heeft geen {piece} op rij {disambig}",
        "no_piece_disambig_square": "{color} heeft geen {piece} op {disambig}",
        "cant_reach": "{def_piece} van {color} op {from_sq} kan {to_sq} niet bereiken",
        "blocked_by": "{def_piece} van {color} op {from_sq} kan {to_sq} niet bereiken, het pad wordt geblokkeerd door {def_blocker} van {blocker_color} op {blocker_sq}",
        "leaves_check": "{def_piece} van {color} op {from_sq} zou {to_sq} kunnen bereiken, maar dat zou de koning schaak zetten",
        "castle_in_check": "{color} kan niet rokeren vanuit schaak",
        "castle_blocked": "{color} kan niet rokeren (koning of toren al verplaatst, of pad geblokkeerd/aangevallen)",
        "no_legal_way": "{color} aan zet, geen legale manier om {san} te spelen",
        "not_valid_notation": "geen geldige schaaknotatie",
    },
}


def _parse_san_parts(san):
    """Extract piece type, target square, and disambiguation from SAN string."""
    clean = san.replace("+", "").replace("#", "").replace("x", "")

    if clean in ("O-O", "O-O-O"):
        return chess.KING, None, None

    if "=" in clean:
        clean = clean.split("=")[0]

    if clean[0] in SAN_PIECE_MAP:
        piece_type = SAN_PIECE_MAP[clean[0]]
        rest = clean[1:]
    else:
        piece_type = chess.PAWN
        rest = clean

    target = rest[-2:]
    disambig = rest[:-2]

    try:
        square = chess.parse_square(target)
    except ValueError:
        return piece_type, None, None

    return piece_type, square, disambig


def _filter_by_disambig(pieces, disambig):
    """Filter candidate squares using SAN disambiguation (file, rank, or both)."""
    if not disambig:
        return pieces
    filtered = []
    for sq in pieces:
        name = chess.square_name(sq)
        if len(disambig) == 2:
            if name == disambig:
                filtered.append(sq)
        elif disambig in "abcdefgh":
            if name[0] == disambig:
                filtered.append(sq)
        elif disambig in "12345678":
            if name[1] == disambig:
                filtered.append(sq)
    return filtered


def _is_blocked_path(board, from_sq, to_sq):
    """Check if a sliding piece's path is blocked."""
    between = chess.SquareSet(chess.between(from_sq, to_sq))
    if not between and from_sq != to_sq:
        return False
    return bool(between & board.occupied)


def _find_blocker(board, from_sq, to_sq):
    """Return the first blocking piece as (color, piece_type, square)."""
    between = chess.SquareSet(chess.between(from_sq, to_sq))
    for sq in between:
        piece = board.piece_at(sq)
        if piece:
            return piece.color, piece.piece_type, sq
    return None


def explain_illegal(board, san, lang="en"):
    """Give a specific reason why a SAN move is illegal."""
    t = TRANSLATIONS[lang]
    color = t["colors"][board.turn]
    piece_type, target_sq, disambig = _parse_san_parts(san)

    if target_sq is None:
        if san in ("O-O", "O-O-O"):
            if board.is_check():
                return t["castle_in_check"].format(color=color)
            return t["castle_blocked"].format(color=color)
        return t["no_legal_way"].format(color=color, san=san)

    piece_name = t["pieces"][piece_type]
    def_piece = t["pieces_def"][piece_type]
    all_pieces = board.pieces(piece_type, board.turn)

    if not all_pieces:
        return t["no_piece"].format(color=color, piece=piece_name)

    candidates = _filter_by_disambig(list(all_pieces), disambig)

    if not candidates:
        if disambig in "abcdefgh":
            return t["no_piece_disambig_file"].format(color=color, piece=piece_name, disambig=disambig)
        elif disambig in "12345678":
            return t["no_piece_disambig_rank"].format(color=color, piece=piece_name, disambig=disambig)
        else:
            return t["no_piece_disambig_square"].format(color=color, piece=piece_name, disambig=disambig)

    for from_sq in candidates:
        move = chess.Move(from_sq, target_sq)

        if board.is_pseudo_legal(move):
            if board.is_into_check(move):
                return t["leaves_check"].format(
                    color=color, piece=piece_name, def_piece=def_piece,
                    from_sq=chess.square_name(from_sq),
                    to_sq=chess.square_name(target_sq))

        if piece_type in (chess.ROOK, chess.QUEEN, chess.BISHOP):
            if _is_blocked_path(board, from_sq, target_sq):
                blocker = _find_blocker(board, from_sq, target_sq)
                if blocker:
                    blocker_color = t["colors"][blocker[0]]
                    blocker_piece = t["pieces"][blocker[1]]
                    def_blocker = t["pieces_def"][blocker[1]]
                    blocker_sq = chess.square_name(blocker[2])
                    return t["blocked_by"].format(
                        color=color, piece=piece_name, def_piece=def_piece,
                        from_sq=chess.square_name(from_sq),
                        to_sq=chess.square_name(target_sq),
                        blocker_color=blocker_color,
                        blocker_piece=blocker_piece,
                        def_blocker=def_blocker,
                        blocker_sq=blocker_sq)

    locations = ", ".join(chess.square_name(sq) for sq in candidates)
    return t["cant_reach"].format(
        color=color, piece=piece_name, def_piece=def_piece,
        from_sq=locations, to_sq=chess.square_name(target_sq))
