import pytest

from app.domain.parser.chess_parser import ChessParser
from app.domain.parsed_output import ParsedMove


# ============================================================================
# FIXTURES
# ============================================================================

@pytest.fixture
def sample_configs():
    """Sample language configurations for testing."""
    return {
        'en': {
            'grid_section': {
                'pieces': {
                    'K': 'King',
                    'Q': 'Queen',
                    'R': 'Rook',
                    'B': 'Bishop',
                    'N': 'Knight'
                },
                'cleaning_rules': [
                    {
                        'pattern': r'\b[oO0]-[oO0]-[oO0]\b',
                        'replacement': 'O-O-O'
                    },
                    {
                        'pattern': r'\b[oO0]-[oO0]\b',
                        'replacement': 'O-O'
                    },
                    {
                        'pattern': ':',
                        'replacement': 'x'
                    },
                    {
                        'pattern': '(?<=[NBRQK])[Il](?=[a-h])',
                        'replacement': '1'
                    },
                    {
                        'pattern': r'\s+',
                        'replacement': ''
                    }
                ],
                'extraction_patterns': {
                    'castling': {
                        'pattern': r'^(?:O-O-O|O-O)$',
                        'order': 1
                    },
                    'promotion': {
                        'pattern': r'(?:=|\/)([NBRQK])$',
                        'order': 3
                    },
                    'check_or_mate': {
                        'pattern': r'([+#])$',
                        'order': 2
                    },
                    'destination_square': {
                        'pattern': r'([a-h][1-8])$',
                        'order': 4
                    },
                    'piece_type': {
                        'pattern': r'^([NBRQK])',
                        'order': 5
                    },
                    'capture_indicator': {
                        'pattern': 'x',
                        'order': 6
                    }
                }
            }
        },
        'nl': {
            'grid_section': {
                'pieces': {
                    'K': 'Koning',
                    'D': 'Dame',
                    'T': 'Toren',
                    'L': 'Loper',
                    'P': 'Paard'
                },
                'cleaning_rules': [
                    {
                        'pattern': r'\b[oO0]-[oO0]-[oO0]\b',
                        'replacement': 'O-O-O'
                    },
                    {
                        'pattern': r'\b[oO0]-[oO0]\b',
                        'replacement': 'O-O'
                    },
                    {
                        'pattern': ':',
                        'replacement': 'x'
                    },
                    {
                        'pattern': '(?<=[KDTLP])[Il](?=[a-h])',
                        'replacement': '1'
                    },
                    {
                        'pattern': r'\s+',
                        'replacement': ''
                    }
                ],
                'extraction_patterns': {
                    'castling': {
                        'pattern': r'^(?:O-O-O|O-O)$',
                        'order': 1
                    },
                    'promotion': {
                        'pattern': r'(?:=|/)([KDTLP])$',
                        'order': 3
                    },
                    'check_or_mate': {
                        'pattern': r'([+#])$',
                        'order': 2
                    },
                    'destination_square': {
                        'pattern': r'([a-h][1-8])$',
                        'order': 4
                    },
                    'piece_type': {
                        'pattern': r'^([KDTLP])',
                        'order': 5
                    },
                    'capture_indicator': {
                        'pattern': 'x',
                        'order': 6
                    }
                }
            }
        }
    }


@pytest.fixture
def parser(sample_configs):
    return ChessParser(sample_configs)


def test_parser_initialization(sample_configs):
    parser = ChessParser(sample_configs)
    assert parser.grid_configs == sample_configs


def test_parser_validation_fails_missing_grid_section():
    invalid_config = {"en": {"wrong_key": {}}}
    with pytest.raises(ValueError, match="Invalid config for language 'en'"):
        ChessParser(invalid_config)


# ============================================================================
# BASIC MOVE PARSING TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_piece,expected_dest", [
    ("e4", "", "e4"),  # Pawn move
    ("Nf3", "N", "f3"),  # Knight move
    ("Bb5", "B", "b5"),  # Bishop move
    ("Ra1", "R", "a1"),  # Rook move
    ("Qd8", "Q", "d8"),  # Queen move
    ("Kh1", "K", "h1"),  # King move
])
def test_parse_basic_moves(parser, raw_input, expected_piece, expected_dest):
    """Test parsing of basic piece moves."""
    result = parser.parse(raw_input, 'en')

    assert result.raw_input == raw_input
    assert result.piece == expected_piece
    assert result.destination == expected_dest
    assert result.move_type == "standard"
    assert result.is_capture is False
    assert result.check_state is None
    assert result.is_valid_syntax is True


