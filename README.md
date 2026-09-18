# GridWise — LLM-Assisted Energy Optimization API

GridWise holo BUP CSE Fest 2026 Hackathon (Online Preliminary)-er jonno toiri kora ekti smart campus energy management API. Ei system-ti natural language operator notes-ke structured directives-e convert kore ebong PuLP Linear Programming solver-er maddhome 24-ghontar shobcheye kom khorocher battery/grid schedule generate kore.

## 🚀 Tech Stack & Architecture
- **Language:** Python 3.12+
- **Framework:** FastAPI
- **LLM Integration:** Groq API (`requests`, auto-detected chat model)
- **Optimization Engine:** PuLP (Linear Programming CBC solver)
- **Data Validation:** Pydantic
- **Pipeline Flow:** Energy Data + Operator Notes ➔ LLM Interpreter ➔ Guardrail Validator ➔ Math Optimizer (PuLP) ➔ Final Validator ➔ API Response

## 📂 Project Structure
```text
BUP fest/
├── main.py          # FastAPI application & endpoints (/health, /optimize-energy)
├── solver.py        # PuLP mathematical optimization logic & constraints
├── llm_agent.py     # Groq API integration & prompt engineering
├── schemas.py       # Pydantic data validation schemas
├── requirements.txt # Project dependencies
├── gitignore.env    # Environment variables (API keys - do not commit secrets)
└── README.md        # Project documentation

⚙️ Installation & Local Quickstart Guide
Follow these steps to set up and run the project locally from a clean environment:

1. Clone the Repository:

Bash
git clone [https://github.com/Istiack-102/gridwise-bup-fest-2026.git](https://github.com/Istiack-102/gridwise-bup-fest-2026.git)
cd gridwise-bup-fest-2026

2. Create and Activate Virtual Environment:

python -m venv venv
source venv/bin/activate 

3. Install Dependencies:

pip install -r requirements.txt

4. Configure Environment Variables:
Create a file named gitignore.env in the root directory and add your Groq API key:

GROQ_API_KEY=gsk_your_actual_api_key_here
(Note: Never commit secret keys or sensitive configuration files to the public repository.)

5. Run the API Server:
uvicorn main:app --reload --host 0.0.0.0 --port 8000

🔌 API Usage & Testing
Once the server is running, you can test the endpoints:

Interactive Documentation (Swagger UI): Open http://localhost:8000/docs in your browser.

Health Check Endpoint:

curl -X GET http://localhost:8000/health
Optimization Endpoint (POST /optimize-energy):
Send a JSON payload adhering to the exact schema defined in the challenge statement.

🛡️ LLM Role, Guardrails & Solver Details
LLM Role: Interprets unstructured operator notes into strict structured directives (solar_reduction, minimum_battery_reserve, no_charge_window, no_discharge_window, max_grid_window, no_op).

Guardrails: Validates LLM output deterministically before passing constraints to the PuLP solver to prevent invalid ranges, incorrect hour indices, or hallucinations.

Optimizer: Minimizes total grid cost (total_cost_bdt) under strict hourly energy balance, battery bounds, rate limits, and end-of-day battery neutrality (initial_energy_kwh == final_energy_kwh).

🐳 Docker Fallback Execution
To run the application using Docker:

docker build -t gridwise-api:latest .
docker run -p 8000:8000 -e GROQ_API_KEY=your_key gridwise-api:latest
Public Docker Hub Image Reference: istiack102/gridwise-api:latest

🏆 Team & Event
Event: BUP CSE Fest 2026 · Hackathon · Online Preliminary

Team Members:

MD Istiack Ahmed (Bangladesh University of Professionals)

MD Nokibur Rahman (Bangladesh University of Professionals)

MD Sabbir Hossion (Bangladesh University of Professionals)

Abdus Salam Gifari (Bangladesh University of Professionals)

