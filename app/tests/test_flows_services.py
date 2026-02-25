import json
from unittest.mock import Mock

import pytest

from app.services.ocr_service import OCRService
from app.services.parsing_service import ParsingService
from app.services.preprocessing.pipeline import PreprocessingPipeline
from app.services.validation_service import ValidationService


@pytest.fixture
def ocr_service():
    provider = Mock()
    provider.recognize.return_value = json.dumps({
        "white": "Shakira",
        "white_elo": 1000,
        "black": "Emmanuel Macron",
        "black_elo": 1000,
        "date": "2026-02-09",
        "tournament": "Interland",
        "lang": "en",
        "raw_moves": ["e4", "e5", "Nf3", "Nc6", "Bb5", "a6"],
    })
    pipeline = Mock()
    pipeline.run.return_value = b"preprocessed"
    return OCRService(provider=provider, pipeline=pipeline)


@pytest.fixture
def parsing_service():
    return ParsingService()


@pytest.fixture
def validation_service():
    return ValidationService()


def test_flow1_ocr_to_parsed_moves(ocr_service, parsing_service):
    """End-to-end: fake OCR → parsed moves DTOs."""
    header, raw_moves = ocr_service.process_scoresheet(b"fake image data")

    assert isinstance(raw_moves, list)
    assert header.lang in ("en", "nl", "fr")

    moves_dto = parsing_service.parse_moves(raw_moves, header.lang)

    # Parsed list matches raw length
    assert len(moves_dto) == len(raw_moves)

    # DTO properties look reasonable
    first = moves_dto[0]
    assert first.raw_input == raw_moves[0]
    assert isinstance(first.san_intent, str)
    assert first.san_intent != "" or first.raw_input.strip() == ""


def test_flow2_validate_english(validation_service):
    """End-to-end: validate a simple legal English sequence."""
    moves = ["d4", "d5", "c4", "e6", "Nc3", "Nf6", "Bg5", "Be7", "e3", "h6", "Bh4", "O-O"]
    result = validation_service.validate_moves(moves, lang="en")

    assert isinstance(result, dict)
    assert result["all_legal"] is True
    assert len(result["moves"]) == len(moves)
    assert all(m["legal"] for m in result["moves"])



def test_flow2_validate_french(validation_service):
    """End-to-end: French notation → translation → validation → French back."""
    french_moves = ["e4", "e5", "Cf3", "Cc6"]
    result = validation_service.validate_moves(french_moves, lang="fr")

    # Still the same number of moves
    assert len(result["moves"]) == len(french_moves)

    # Moves in result should be ORIGINAL French, not English
    returned_moves = [m["move"] for m in result["moves"]]
    assert returned_moves == french_moves

    # They should all be legal
    assert result["all_legal"] is True
    assert all(m["legal"] for m in result["moves"])


def test_flow2_validate_illegal_with_reason(validation_service):
    """End-to-end: illegal move produces an explanation."""
    moves = ["e4", "e5", "Ra3"]
    result = validation_service.validate_moves(moves, lang="en")

    assert result["all_legal"] is False

    # Last move should be illegal and have a reason
    last = result["moves"][-1]
    assert last["move"] == "Ra3"
    assert last["legal"] is False
    assert isinstance(last.get("reason"), str)
    assert last["reason"]  # non-empty
