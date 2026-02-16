## TWO Core Flows

The application has two distinct(i think so gang) user flows that work together:

### OCR + Parse -> Frontend Editing

1. User uploads scoresheet image → POST /api/scoresheets
2. OCR extracts raw text strings (mock data for now)
3. ChessParser cleans OCR noise → ParsedMove objects
4. ParsingService -> MoveDTOs -> Frontend displays an editable table with moves

### Validate Edited Moves

1. User clicks the submit button -> POST /api/validate
2. The ValidationService translates internally the moves if in another language, then validates them and maps them back to original language
3. Frontend displays validation results


## Package Breakdown

### `app/api/` - FastAPI Layer
````
api/
├── init.py
├── dependencies.py # Singleton service factories (@lru_cache)
├── routes/ # Equivalent to Java controllers
│ ├── init.py
│ ├── scoresheet.py # POST /api/scoresheets (flow 1)
│ └── validation.py # POST /api/validate (flow 2)
└── dtos/ # Pydantic DTOs (API contract)
├── move_dto.py
├── scoresheet_dto.py
└── validation_dto.py
````

#### Some decision explanations:
- `@lru_cache` is python's built-in memoization decorator. The point is to avoid service instantiation on every request.
- Used `pydantic` for DTOs, because it's a great library for type-safety and validation.

### `app/services/` - Business Logic Orchestration

````
services/
├── ocr_service.py          # Mock OCR → raw text strings
├── parsing_service.py      # Raw strings → ParsedMove → DTOs
└── validation_service.py   # lang→EN→validate→lang
````

#### Some decision explanations:
- Internal translation for the moves is purely for the `python-chess` library, as it only accepts english moves. 
- Moves are then translated back to the original language, so as to display properly for the end user.

### `app/domain/` - Pure Business Logic
````
domain/
├── __init__.py
├── parser/
│   ├── __init__.py
│   ├── chess_parser.py     # original parser.py
│   └── notation_translator.py # FR/NL → English (for validation)
├── validator/
│   ├── __init__.py
│   ├── explanation.py      # exactly the same as before
│   └── move_validator.py   # same validation logic as before, wrapper in a class
├── parsed_output.py        # ParsedMove domain model
└── scoresheet.py           # Scoresheet domain model
````

#### Some decision explanations:
- `scoresheet.py` is empty, as we don't need a domain object yet, however it may be needed later on, so i left it like this
- The only change in the validation logic is the added typehint, and validate_moves return a dict with two keys, so as to centralize the business logic of "are all moves legal?" inside the validator where it belongs, rather than repeating it in every HTTP route.