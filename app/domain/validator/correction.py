import chess
from app.domain.validator.explanation import _parse_san_parts, SAN_PIECE_MAP


def correct_moves(moves: list[str]) -> list[dict]:
    board = chess.Board()
    results = []

    for i, move in enumerate(moves):
        try:
            board.push_san(move)
            results.append({"move": move, "legal": True})
        except ValueError:
            suggestion, fix_type = _find_correction(board, moves, i)
            entry = {"move": move, "legal": False, "suggestion": suggestion, "fix_type": fix_type}
            results.append(entry)
            if suggestion:
                board.push_san(suggestion)

    return results


def _find_correction(board, moves, error_index):
    illegal_san = moves[error_index]
    piece_type, target_sq, disambig = _parse_san_parts(illegal_san)

    future_anchor_matches = []
    if piece_type is not None:
        future_target = _scan_future_piece_move(moves, error_index, piece_type)
        if future_target is not None:
            for legal_move in board.legal_moves:
                moved_piece = board.piece_at(legal_move.from_square)
                if moved_piece is None or moved_piece.piece_type != piece_type:
                    continue
                sim_board = board.copy()
                sim_board.push(legal_move)
                probe = chess.Move(legal_move.to_square, future_target)
                if probe in sim_board.pseudo_legal_moves:
                    future_anchor_matches.append(legal_move)

            if len(future_anchor_matches) == 1:
                return board.san(future_anchor_matches[0]), "future_anchor"

    candidates = _generate_candidates(board, illegal_san, future_anchor_matches)

    remaining = moves[error_index + 1:]

    # Pass 2 — global fix
    for move_obj in candidates:
        san = board.san(move_obj)
        if _simulate_forward(board, san, remaining, require_all=True):
            return san, "global"

    # Pass 3 — local fix
    for move_obj in candidates:
        san = board.san(move_obj)
        if _simulate_forward(board, san, remaining, require_all=False):
            return san, "local"

    return None, None


def _generate_candidates(board, illegal_san, future_anchor_matches):
    piece_type, target_sq, disambig = _parse_san_parts(illegal_san)
    anchor_set = set(future_anchor_matches)

    scored = []
    for legal_move in board.legal_moves:
        if legal_move in anchor_set:
            continue
        score = 0
        moved_piece = board.piece_at(legal_move.from_square)
        if moved_piece and piece_type and moved_piece.piece_type == piece_type:
            score += 10
        if target_sq is not None and legal_move.to_square == target_sq:
            score += 5
        elif target_sq is not None:
            file_diff = abs(chess.square_file(legal_move.to_square) - chess.square_file(target_sq))
            rank_diff = abs(chess.square_rank(legal_move.to_square) - chess.square_rank(target_sq))
            if file_diff <= 1 and rank_diff <= 1:
                score += 3
        scored.append((score, legal_move))

    scored.sort(key=lambda x: -x[0])
    return list(future_anchor_matches) + [m for _, m in scored]


def _scan_future_piece_move(moves, error_index, piece_type):
    for future_san in moves[error_index + 1:]:
        ft, sq, _ = _parse_san_parts(future_san)
        if ft == piece_type and sq is not None:
            return sq
    return None


def _simulate_forward(board, candidate_san, remaining_moves, require_all):
    sim = board.copy()
    try:
        sim.push_san(candidate_san)
    except ValueError:
        return False

    for move_san in remaining_moves:
        try:
            sim.push_san(move_san)
        except ValueError:
            if require_all:
                return False
            return True

    return True
