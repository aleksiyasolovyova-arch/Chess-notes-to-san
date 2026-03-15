import pytest
from app.domain.parser.pgn import to_pgn
from app.domain.scoresheet import ScoresheetHeader


@pytest.fixture
def full_header():
    return ScoresheetHeader(
        white="Magnus Carlsen",
        black="Hikaru Nakamura",
        white_elo=2830,
        black_elo=2794,
        date="2024.01.15",
        tournament="World Rapid",
        lang="en",
        result="1-0",
    )


@pytest.fixture
def empty_header():
    return ScoresheetHeader(
        white="",
        black="",
        white_elo=0,
        black_elo=0,
        date="",
        tournament="",
        lang="en",
        result="*",
    )


class TestToPgnHeaders:
    def test_full_header_tags_present(self, full_header):
        pgn = to_pgn(full_header, ["e4", "e5"])

        assert '[White "Magnus Carlsen"]' in pgn
        assert '[Black "Hikaru Nakamura"]' in pgn
        assert '[Event "World Rapid"]' in pgn
        assert '[Date "2024.01.15"]' in pgn
        assert '[Result "1-0"]' in pgn

    def test_empty_header_uses_defaults(self, empty_header):
        pgn = to_pgn(empty_header, ["e4"])

        assert '[White "?"]' in pgn
        assert '[Black "?"]' in pgn
        assert '[Event "?"]' in pgn
        assert '[Date "????.??.??"]' in pgn

    def test_site_always_question_mark(self, full_header):
        pgn = to_pgn(full_header, ["e4"])
        assert '[Site "?"]' in pgn

    def test_round_always_question_mark(self, full_header):
        pgn = to_pgn(full_header, ["e4"])
        assert '[Round "?"]' in pgn


class TestToPgnResult:


    def test_unknown_result_tag_and_terminator(self, empty_header):
        pgn = to_pgn(empty_header, ["e4"])
        assert '[Result "*"]' in pgn
        assert pgn.endswith("*")

    def test_result_default_is_unknown(self):
        header = ScoresheetHeader(
            white="A", black="B",
            white_elo=0, black_elo=0,
            date="", tournament="",
            lang="en",
            # result omitted — should default to "*"
        )
        pgn = to_pgn(header, ["e4"])
        assert '[Result "*"]' in pgn
        assert pgn.endswith("*")


class TestToPgnMoves:
    def test_even_move_count(self, full_header):
        pgn = to_pgn(full_header, ["e4", "e5", "Nf3", "Nc6"])
        assert "1. e4 e5" in pgn
        assert "2. Nf3 Nc6" in pgn

    def test_odd_move_count_last_white_only(self, full_header):
        pgn = to_pgn(full_header, ["e4", "e5", "Nf3"])
        assert "1. e4 e5" in pgn
        assert "2. Nf3" in pgn

    def test_single_move(self, full_header):
        pgn = to_pgn(full_header, ["e4"])
        assert "1. e4" in pgn

    def test_move_numbering_is_sequential(self, full_header):
        moves = ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"]
        pgn = to_pgn(full_header, moves)
        assert "1. e4 e5" in pgn
        assert "2. Nf3 Nc6" in pgn
        assert "3. Bb5 a6" in pgn

    def test_illegal_move_still_exported(self, full_header):
        """PGN export does not enforce legality — all moves are written as-is."""
        pgn = to_pgn(full_header, ["e4", "Vb6"])
        assert "Vb6" in pgn

    def test_headers_and_moves_separated_by_blank_line(self, full_header):
        pgn = to_pgn(full_header, ["e4", "e5"])
        parts = pgn.split("\n\n")
        assert len(parts) == 2
        assert parts[0].startswith("[")
        assert parts[1].startswith("1.")

    def test_castling_exported(self, full_header):
        moves = ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "O-O"]
        pgn = to_pgn(full_header, moves)
        assert "O-O" in pgn

    def test_promotion_exported(self, full_header):
        pgn = to_pgn(full_header, ["e4", "e5", "e8=Q"])
        assert "e8=Q" in pgn
