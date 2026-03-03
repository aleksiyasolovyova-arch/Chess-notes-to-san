import pytest
from typing import List

from app.services.validation_service import ValidationService


@pytest.fixture
def validation_service():
    return ValidationService()


class TestValidationService:
    """Tests for ValidationService with translation."""

    def test_english_moves_work(self, validation_service):
        """English moves pass through unchanged."""
        moves = ["e4", "e5", "Nf3"]
        result = validation_service.validate_moves(moves, lang="en")

        assert result["all_legal"] is True
        assert len(result["moves"]) == 3
        assert all(m["legal"] for m in result["moves"])
        assert [m["move"] for m in result["moves"]] == moves

    def test_french_moves_translated(self, validation_service):
        """French moves get translated internally before validation."""
        french_moves = ["e4", "e5", "Cf3", "Cc6"]  # C = Cavalier
        result = validation_service.validate_moves(french_moves, lang="fr")

        assert result["all_legal"] is True
        # User sees original French moves back
        assert result["moves"][2]["move"] == "Cf3"
        assert result["moves"][3]["move"] == "Cc6"

    def test_french_knight_move_is_legal(self, validation_service):
        """French Cf3 is legal because it translates to Nf3."""
        result = validation_service.validate_moves(["Cf3"], lang="fr")

        assert result["all_legal"] is True

    def test_dutch_moves_translated(self, validation_service):
        """Dutch moves get translated internally before validation."""
        dutch_moves = ["e4", "Pe4"]  # P = Paard (knight)
        result = validation_service.validate_moves(dutch_moves, lang="nl")

        assert result["all_legal"] is False  # Pe4 is invalid
        assert result["moves"][1]["move"] == "Pe4"  # Original preserved

    def test_dutch_knight_move_is_legal(self, validation_service):
        """Dutch Pf3 is legal because it translates to Nf3."""
        result = validation_service.validate_moves(["Pf3"], lang="nl")

        assert result["all_legal"] is True

    def test_illegal_move_gets_explanation(self, validation_service):
        """Illegal moves get language-specific explanations."""
        moves = ["e4", "Ra3"]  # Ra3 illegal early game
        result = validation_service.validate_moves(moves, lang="en")

        assert result["all_legal"] is False
        assert not result["moves"][1]["legal"]
        assert "can't reach" in result["moves"][1]["reason"]

    def test_french_illegal_explanation(self, validation_service):
        """Error messages come back in user's language."""
        moves = ["e4", "Ra3"]
        result = validation_service.validate_moves(moves, lang="fr")

        assert "ne peut pas atteindre" in result["moves"][1]["reason"]

    def test_original_move_preserved_on_illegal(self, validation_service):
        """Original notation is preserved even when the move is illegal."""
        moves = ["e4", "Ta3"]  # Ta3 = Ra3 in Dutch, still illegal
        result = validation_service.validate_moves(moves, lang="nl")

        assert result["moves"][1]["move"] == "Ta3"
        assert not result["moves"][1]["legal"]

    def test_unsupported_language_raises_error(self, validation_service):
        """Unsupported languages fail early with a clear message."""
        with pytest.raises(ValueError, match="Unsupported language"):
            validation_service.validate_moves(["e4"], lang="de")
