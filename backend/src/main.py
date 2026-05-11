from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from presentation.controllers.proposicao_controller import router

app = FastAPI(title="Monitor Legislativo API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {"message": "API rodando"}


@app.get("/health")
def health():
    return {"status": "ok"}
