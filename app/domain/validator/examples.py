from app.domain.validator.move_validator import MoveValidator


validator = MoveValidator()


def print_results(title, description, moves):
    print(f"=== {title} ===")
    print(f"Error: {description}")
    result = validator.validate_moves(moves)
    for r in result["moves"]:
        if r["legal"]:
            print(f"  {r['move']:8s} legal")
        else:
            suggestion = r.get("suggestion")
            fix_type = r.get("fix_type")
            fix = f" -> {suggestion} ({fix_type})" if suggestion else ""
            print(f"  {r['move']:8s} ILLEGAL: {r['reason']}{fix}")
    print()


# Opera Game (Morphy vs Duke of Brunswick, 1858)
# Ng6 should be Nf6 (adjacent square misread)
opera_game = [
    "e4", "e5", "Nf3", "d6", "d4", "Bg4",
    "dxe5", "Bxf3", "Qxf3", "dxe5", "Bc4", "Ng6",
    "Qb3", "Qe7", "Nc3", "c6", "Bg5", "b5",
    "Nxb5", "cxb5", "Bxb5+", "Nbd7", "O-O-O", "Rd8",
    "Rxd7", "Rxd7", "Rd1", "Qe6", "Bxd7+", "Nxd7",
    "Qb8+", "Nxb8", "Rd8#",
]

# Immortal Game (Anderssen vs Kieseritzky, 1851) — first 21 moves
# Bc5 should be Bc4 (adjacent square misread)
immortal_game = [
    "e4", "e5", "f4", "exf4", "Bc5", "Qh4+",
    "Kf1", "b5", "Bxb5", "Nf6", "Nf3", "Qh6",
    "d3", "Nh5", "Nh4", "Qg5", "Nf5", "c6",
    "g4", "Nf6", "Rg1",
]

# Kasparov's Immortal (Kasparov vs Topalov, 1999) — first 22 moves
# Nge3 should be Nge2 (adjacent square misread)
kasparov_immortal = [
    "e4", "d6", "d4", "Nf6", "Nc3", "g6",
    "Be3", "Bg7", "Qd2", "c6", "f3", "b5",
    "Nge3", "Nbd7", "Bh6", "Bxh6", "Qxh6", "Bb7",
    "a3", "e5", "O-O-O", "Qe7",
]

# Evergreen Game (Anderssen vs Dufresne, 1852) — first 20 moves
# Ba5 misread as Ba6 (adjacent square)
evergreen_game = [
    "e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5",
    "b4", "Bxb4", "c3", "Ba6", "d4", "exd4",
    "O-O", "d3", "Qb3", "Qf6", "e5", "Qg6",
    "Re1", "Nge7",
]

# Game of the Century (Byrne vs Fischer, 1956) — first 26 moves
# Bg4 misread as Bg3 (wrong square)
game_of_century = [
    "Nf3", "Nf6", "c4", "g6", "Nc3", "Bg7",
    "d4", "O-O", "Bf4", "d5", "Qb3", "dxc4",
    "Qxc4", "c6", "e4", "Nbd7", "Rd1", "Nb6",
    "Qc5", "Bg3", "Bg5", "Na4", "Qa3", "Nxc3",
    "bxc3", "Nxe4",
]

# Scholar's Mate attempt — short and simple
# Bc4 misread as Bc3 (wrong square)
scholars_mate = [
    "e4", "e5", "Bc3", "Nc6", "Qh5", "Nf6", "Qxf7#",
]

# Italian Game (Giuoco Piano) — first 16 moves
# Nxe3 misread as Nxe4 (adjacent square, wrong capture target)
italian_game = [
    "e4", "e5", "Nf3", "Nc6", "Bc4", "Bc5",
    "c3", "Nf6", "d4", "exd4", "cxd4", "Bb4+",
    "Nc3", "Nxe3", "O-O", "d5",
]

# Sicilian Dragon — first 18 moves
# Be3 misread as Be2 (wrong square, piece already on e2 would conflict)
sicilian_dragon = [
    "e4", "c5", "Nf3", "d6", "d4", "cxd4",
    "Nxd4", "Nf6", "Nc3", "g6", "Be2", "Bg7",
    "f3", "O-O", "Qd2", "Nc6", "Be2", "a6",
]

# --- Future anchor tests ---

