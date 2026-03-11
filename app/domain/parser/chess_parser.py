import re
from typing import Dict, Any, Optional, List
from app.domain.parsed_output import ParsedMove
from app.domain.notation import NOTATION_CONFIG, detect_notation_language


class ChessParser:
    def __init__(self, grid_configs: Dict[str, Any]):
        self.grid_configs = grid_configs
        self.signatures = {lang: set(mapping.keys()) for lang, mapping in NOTATION_CONFIG.items()}
        self._validate_configs()

    def _validate_configs(self) -> None:
        required = ["grid_section"]
        for lang, config in self.grid_configs.items():
            if not all(k in config for k in required):
                raise ValueError(f"Invalid config for language '{lang}': missing {required}")

    def detect_notation_language(self, raw_moves: List[str]) -> str:
        return detect_notation_language(raw_moves)

    def parse_moves(self, raw_moves: List[str]) -> List[ParsedMove]:
        lang = self.detect_notation_language(raw_moves)
        return self.parse_batch(raw_moves, lang)

    def parse_batch(self, raw_moves: List[str], lang: str = "en") -> List[ParsedMove]:
        if lang not in self.grid_configs:
            available = ", ".join(sorted(self.grid_configs.keys()))
            raise ValueError(f"Language '{lang}' not supported. Available: {available}")
        return [self.parse(move, lang) for move in raw_moves]

    def parse(self, raw_input: str, lang: str = "en") -> ParsedMove:
        if lang not in self.grid_configs:
            available = ", ".join(sorted(self.grid_configs.keys()))
            raise ValueError(f"Language '{lang}' not supported. Available: {available}")

        config = self.grid_configs[lang]["grid_section"]
        cleaned = self._clean_input(raw_input, config["cleaning_rules"])
        cleaned = self._sanitize_input(cleaned, config)

        castling = self._try_parse_castling(raw_input, cleaned, config)
        if castling:
            return castling

        components = self._extract_components(cleaned, config)

        return ParsedMove(
            raw_input=raw_input,
            san_intent=cleaned,
            move_type="standard",
            piece=components.get("piece", ""),
            destination=components.get("destination"),
            disambiguation=components.get("disambiguation"),
            promotion=components.get("promotion"),
            check_state=components.get("check_state"),
            is_capture=components.get("is_capture", False),
        )


    def _clean_input(self, text: str, rules: list) -> str:
        for rule in rules:
            text = re.sub(rule['pattern'], rule['replacement'], text)
        return text.strip()

    def _try_parse_castling(self, raw: str, clean_move: str, grid_config: Dict) -> Optional[ParsedMove]:
        pattern = grid_config['extraction_patterns']['castling']['pattern']
        if not re.search(pattern, clean_move):
            return None

        castle_type = "queenside" if "O-O-O" in clean_move else "kingside"

        return ParsedMove(
            raw_input=raw,
            san_intent=clean_move,
            move_type="castling",
            piece="K",
            destination=None,
            disambiguation=castle_type,
            promotion=None,
            check_state=None,
            is_capture=False
        )

    def _extract_components(self, cleaned: str, grid_config: Dict) -> Dict[str, Any]:
        patterns = grid_config['extraction_patterns']
        components: Dict[str, Any] = {
            'piece': '',
            'destination': None,
            'disambiguation': None,
            'promotion': None,
            'check_state': None,
            'is_capture': False
        }

        sorted_patterns = sorted(
            patterns.items(),
            key=lambda x: x[1].get('order', 999)
        )

        working_string = cleaned

        for pattern_name, pattern_config in sorted_patterns:
            if pattern_name == 'castling':
                continue

            pattern = pattern_config['pattern']

            if pattern_name == 'promotion':
                match = re.search(pattern, working_string)
                if match:
                   components['promotion'] = match.group(1)
                   working_string = re.sub(pattern, '', working_string)

            elif pattern_name == 'check_or_mate':
                match = re.search(pattern, working_string)
                if match:
                    components['check_state'] = match.group(1)
                    working_string = re.sub(pattern, '', working_string)

            elif pattern_name == 'destination_square':
                match = re.search(pattern, working_string)
                if match:
                    components['destination'] = match.group(1)
                    working_string = working_string.replace(match.group(1), '', 1)

            elif pattern_name == 'piece_type':
                match = re.search(pattern, working_string)
                if match:
                    components['piece'] = match.group(1)
                    working_string = re.sub(pattern, '', working_string, count=1)

            elif pattern_name == 'capture_indicator':
                if 'x' in working_string:
                    components['is_capture'] = True
                    working_string = working_string.replace('x', '', 1)

        if not components['piece']:
            components['piece'] = ''

        remaining = working_string.strip()
        if remaining:
            components['disambiguation'] = remaining

        return components


    def _sanitize_input(self, text: str, grid_config: Dict) -> str:
        valid_chars_cfg = grid_config.get("valid_characters", {})
        allowed = set(
            valid_chars_cfg.get("letters", []) +
            valid_chars_cfg.get("numbers", []) +
            valid_chars_cfg.get("symbols", [])
        )
        if not allowed:
            return text
        return "".join(c for c in text if c in allowed)
