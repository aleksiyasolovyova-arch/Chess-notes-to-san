from app.services.validation_service import ValidationService


def test_flow2_validate_english():
    """End-to-end: validate a simple legal English sequence."""
    service = ValidationService()
    moves = ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "h6", "Bh4", "O-O"]
    result = service.validate_moves(moves, lang="en")

    assert isinstance(result, dict)
    assert result["all_legal"] is True
    assert len(result["moves"]) == len(moves)
    assert all(m["legal"] for m in result["moves"])


def test_flow2_validate_french():
    """End-to-end: French notation → translation → validation → French back."""
    service = ValidationService()
    french_moves = ["e4", "e5", "Cf3", "Cc6"]
    result = service.validate_moves(french_moves, lang="fr")

    assert len(result["moves"]) == len(french_moves)
    returned_moves = [m["move"] for m in result["moves"]]
    assert returned_moves == french_moves
    assert result["all_legal"] is True
    assert all(m["legal"] for m in result["moves"])


def test_flow2_validate_illegal_with_reason():
    """End-to-end: illegal move produces an explanation."""
    service = ValidationService()
    moves = ["e4", "e5", "Ra3"]
    result = service.validate_moves(moves, lang="en")

    assert result["all_legal"] is False
    last = result["moves"][-1]
    assert last["move"] == "Ra3"
    assert last["legal"] is False
    assert isinstance(last.get("reason"), str)
    assert last["reason"]