# Scotch Game — future anchor fix
# Nd5 is illegal for the f3 knight; the future Nb3 reveals the knight
# needed to land on d4 (from d4, Nb3 is reachable), so Nxd4 is the anchor fix.
scotch_future_anchor = [
    "e4", "e5", "Nf3", "Nc6", "d4", "exd4",
    "Nd5", "Bc5", "Nb3", "Bb6",
]

# Ruy Lopez — future anchor fix
# Bb6 is illegal for the f1 bishop; the future Bxb5 reveals the bishop
# needed to reach the b5 square, anchoring the correction to Bb5.
ruy_lopez_future_anchor = [
    "e4", "e5", "Nf3", "Nc6", "Bb6", "a6",
    "Ba4", "Nf6", "O-O", "Be7",
]

# --- Local fix tests (multiple errors — global simulation fails) ---

# Sicilian Najdorf with two errors — forces local fixes
# Error 1: Nxd5 (move 4) — knight on f3 can't reach d5, should be Nxd4
# Error 2: Bg6 (move 11) — bishop on c1 can't reach g6, should be Bg5
najdorf_two_errors = [
    "e4", "c5", "Nf3", "d6", "d4", "cxd4",
    "Nxd5", "Nf6", "Nc3", "a6", "Bg6", "e6",
    "f4", "Be7",
]

# King's Indian with two errors — forces local fixes
# Error 1: Nc4 (move 3) — knight on b1 can't reach c4, should be Nc3
# Error 2: Bf2 (move 11) — bishop on f1 can't reach f2 (not diagonal), should be Be2
king_indian_two_errors = [
    "d4", "Nf6", "c4", "g6", "Nc4", "Bg7",
    "e4", "d6", "Nf3", "O-O", "Bf2", "e5",
    "O-O", "Nc6", "d5", "Ne7",
]

# --- Mixed: anchor + later error ---

# Queen's Gambit Declined — anchor fix on first error, local fix on second
# Error 1: Bf4 (move 7) — bishop on c1 is blocked by d2 pawn (still there),
#          should be Bg5; the future Bxf6 anchors it (from g5, Bxf6 works).
# Error 2: Rc2 (move 15) — rook can't reach c2, should be Rc1
qgd_mixed = [
    "d4", "d5", "c4", "e6", "Nc3", "Nf6",
    "Bf4", "Be7", "e3", "O-O", "Nf3", "Nbd7",
    "Bxf6", "Bxf6", "Rc2", "c6",
]


if __name__ == "__main__":
    print_results(
        "Opera Game (Morphy, 1858)",
        "Ng6 should be corrected to Nf6",
        opera_game,
    )
    print_results(
        "Immortal Game (Anderssen, 1851)",
        "Bc5 should be corrected to Bc4",
        immortal_game,
    )
    print_results(
        "Kasparov's Immortal (1999)",
        "Nge3 should be corrected to Nge2",
        kasparov_immortal,
    )
    print_results(
        "Evergreen Game (Anderssen, 1852)",
        "Ba6 should be corrected to Ba5",
        evergreen_game,
    )
    print_results(
        "Game of the Century (Fischer, 1956)",
        "Bg3 should be corrected to Bg4",
        game_of_century,
    )
    print_results(
        "Scholar's Mate attempt",
        "Bc3 should be corrected to Bc4",
        scholars_mate,
    )
    print_results(
        "Italian Game (Giuoco Piano)",
        "Nxe3 should be corrected to Nxe4",
        italian_game,
    )
    print_results(
        "Sicilian Dragon",
        "Be2 (move 17) should be corrected to Be3",
        sicilian_dragon,
    )

    # Future anchor tests
    print_results(
        "Scotch Game — future anchor",
        "Nd5 should be corrected to Nxd4 (anchored by future Nb3)",
        scotch_future_anchor,
    )
    print_results(
        "Ruy Lopez — future anchor",
        "Bb6 should be corrected to Bb5 (anchored by future Bxb5)",
        ruy_lopez_future_anchor,
    )

    # Local fix tests (multiple errors)
    print_results(
        "Sicilian Najdorf — two errors (local)",
        "Nxd5 -> Nxd4 (local), Bg6 -> Bg5 (local)",
        najdorf_two_errors,
    )
    print_results(
        "King's Indian — two errors (local)",
        "Nc4 -> Nc3 (local), Bf2 -> Be2 (local)",
        king_indian_two_errors,
    )

    # Mixed test
    print_results(
        "QGD — anchor + local mix",
        "Bf4 -> Bg5 (anchor via Bxf6), Rc2 -> Rc1 (local)",
        qgd_mixed,
    )
