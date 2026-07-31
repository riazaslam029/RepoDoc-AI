from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.routes import analyze

app = FastAPI(
    title='RepoDoc AI API',
    description='AI-powered GitHub Documentation Assistant',
    version='1.0.0',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(analyze.router, prefix='/api/v1', tags=['analyze'])


@app.get('/health')
async def health_check():
    return {'status': 'ok', 'version': '1.0.0'}