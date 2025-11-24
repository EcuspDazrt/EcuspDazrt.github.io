from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from Solver import GameBoard

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.post("/solve")
def solve(payload: dict):
    gameboard = GameBoard()
    board = payload["board"]
    board_state = [[board[i+j*4]for i in range(4)] for j in range(4)]
    gameboard.board = board_state
    moves = gameboard.solve()  # e.g. ["R", "U", "L", "D"]
    return moves

@app.post("/shuffle")
def init_board():
    board = GameBoard()
    return board.board

uvicorn.run(app, host="0.0.0.0", port=8000)