# ============================================================================
# CAPTURE TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_piece,expected_dest", [
    ("dxc5", "", "c5"),  # Pawn capture
    ("Nxe5", "N", "e5"),  # Knight capture
    ("Bxg5", "B", "g5"),  # Bishop capture
    ("Rxc8", "R", "c8"),  # Rook capture
    ("Qxc7", "Q", "c7"),  # Queen capture
])
def test_parse_captures(parser, raw_input, expected_piece, expected_dest):
    """Test parsing of capture moves."""
    result = parser.parse(raw_input, 'en')

    assert result.piece == expected_piece
    assert result.destination == expected_dest
    assert result.is_capture is True


# ============================================================================
# CHECK AND CHECKMATE TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_check", [
    ("Nf3+", "+"),  # Check
    ("Qh8#", "#"),  # Checkmate
    ("e4+", "+"),  # Pawn check
    ("Rxc8#", "#"),  # Capture with checkmate
])
def test_parse_check_and_mate(parser, raw_input, expected_check):
    """Test parsing of moves with check or checkmate."""
    result = parser.parse(raw_input, 'en')

    assert result.check_state == expected_check


# ============================================================================
# PROMOTION TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_promotion", [
    ("e8=Q", "Q"),  # Promote to queen
    ("e8=R", "R"),  # Promote to rook
    ("e8=B", "B"),  # Promote to bishop
    ("e8=N", "N"),  # Promote to knight
    ("a1=Q+", "Q"),  # Promotion with check
    ("exd8=Q#", "Q"),  # Capture promotion with checkmate
])
def test_parse_promotions(parser, raw_input, expected_promotion):
    """Test parsing of pawn promotion moves."""
    result = parser.parse(raw_input, 'en')

    assert result.promotion == expected_promotion


# ============================================================================
# CASTLING TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_castle_type", [
    ("O-O", "kingside"),
    ("O-O-O", "queenside"),
    ("0-0", "kingside"),  # Test OCR cleanup
    ("0-0-0", "queenside"),  # Test OCR cleanup
    ("o-o", "kingside"),  # Test lowercase cleanup
])
def test_parse_castling(parser, raw_input, expected_castle_type):
    """Test parsing of castling moves."""
    result = parser.parse(raw_input, 'en')

    assert result.move_type == "castling"
    assert result.piece == "K"
    assert result.disambiguation == expected_castle_type
    assert result.destination is None


# ============================================================================
# DISAMBIGUATION TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_piece,expected_dest,expected_disamb", [
    ("Nbd7", "N", "d7", "b"),  # File disambiguation
    ("R1a3", "R", "a3", "1"),  # Rank disambiguation
    ("Qh4e1", "Q", "e1", "h4"),  # Full square disambiguation
    ("Nge2", "N", "e2", "g"),  # File disambiguation
])
def test_parse_disambiguation(parser, raw_input, expected_piece, expected_dest, expected_disamb):
    """Test parsing of moves with disambiguation."""
    result = parser.parse(raw_input, 'en')

    assert result.piece == expected_piece
    assert result.destination == expected_dest
    assert result.disambiguation == expected_disamb


# ============================================================================
# CLEANING TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,expected_clean", [
    ("N f3", "Nf3"),  # Whitespace removal
    ("e:d5", "exd5"),  # Colon to x
    ("RIa3", "R1a3"), # I/l to 1 before file
    ("Blh6", "B1h6"),
    ("e 4 +", "e4+"),  # Multiple spaces
])
def test_input_cleaning(parser, raw_input, expected_clean):
    """Test input cleaning rules are applied correctly."""
    result = parser.parse(raw_input, 'en')

    assert result.san_intent == expected_clean


