# GridWise — LLM-Assisted Energy Optimization API

GridWise holo BUP CSE Fest 2026 Hackathon (Online Preliminary)-er jonno toiri kora ekti smart campus energy management API. Ei system-ti natural language operator notes-ke structured directives-e convert kore ebong PuLP Linear Programming solver-er maddhome 24-ghontar shobcheye kom khorocher battery/grid schedule generate kore.

## 🚀 Tech Stack
- **Language:** Python 3.12+
- **Framework:** FastAPI
- **LLM Integration:** Groq API (`requests`)
- **Optimization Engine:** PuLP (Linear Programming CBC solver)
- **Data Validation:** Pydantic

## 📂 Project Structure

```text
BUP fest/
├── main.py          # FastAPI application & endpoints
├── solver.py        # PuLP mathematical optimization logic
├── llm_agent.py     # Groq API integration & prompt engineering
├── schemas.py       # Pydantic data validation schemas
├── requirements.txt # Project dependencies
├── gitignore.env    # Environment variables (API keys)
└── README.md        # Project documentation

## ⚙️ Installation & Setup Guide

1. **Clone the Repository:**

git clone https://github.com/Istiack-102/gridwise-bup-fest-2026.git
cd gridwise-bup-fest-2026



Create and Activate Virtual Environment:

Bash
python -m venv venv
source venv/bin/activate  # Windows-er jonno: venv\Scripts\activate
Install Dependencies:

Bash
pip install -r requirements.txt
Configure Environment Variables:
Project folder-e gitignore.env nam-e ekti file toiri korun ebong apnar Groq API key-ti nicher moto kore din:

Code snippet
GROQ_API_KEY=gsk_your_actual_api_key_here
Run the API Server:

Bash
uvicorn main:app --reload
🔌 API Usage
Server chalu howar por browser-e nicher link-গুলিতে giye API test korte parben:

Interactive Docs (Swagger UI): http://127.0.0.1:8000/docs

Health Check Endpoint: GET /health

Optimization Endpoint: POST /optimize-energy

Sample Request Body (POST /optimize-energy):
JSON
{
  "scenario_id": "SAMPLE-01",
  "operator_notes": [
    "Facilities will wash the rooftop solar panels from noon until 2 PM. During cleaning, usable solar should be treated as roughly 25% of the forecast."
  ],
  "hours": [
    { "hour": 0, "demand_kwh": 90, "solar_kwh": 0, "tariff_bdt_per_kwh": 6 }
  ],
  "battery": {
    "capacity_kwh": 220,
    "initial_energy_kwh": 110,
    "minimum_energy_kwh": 40,
    "max_charge_kwh_per_hour": 50,
    "max_discharge_kwh_per_hour": 50
  }
}
🏆 Team & Event
Event: BUP CSE Fest 2026 · Hackathon · Online Preliminary

Developer: 
1. MD Istiack Ahmed (Bangladesh University of Professionals)
2. MD Nokibur Rahman (Bangladesh University of Professionals)
3. MD Sabbir Hossion (Bangladesh University of Professionals)
4. Abdus Salam Gifari (Bangladesh University of Professionals)# gridwise-bup-fest-2026
