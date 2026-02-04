# Deployment & Running Instructions

## 1. Prerequisites
- Python 3.9+
- Node.js 18+
- Git

## 2. Setup Backend (Python/FastAPI)
1. **Navigate to the root directory**:
   ```bash
   cd /path/to/MCP_Handwritten-Paper-Automation
   ```
2. **Setup Virtual Environment** (Optional but recommended):
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Set Environment Variables**:
   Create a `.env` file in the root if not exists:
   ```bash
   HF_TOKEN=your_hugging_face_token
   ```
5. **Start the API Server**:
   ```bash
   uvicorn api:app --reload --port 8000
   ```
   The backend will run at `http://127.0.0.1:8000`.

## 3. Setup Frontend (React/Vite)
1. **Navigate to frontend directory**:
   ```bash
   cd frontend
   ```
2. **Install Dependencies**:
   ```bash
   npm install
   ```
3. **Start Development Server**:
   ```bash
   npm run dev
   ```
   The frontend will run at `http://localhost:5173`.

## 4. Usage
- Open `http://localhost:5173` in your browser.
- Upload your **Answer Sheet**, **Question Paper**, and **Solution Key**.
- Click **Run Evaluation**.
- View the detailed report with marks and feedback.

## 5. Deployment (Production)
To serve everything together:
1. Build the frontend: `cd frontend && npm run build`
2. Configure FastAPI to serve the `frontend/dist` static files.
3. Deploy the Python app to a standard host (Railway, Render, AWS).