# ============================================================================
# MULTILINGUAL TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,lang,expected_piece,expected_dest", [
    ("Pe4", "nl", "P", "e4"),  # Dutch knight (Paard)
    ("Lc4", "nl", "L", "c4"),  # Dutch bishop (Loper)
    ("Ta1", "nl", "T", "a1"),  # Dutch rook (Toren)
    ("Dd5", "nl", "D", "d5"),  # Dutch queen (Dame)
])
def test_parse_dutch_notation(parser, raw_input, lang, expected_piece, expected_dest):
    """Test parsing of Dutch chess notation."""
    result = parser.parse(raw_input, lang)

    assert result.piece == expected_piece
    assert result.destination == expected_dest
    assert result.san_intent.startswith(expected_piece)


def test_dutch_castling(parser):
    """Test castling works in Dutch notation."""
    result = parser.parse("O-O", "nl")

    assert result.move_type == "castling"
    assert result.piece == "K"


# ============================================================================
# COMPLEX MOVE TESTS
# ============================================================================

@pytest.mark.parametrize("raw_input,piece,dest,disamb,promo,check,capture", [
    ("Nbxd7+", "N", "d7", "b", None, "+", True),
    ("e8=Q#", "", "e8", None, "Q", "#", False),
    ("Raxc1", "R", "c1", "a", None, None, True),
    ("exf8=N+", "", "f8", "e", "N", "+", True),
])
def test_parse_complex_moves(parser, raw_input, piece, dest, disamb, promo, check, capture):
    """Test parsing of complex moves with multiple components."""
    result = parser.parse(raw_input, 'en')

    assert result.piece == piece
    assert result.destination == dest
    assert result.disambiguation == disamb
    assert result.promotion == promo
    assert result.check_state == check
    assert result.is_capture == capture


# ============================================================================
# BATCH PARSING TESTS
# ============================================================================

def test_parse_batch(parser):
    """Test batch parsing of multiple moves."""
    moves = ["e4", "Nf3", "O-O", "Qd8+"]
    results = parser.parse_batch(moves, 'en')

    assert len(results) == 4
    assert all(isinstance(r, ParsedMove) for r in results)
    assert results[0].destination == "e4"
    assert results[1].piece == "N"
    assert results[2].move_type == "castling"
    assert results[3].check_state == "+"


# ============================================================================
# ERROR HANDLING TESTS
# ============================================================================

def test_parse_unsupported_language(parser):
    """Test parsing raises error for unsupported language."""
    with pytest.raises(ValueError, match="Language 'de' not supported"):
        parser.parse("Nf3", "de")


def test_parse_invalid_language_message(parser):
    """Test error message includes available languages."""
    with pytest.raises(ValueError, match="Available: .*en.*nl"):
        parser.parse("e4", "invalid")


# ============================================================================
# EDGE CASES
# ============================================================================

def test_parse_empty_string(parser):
    """Test parsing empty string."""
    result = parser.parse("", 'en')

    assert result.raw_input == ""
    assert result.san_intent == ""


def test_parse_whitespace_only(parser):
    """Test parsing whitespace-only string."""
    result = parser.parse("   ", 'en')

    assert result.san_intent == ""


def test_parse_preserves_raw_input(parser):
    """Test that raw_input is preserved unchanged."""
    raw = " N f3 + "
    result = parser.parse(raw, 'en')

    assert result.raw_input == raw
    assert result.san_intent == "Nf3+"


# ============================================================================
# VALIDATION PROPERTY TESTS
# ============================================================================

def test_is_valid_syntax_castling(parser):
    """Test is_valid_syntax returns True for castling."""
    result = parser.parse("O-O", 'en')
    assert result.is_valid_syntax is True


def test_is_valid_syntax_with_destination(parser):
    """Test is_valid_syntax returns True when destination exists."""
    result = parser.parse("Nf3", 'en')
    assert result.is_valid_syntax is True


def test_is_valid_syntax_no_destination(parser):
    """Test is_valid_syntax returns False when destination is None."""
    # This would require creating a ParsedMove manually since
    # the parser should always extract a destination for standard moves
    parsed = ParsedMove(
        raw_input="N",
        san_intent="N",
        move_type="standard",
        piece="N",
        destination=None
    )
    assert parsed.is_valid_syntax is False
