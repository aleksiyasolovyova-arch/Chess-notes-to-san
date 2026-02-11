from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from validation import validate_moves, SUPPORTED_LANGUAGES

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

MAX_SIZE = 10 * 1024 * 1024  # 10 MB
ACCEPTED_TYPES = {"image/jpeg", "image/png", "image/webp", "application/pdf"}


@app.post("/api/scoresheets")
async def upload_scoresheet(file: UploadFile = File(...)):
    if file.content_type not in ACCEPTED_TYPES:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: {file.content_type}")

    contents = await file.read()
    if len(contents) > MAX_SIZE:
        raise HTTPException(status_code=400, detail="File too large. Maximum size is 10 MB.")

    # Mock response — replace with actual OCR processing
    mock_moves = [
        "e4", "e5", "Nf3", "Nc6", "Bb5", "a6", "Ba4", "Nf6",
        "O-O", "Be7", "Re1", "b5", "Bb3", "d6", "c3", "O-O",
        "h3", "Nb8", "d4", "Nbd7", "Nbd2", "Bb7", "Bc2", "Re8",
        "Nf1", "Bf8", "Ng3", "g6", "Bg5", "h6", "Bd2", "Bg7",
        "a4", "c5", "d5", "c4", "b4", "Nh5", "Be3", "Nf4",
        "Qd2", "a5", "Ra3", "axb4", "cxb4", "Bc8", "Rea1", "Bd7",
        "Kh2", "Qc7", "Ng1", "Rab8", "f3", "Nh5", "Nxh5", "gxh5",
        "g4", "hxg4", "hxg4", "h5", "g5", "Nf8", "Rg1", "Ng6",
        "Nf3", "Kh7", "Nh4", "Nxh4", "Qxh4", "Rg8", "Qg3", "Be8",
        "Bd1", "Qd7", "Be2", "Bg6", "Kh1", "Re8", "Bd1", "Bf8",
    ]
    return {
        "filename": file.filename,
        "white": "Shakira",
        "white_elo": 1000,
        "black": "Emmanuel Macron",
        "black_elo": 1000,
        "date": "2026-02-09",
        "tournament": "Interland",
        "moves": mock_moves,
        "status": "success",
    }


class ScoresheetUpdate(BaseModel):
    white: str
    white_elo: int
    black: str
    black_elo: int
    date: str
    tournament: str
    moves: list[str]


class ValidateRequest(BaseModel):
    moves: list[str]
    lang: str = "en"


@app.post("/api/validate")
async def validate(body: ValidateRequest):
    if body.lang not in SUPPORTED_LANGUAGES:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported language '{body.lang}', choose from: {sorted(SUPPORTED_LANGUAGES)}",
        )
    results = validate_moves(body.moves, lang=body.lang)
    all_legal = all(r["legal"] for r in results)
    return {"legal": all_legal, "moves": results}


@app.put("/api/scoresheets/{filename}")
async def update_scoresheet(filename: str, body: ScoresheetUpdate):
    return {
        "filename": filename,
        "white": body.white,
        "white_elo": body.white_elo,
        "black": body.black,
        "black_elo": body.black_elo,
        "date": body.date,
        "tournament": body.tournament,
        "moves": body.moves,
        "status": "updated",
    }
