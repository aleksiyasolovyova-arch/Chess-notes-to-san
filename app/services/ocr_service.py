import random
#TODO: literally replace this whole service lmao

class OCRService:
    def __init__(self):
        self.mock_data = {
            "en": {
                "white": "Magnus Carlsen",
                "black": "Fabiano Caruana",
                "white_elo": 2830,
                "black_elo": 2800,
                "date": "2024-10-12",
                "tournament": "Sinquefield Cup",
                "lang": "en",
                "raw_moves": [
                    "e4", "e5", "Nf3", "Nc6", "Bb5", "a6",
                    "Ba4", "Nf6", "O-O", "Be7", "Re1", "b5"
                ]
            },
            "fr": {
                "white": "Pierre Dubois",
                "black": "Marie Laurent",
                "white_elo": 2250,
                "black_elo": 2230,
                "date": "2025-02-15",
                "tournament": "Tournoi Lier",
                "lang": "fr",
                "raw_moves": [
                    "e4", "e5", "Cf3", "Cc6", "Fb5", "a6",
                    "Fb4", "Cf6", "O-O", "Fe7", "Re1", "b5"
                ]
            },
            "nl": {
                "white": "Jan de Vries",
                "black": "Els van Dijk",
                "white_elo": 2180,
                "black_elo": 2160,
                "date": "2026-01-20",
                "tournament": "Lier Open",
                "lang": "nl",
                "raw_moves": [
                    "e4", "e5", "Pf3", "Pc6", "Lb5", "a6",
                    "Lb4", "Pf6", "O-O", "Le7", "Te1", "b5"
                ]
            }
        }

    def process_scoresheet(self, image_bytes: bytes) -> dict:
        return {
            "raw_text": """
        White: Magnus Carlsen
        Elo: 2830
        Black: Fabiano Caruana  
        Elo: 2800
        Tournament: Sinquefield Cup
        Date: 2024-10-12
        """,
            "raw_moves": ["e4", "e5", "Pf3", "Pc6", "Lb5", "a6"]
        }

