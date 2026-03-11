import json
from unittest.mock import Mock

import cv2
import numpy as np
import pytest

from app.domain.scoresheet import ScoresheetHeader
from app.services.ocr_service import OCRService, sort_and_strip_move_numbers
from app.services.preprocessing.pipeline import PreprocessingPipeline


def make_image_bytes(width: int, height: int) -> bytes:
    img = np.full((height, width, 3), 128, dtype=np.uint8)
    _, buf = cv2.imencode(".jpg", img)
    return buf.tobytes()


def make_json(**overrides) -> str:
    data = {
        "white": "Alice",
        "white_elo": 1500,
        "black": "Bob",
        "black_elo": 1400,
        "date": "2026-01-01",
        "tournament": "Club Championship",
        "lang": "en",
        "raw_moves": ["1. e4", "2. e5", "3. Nf3"],
    }
    data.update(overrides)
    return json.dumps(data)


class TestSortAndStripMoveNumbers:

    def test_strips_numbers_in_order(self):
        assert sort_and_strip_move_numbers(["1. e4", "2. e5", "3. Nf3"]) == ["e4", "e5", "Nf3"]

    def test_sorts_out_of_order(self):
        assert sort_and_strip_move_numbers(["3. Nf3", "1. e4", "2. e5"]) == ["e4", "e5", "Nf3"]

    def test_empty_list(self):
        assert sort_and_strip_move_numbers([]) == []

    def test_unnumbered_moves_appended(self):
        assert sort_and_strip_move_numbers(["1. e4", "e5"]) == ["e4", "e5"]

    def test_strips_extra_whitespace_around_move(self):
        assert sort_and_strip_move_numbers(["1.  e4", "2.  e5"]) == ["e4", "e5"]

    def test_black_move_ellipsis_with_space(self):
        assert sort_and_strip_move_numbers(["1. e4", "1... e5"]) == ["e4", "e5"]

    def test_black_move_ellipsis_without_space(self):
        assert sort_and_strip_move_numbers(["1. e4", "1...e5"]) == ["e4", "e5"]

    def test_mixed_white_and_black_notation(self):
        result = sort_and_strip_move_numbers(["1. e4", "1... e5", "2. Nf3", "2... Nc6"])
        assert result == ["e4", "e5", "Nf3", "Nc6"]


class TestPreprocessingPipeline:

    def test_returns_bytes(self):
        result = PreprocessingPipeline().run(make_image_bytes(800, 600))
        assert isinstance(result, bytes) and len(result) > 0

    def test_small_image_not_resized(self):
        result = PreprocessingPipeline().run(make_image_bytes(800, 600))
        img = cv2.imdecode(np.frombuffer(result, np.uint8), cv2.IMREAD_COLOR)
        assert max(img.shape[:2]) <= 800

    def test_large_image_is_resized(self):
        result = PreprocessingPipeline().run(make_image_bytes(4000, 3000))
        img = cv2.imdecode(np.frombuffer(result, np.uint8), cv2.IMREAD_COLOR)
        assert max(img.shape[:2]) == 1568

    def test_aspect_ratio_preserved_on_resize(self):
        result = PreprocessingPipeline().run(make_image_bytes(4000, 2000))
        img = cv2.imdecode(np.frombuffer(result, np.uint8), cv2.IMREAD_COLOR)
        h, w = img.shape[:2]
        assert abs(w / h - 2.0) < 0.05

    def test_portrait_image_is_resized(self):
        result = PreprocessingPipeline().run(make_image_bytes(3000, 4000))
        img = cv2.imdecode(np.frombuffer(result, np.uint8), cv2.IMREAD_COLOR)
        assert max(img.shape[:2]) == 1568

    def test_image_at_exact_limit_not_resized(self):
        result = PreprocessingPipeline().run(make_image_bytes(1568, 1000))
        img = cv2.imdecode(np.frombuffer(result, np.uint8), cv2.IMREAD_COLOR)
        assert max(img.shape[:2]) <= 1568

    def test_corrupt_bytes_raises(self):
        with pytest.raises(ValueError, match="Could not decode"):
            PreprocessingPipeline().run(b"not an image")


class TestOCRServiceParse:

    @pytest.fixture
    def service(self):
        return OCRService(provider=Mock(), pipeline=Mock())

    def test_returns_header_and_moves(self, service):
        header, moves = service._parse(make_json())
        assert isinstance(header, ScoresheetHeader)
        assert isinstance(moves, list)

    def test_header_fields(self, service):
        header, _ = service._parse(make_json())
        assert header.white == "Alice"
        assert header.white_elo == 1500
        assert header.black == "Bob"
        assert header.black_elo == 1400
        assert header.date == "2026-01-01"
        assert header.tournament == "Club Championship"
        assert header.lang == "en"

    def test_moves_list(self, service):
        _, moves = service._parse(make_json())
        assert moves == ["e4", "e5", "Nf3"]

    def test_moves_sorted_by_number(self, service):
        scrambled = make_json(raw_moves=["3. Nf3", "1. e4", "2. e5"])
        _, moves = service._parse(scrambled)
        assert moves == ["e4", "e5", "Nf3"]

    def test_moves_without_numbers_pass_through(self, service):
        mixed = make_json(raw_moves=["1. e4", "e5", "3. Nf3"])
        _, moves = service._parse(mixed)
        assert moves == ["e4", "Nf3", "e5"]

    @pytest.mark.parametrize("field,expected", [
        ("white", "Unknown"),
        ("black", "Unknown"),
    ])
    def test_null_name_fields_default(self, service, field, expected):
        header, _ = service._parse(make_json(**{field: None}))
        assert getattr(header, field) == expected

    def test_null_elo_defaults_to_zero(self, service):
        header, _ = service._parse(make_json(white_elo=None, black_elo=None))
        assert header.white_elo == 0
        assert header.black_elo == 0

    def test_null_lang_defaults_to_en(self, service):
        header, _ = service._parse(make_json(lang=None))
        assert header.lang == "en"

    def test_empty_moves_list(self, service):
        _, moves = service._parse(make_json(raw_moves=[]))
        assert moves == []

    def test_strips_markdown_json_fence(self, service):
        wrapped = f"```json\n{make_json()}\n```"
        header, _ = service._parse(wrapped)
        assert header.white == "Alice"

    def test_strips_plain_fence(self, service):
        wrapped = f"```\n{make_json()}\n```"
        header, _ = service._parse(wrapped)
        assert header.white == "Alice"

    def test_missing_moves_key_defaults_to_empty(self, service):
        data = json.loads(make_json())
        del data["raw_moves"]
        _, moves = service._parse(json.dumps(data))
        assert moves == []

    def test_invalid_json_raises(self, service):
        with pytest.raises(json.JSONDecodeError):
            service._parse("not valid json")


class TestOCRServiceProcessScoresheet:

    @pytest.fixture
    def provider(self):
        mock = Mock()
        mock.recognize.return_value = make_json()
        return mock

    @pytest.fixture
    def service(self, provider):
        return OCRService(provider=provider, pipeline=PreprocessingPipeline())

    def test_returns_header_and_moves(self, service):
        header, moves = service.process_scoresheet(make_image_bytes(800, 600))
        assert isinstance(header, ScoresheetHeader)
        assert isinstance(moves, list)

    def test_provider_receives_bytes(self, service, provider):
        service.process_scoresheet(make_image_bytes(800, 600))
        provider.recognize.assert_called_once()
        assert isinstance(provider.recognize.call_args[0][0], bytes)
