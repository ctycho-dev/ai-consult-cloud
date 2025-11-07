# AI Consult Cloud

## Backend (FastAPI)

### Install
```bash
cd backend
python -m venv .venv
source .venv/bin/activate 
pip install -r requirements.txt
```

### Run
```bash
cd backend
mode=dev uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Backend runs at [http://localhost:8000](http://localhost:8000)

### Create admin user
```bash
cd backend
mode=dev python3 -m scripts.create_admin
```

### Load test
```bash
cd backend
# In another terminal - with web UI (recommended)
locust -f load_test.py --host=http://localhost:8000

# Then open http://localhost:8089 in browser
# Enter: 15 users, spawn rate 2, then click Start
```

---

## Frontend (React/Next.js)

### Install
```bash
cd frontend
npm install
```

### Run
```bash
npm run dev
```

Frontend runs at [http://localhost:3000](http://localhost:5173)
