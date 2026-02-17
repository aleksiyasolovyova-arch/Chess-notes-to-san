# app/tests/services/test_validation_service.py
import pytest
from typing import List

from app.services.validation_service import ValidationService
from app.domain.parser.notation_translator import NotationTranslator


@pytest.fixture
def validation_service():
    return ValidationService()


@pytest.fixture
def translator():
    return NotationTranslator()


class TestValidationService:
    """Tests for ValidationService with translation."""

    def test_english_moves_work(self, validation_service):
        """English moves pass through unchanged."""
        moves = ["e4", "e5", "Nf3"]
        result = validation_service.validate_moves(moves, lang="en")

        assert result["all_legal"] is True
        assert len(result["moves"]) == 3
        assert all(m["legal"] for m in result["moves"])

    def test_french_moves_translated(self, validation_service, translator):
        """French moves get translated internally."""
        french_moves = ["e4", "e5", "Cf3", "Cc6"]  # C = Cavalier
        result = validation_service.validate_moves(french_moves, lang="fr")

        assert result["all_legal"] is True
        # User sees original French moves back
        assert result["moves"][2]["move"] == "Cf3"
        assert result["moves"][3]["move"] == "Cc6"

    def test_dutch_moves_translated(self, validation_service):
        """Dutch moves get translated."""
        dutch_moves = ["e4", "Pe4"]  # P = Paard (knight)
        result = validation_service.validate_moves(dutch_moves, lang="nl")

        assert result["all_legal"] is False  # Pe4 invalid
        assert result["moves"][1]["move"] == "Pe4"  # Original preserved

    def test_illegal_move_gets_explanation(self, validation_service):
        """Illegal moves get language-specific explanations."""
        moves = ["e4", "Ra3"]  # Ra3 illegal early game
        result = validation_service.validate_moves(moves, lang="en")

        assert result["all_legal"] is False
        assert not result["moves"][1]["legal"]
        assert "can't reach" in result["moves"][1]["reason"]

    def test_french_illegal_explanation(self, validation_service):
        """Error messages in user's language."""
        moves = ["e4", "Ra3"]
        result = validation_service.validate_moves(moves, lang="fr")

        assert "ne peut pas atteindre" in result["moves"][1]["reason"]  # French

    def test_unsupported_language_raises_error(self, validation_service):
        """Unsupported languages fail early."""
        with pytest.raises(ValueError, match="Unsupported language"):
            validation_service.validate_moves(["e4"], lang="de")

class TestNotationTranslator:
    """Tests for the internal translator."""

    def test_french_to_english(self, translator):
        assert translator.translate("Cf3", "fr") == "Nf3"  # C→N
        assert translator.translate("Tf1", "fr") == "Rf1"  # T→R
        assert translator.translate("e4", "fr") == "e4"    # Pawn unchanged

    def test_dutch_to_english(self, translator):
        assert translator.translate("Pe4", "nl") == "Ne4"  # P→N
        assert translator.translate("Le5", "nl") == "Be5"  # L→B

    def test_english_unchanged(self, translator):
        assert translator.translate("Nf3", "en") == "Nf3"
        assert translator.translate("O-O", "en") == "O-O"
