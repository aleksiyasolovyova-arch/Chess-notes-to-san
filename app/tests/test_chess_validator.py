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
        result = validation_service.validate_moves(moves, ui_lang="en")

        assert result["all_legal"] is True
        assert len(result["moves"]) == 3
        assert all(m["legal"] for m in result["moves"])
        assert [m["move"] for m in result["moves"]] == moves

    def test_french_moves_translated(self, validation_service):
        french_moves = ["e4", "e5", "Cf3", "Cc6"]
        result = validation_service.validate_moves(french_moves, notation_lang="fr", ui_lang="fr")

        assert result["all_legal"] is True
        assert result["moves"][2]["move"] == "Cf3"
        assert result["moves"][3]["move"] == "Cc6"

    def test_french_knight_move_is_legal(self, validation_service):
        result = validation_service.validate_moves(["Cf3"], notation_lang="fr", ui_lang="fr")
        assert result["all_legal"] is True

    def test_dutch_knight_move_is_legal(self, validation_service):
        result = validation_service.validate_moves(["Pf3"], notation_lang="nl", ui_lang="nl")
        assert result["all_legal"] is True

    def test_dutch_moves_translated(self, validation_service):
        dutch_moves = ["e4", "Pe4"]
        result = validation_service.validate_moves(dutch_moves, notation_lang="nl", ui_lang="nl")

        assert result["all_legal"] is False
        assert result["moves"][1]["move"] == "Pe4"


    def test_illegal_move_gets_explanation(self, validation_service):
        """Illegal moves get ui_language-specific explanations."""
        moves = ["e4", "Ra3"]  # Ra3 illegal early game
        result = validation_service.validate_moves(moves, ui_lang="en")

        assert result["all_legal"] is False
        assert not result["moves"][1]["legal"]
        assert "can't reach" in result["moves"][1]["reason"]

    def test_french_illegal_explanation(self, validation_service):
        """Error messages come back in user's ui_language."""
        moves = ["e4", "Ra3"]
        result = validation_service.validate_moves(moves, ui_lang="fr")

        assert "ne peut pas atteindre" in result["moves"][1]["reason"]

    def test_original_move_preserved_on_illegal(self, validation_service):
        moves = ["e4", "Ta3"]
        result = validation_service.validate_moves(moves, notation_lang="nl", ui_lang="nl")

        assert result["moves"][1]["move"] == "Ta3"
        assert not result["moves"][1]["legal"]

    def test_unsupported_ui_language_raises_error(self, validation_service):
        with pytest.raises(ValueError, match="Unsupported language"):
            validation_service.validate_moves(["e4"], ui_lang="de")

