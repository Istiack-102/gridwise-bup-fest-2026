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
        raw_directives = interpret_operator_notes(request.operator_notes)
        
        directives = []
        for d in raw_directives:
            directives.append(DirectiveInterpretation(**d))
            
        result = solve_gridwise(request, directives)
        
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
        raise HTTPException(status_code=500, detail=str(e))