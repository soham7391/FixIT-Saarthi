# FixIT Saarthi — AI-Assisted Computer Troubleshooting Expert System

**FixIT Saarthi** is an AI-assisted computer troubleshooting expert system designed to help users diagnose and resolve PC performance and freezing issues through structured diagnostic reasoning.

---

## 🚀 What FixIT Saarthi Is

FixIT Saarthi is **not** an unconstrained chatbot. It is a structured **expert system**:
- **Deterministic Expert Engine**: Evaluates symptoms against domain rules, calculates normalized confidence scores, and ranks candidate causes deterministically.
- **Gemini Assistance Layer**: Uses Google Gemini API (`google-genai` SDK) to parse unstructured user problem descriptions and Task Manager screenshots into strict Pydantic JSON schemas. Gemini acts purely as an assistance layer without making final diagnoses.
- **Action Safety Ratings**: Every fix instruction is badged with an explicit safety level (`Safe` 🟢, `Caution` 🟡, `Advanced` 🔴).

---

## 🛠️ Tech Stack

- **Language**: Python 3.11+
- **API Framework**: FastAPI & Uvicorn
- **Data Validation**: Pydantic v2
- **AI Integration**: Google GenAI SDK (`google-genai`)
- **Testing**: Pytest & HTTPX TestClient

---

## ✅ Completed Work

- [x] **FastAPI Backend Setup**: Direct routing under `app/api/` and health check (`GET /health`).
- [x] **Flagship Domain**: Performance / Freezing diagnostic rule engine (`knowledge_base/performance.py`).
- [x] **Deterministic Engine**: Cause evaluator, score ranker, and explanation generator (`app/expert_engine/`).
- [x] **Safety Ratings**: Explicit `Safe`, `Caution`, and `Advanced` safety badging on all fix actions.
- [x] **Gemini Assistance Layer**: Natural-language text parsing (`POST /api/diagnostic/parse-text`) and Task Manager screenshot OCR parsing (`POST /api/diagnostic/parse-screenshot`) with minimal token response schemas.
- [x] **Handoff Pipeline**: `POST /api/diagnostic/evaluate` automatically merges Gemini-extracted observations with user inputs and evaluates them through the expert engine.
- [x] **Automated Tests**: Pytest test suite (24 unit tests covering rule evaluation, cause ranking, safety levels, schema validation, and mocked Gemini NLU/OCR parsing).

---

## 🔍 Supported Symptoms & Causes

### Supported Symptoms
- `high_cpu_usage` (Processor utilization >= 80%)
- `high_ram_usage` (Memory utilization >= 80%)
- `high_disk_usage` (Disk active time >= 85%)
- `general_slowdown` (Overall system lag)
- `app_freezing` (Applications freezing or 'Not Responding')
- `top_process_name` (Name of top resource-consuming process)

### Supported Diagnostic Causes
1. **RAM Exhaustion / Memory Leak** (`cause_ram_exhaustion`)
2. **High CPU Bottleneck / Rogue Process** (`cause_cpu_bottleneck`)
3. **Disk I/O Saturation / HDD Bottleneck** (`cause_disk_saturation`)
4. **Thermal Throttling / Power Plan Constraint** (`cause_thermal_power`)
5. **Background Service / Startup Overload** (`cause_startup_overload`)

---

## 📡 API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| `GET` | `/health` | Health check endpoint |
| `POST` | `/api/diagnostic/parse-text` | Extracts structured observations from user problem text |
| `POST` | `/api/diagnostic/parse-screenshot` | Extracts CPU, RAM, Disk, and top_process_name from Task Manager screenshots |
| `POST` | `/api/diagnostic/evaluate` | Evaluates observations through expert engine & returns ranked causes with fix steps |

---

## ⚙️ Environment Configuration

Create a `.env` file in the backend root by copying `.env.example`:

```bash
cp .env.example .env
```

`.env` variables:
```env
GEMINI_API_KEY=your_actual_gemini_api_key_here
```
*(Note: `GEMINI_MODEL` defaults internally to `gemini-2.5-flash`)*

---

## 🏃 How to Run Locally

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Start FastAPI Server**:
   ```bash
   uvicorn app.main:app --reload
   ```
   The API will be available at `http://127.0.0.1:8000`.

3. **Run Automated Tests**:
   ```bash
   pytest tests -v
   ```

---

## 🤝 Expectations for Frontend Teammate

The frontend teammate will build a Progressive Web App (PWA) using **React + TypeScript + Vite + Tailwind CSS** that connects to these backend APIs:

- **Problem Intake UI**: Natural language text entry for describing computer slowness.
- **Task Manager Screenshot Uploader**: Drag-and-drop screenshot submission.
- **Diagnostic Progress & Questions**: Render extracted observations and interactive symptom questions.
- **Ranked Cause & Explanation View**: Display ranked diagnoses with confidence scores and reasoning.
- **Safety-Labelled Fix Guides**: Render step-by-step fix guides badged with `Safe`, `Caution`, or `Advanced` labels.
- **Resolution Verification Loop**: Interactive buttons to confirm whether a fix resolved the issue or to move to the next cause.
- **Future QR / Share Session UI**: UI components for cross-device QR code session transfer (when backend persistence is added).

---

## 📌 Current Project Status & Planned Work

> [!NOTE]
> The project is actively under development. Currently, the core backend expert system for **Performance / Freezing** is complete and fully tested.

**Planned for Future Releases**:
- 🔄 **Boot Failure / Slow Startup** domain
- 🌐 **Network / Connectivity** domain
- 🗄️ **Supabase PostgreSQL** session persistence & diagnostic history
- 📱 **QR Code Cross-Device Session Sync**
