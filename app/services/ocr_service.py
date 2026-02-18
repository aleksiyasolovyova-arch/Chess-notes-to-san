from typing import List, Dict, Any

#TODO: literally replace this whole service lmao

class OCRService:

    def process_scoresheet(self, file_bytes: bytes) -> Dict[str, Any]:
        # For now: return hardcoded data from old main.py
        mock_moves: List[str] = [
            "e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6",
            "O-O", "Be7", "Re1", "b5", "Bb3", "d6", "c3", "O-O",
        ]
        return {
            "white": "Shakira",
            "white_elo": 1000,
            "black": "Emmanuel Macron",
            "black_elo": 1000,
            "date": "2026-02-09",
            "tournament": "Interland",
            "lang": "en",
            "raw_moves": mock_moves,
        }