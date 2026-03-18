## Core Flows

The application has several distinct user flows that work together:

### OCR + Parse -> Frontend Editing

1. User uploads scoresheet image(s) → `POST /api/scoresheets`.
2. `PreprocessingPipeline` resizes and encodes image to meet API limits.
3. `ClaudeOCRProvider` extracts structured data including header info and raw move strings.
4. `ChessParser` cleans OCR noise and converts strings to `ParsedMove` objects.

### Validate and Correct Edited Moves

1. User clicks the submit button → `POST /api/validate`.
2. `ValidationService` detects the notation language and translates moves to English.
3. `MoveValidator` and `correct_moves` logic verify move legality and suggest corrections for errors.
4. Frontend displays validation results and suggestions.

### Export to PGN

1. User exports the final moves → `POST /api/validate/pgn`.
2. `to_pgn` utility generates a standard PGN file with headers and English SAN moves.

## Package Breakdown

### `app/api/` - FastAPI Layer
```
api/
├── dependencies.py      # Singleton service factories (@lru_cache)
├── dtos/                # Pydantic DTOs (API contract)
│   ├── move_dto.py
│   ├── scoresheet_dto.py
│   └── validation_dto.py
└── routes/              # FastAPI routers (Controllers)
    ├── health.py        # GET /health
    ├── scoresheet.py    # POST /api/scoresheets
    └── validation.py    # POST /api/validate, /api/validate/pgn
```

### `app/services/` - Business Logic Orchestration

```
services/
├── ocr/                 # OCR Provider implementations (Claude, etc.)
│   ├── base.py
│   └── claude.py
├── preprocessing/       # Image processing before OCR
│   └── pipeline.py
├── ocr_service.py       # Orchestrates preprocessing and OCR
├── parsing_service.py   # Raw strings → ParsedMove → DTOs
└── validation_service.py # lang → EN → validate → lang
```

### `app/domain/` - Pure Business Logic

```
domain/
├── parser/
│   ├── chess_parser.py  # Cleans raw text into chess moves
│   └── pgn.py           # PGN export logic
├── validator/
│   ├── correction.py    # Logic for finding move suggestions
│   ├── explanation.py   # Textual explanations for illegal moves
│   └── move_validator.py # Core move validation
├── notation.py          # Notation detection and translation (EN/FR/NL)
├── parsed_output.py     # ParsedMove domain model
└── scoresheet.py        # Scoresheet domain model
```

### `app/corpus/` - Static Data

Contains JSON files with language-specific piece names and common header mappings used for detection and translation. Additionally, it contains cleaning rules and extraction patterns for noisy OCR output.

### `app/tests/` - Automated Tests

Includes tests for core flows.

## Infrastructure

- `Dockerfile` and `docker-compose.yml`: Containerization for local development and deployment.
- `requirements.txt`: Python dependencies (fastapi, python-chess, anthropic, opencv-python, etc.).

## Decision Explanations

- **`@lru_cache`**: Used in `dependencies.py` to avoid service instantiation on every request.
- **`pydantic`**: Used for DTOs to ensure type-safety.
- **Internal Translation**: Moves are translated to English for the `python-chess` library, which is strictly English-only, then translated back if necessary to maintain user context.
