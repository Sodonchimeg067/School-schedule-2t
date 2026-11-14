# ЕБС-ийн ахлах ангийн хичээлийн хуваарь боловсруулах систем

FastAPI + SQLAlchemy (SQLite) дээр бүтсэн backend. Лаб-8: GitHub Actions CI.

## Бүтэц
- `src/main.py` – FastAPI апп (US-01…US-16)
- `src/t.js` – Node.js: сурагчийн хичээл сонголтын урсгалын загвар
- `tests/` – pytest автомат тестүүд (in-memory өгөгдлийн сан ашиглана)
- `.github/workflows/ci.yml` – CI workflow

## Ажиллуулах заавар
```bash
python -m venv .venv
.venv\Scripts\activate          # Mac/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.main:app --reload   # http://127.0.0.1:8000/docs
python -m pytest -v             # тест ажиллуулах
```
