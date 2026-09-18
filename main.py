from fastapi import FastAPI, HTTPException
from schemas import OptimizeRequest, OptimizeResponse, DirectiveInterpretation
from llm_agent import interpret_operator_notes
from solver import solve_gridwise

app = FastAPI(title="GridWise Optimization API")

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.post("/optimize-energy", response_model=OptimizeResponse)
def optimize_energy(request: OptimizeRequest):
    try:
        # Step 1: LLM-কে দিয়ে ন্যাচারাল ল্যাঙ্গুয়েজ নোটস প্রসেস করা
        raw_directives = interpret_operator_notes(request.operator_notes)
        
        # Step 2: LLM এর আউটপুট Pydantic দিয়ে ভ্যালিডেট করা (Guardrails)
        directives = []
        for d in raw_directives:
            directives.append(DirectiveInterpretation(**d))
            
        # Step 3: Math Optimizer দিয়ে ২৪ ঘণ্টার বেস্ট প্ল্যান বের করা
        result = solve_gridwise(request, directives)
        
        # Step 4: ফাইনাল আউটপুট রিটার্ন করা
        return OptimizeResponse(
            scenario_id=request.scenario_id,
            directive_interpretation=directives,
            hourly_plan=result["hourly_plan"],
            total_grid_kwh=result["total_grid_kwh"],
            total_cost_bdt=result["total_cost_bdt"],
            peak_grid_kwh=result["peak_grid_kwh"],
            plan_summary="LLM successfully extracted directives. Math optimizer generated the lowest cost schedule complying with all constraints."
        )
    except Exception as e:
        # সিস্টেম ক্র্যাশ না করে সেফ ফেলিউর রিটার্ন করবে
        raise HTTPException(status_code=500, detail=str(e))