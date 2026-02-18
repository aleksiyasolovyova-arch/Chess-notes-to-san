import re
from typing import Dict, Any, Optional
from app.domain.parsed_output import ParsedMove

class ChessParser:
    def __init__(self, language_configs: Dict[str, Any]):
        self.configs = language_configs

        self._validate_configs()

    def _validate_configs(self) -> None:
          required_keys = ['grid_section']
          for lang_code, config in self.configs.items():
              if not all(key in config for key in required_keys):
                  raise ValueError(f"Invalid config for language '{lang_code}'")


    def parse(self, raw_input: str, lang_code: str = 'en') -> ParsedMove:
        if lang_code not in self.configs:
            raise ValueError(
                f"Language '{lang_code}' not supported. "
                f"Available: {list(self.configs.keys())}"
            )

        config = self.configs[lang_code]
        grid_config = config['grid_section']

        cleaned = self._clean_input(raw_input, grid_config['cleaning_rules'])

        castling_move = self._try_parse_castling(raw_input, cleaned, grid_config)
        if castling_move:
            return castling_move

        components = self._extract_components(cleaned, grid_config)

        return ParsedMove(
            raw_input=raw_input,
            san_intent=cleaned,
            move_type="standard",
            piece=components['piece'],
            destination=components['destination'],
            disambiguation=components['disambiguation'],
            promotion=components['promotion'],
            check_state=components['check_state'],
            is_capture=components['is_capture']

        )



    def _clean_input(self, text: str, rules: list) -> str:

        for rule in rules:
            text = re.sub(rule['pattern'], rule['replacement'], text)
        return text.strip()

    def _try_parse_castling(self, raw: str, clean: str, grid_config: Dict) -> Optional[ParsedMove]:
        pattern = grid_config['extraction_patterns']['castling']['pattern']
        match = re.search(pattern, clean)

        if not match:
            return None

        san_move = clean
        castle_type = "queenside" if "O-O-O" in san_move else "kingside"

        return ParsedMove(
            raw_input=raw,
            san_intent=san_move,
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
        components = {
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

    def parse_batch(self, raw_inputs: list[str], lang_code: str = 'en') -> list[ParsedMove]:
        return[self.parse(raw, lang_code) for raw in raw_inputs]


