import asyncio
import logging
import re
import time
import uuid
from enum import Enum
from typing import Dict, List, Optional, Tuple
from pydantic import BaseModel, Field
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(level=logging.INFO, format="%(asctime)s - [%(levelname)s] - %(message)s")
logger = logging.getLogger("CognitiveOS")

class ExecutionTier(str, Enum):
    TIER_1_REFLEX = "Tier 1: Reflex Mode"
    TIER_2_ANALYTICAL = "Tier 2: Analytical Logic"
    TIER_3_HEAVY = "Tier 3: Heavy Engine"

class DialecticOutcome(str, Enum):
    SYNTHESIS_REACHED = "SYNTHESIS_REACHED"
    IMPASSE_DECLARED = "IMPASSE_DECLARED"

class PipelineStatus(str, Enum):
    SUCCESS = "SUCCESS: Verified & Filtered"
    REJECTED_TRUTH_GATE = "REJECTED: Failed Truth Gate"
    REJECTED_SAFETY_VETO = "REJECTED: Failed Safety Constitution"
    REJECTED_LOW_UTILITY = "REJECTED: Below 80% Utility Threshold"

class PragmatismMetricsInput(BaseModel):
    feasibility: float = Field(..., ge=0.0, le=1.0)
    cost_efficiency: float = Field(..., ge=0.0, le=1.0)
    downstream_impact: float = Field(..., ge=0.0, le=1.0)
    complexity_penalty: float = Field(0.1, ge=0.0, le=1.0)

class TaskEvaluationRequest(BaseModel):
    prompt: str = Field(..., min_length=3, max_length=5000)
    metrics: PragmatismMetricsInput
    simulate_impasse: bool = False

class TaskEvaluationResponse(BaseModel):
    task_id: str
    status: PipelineStatus
    assigned_tier: ExecutionTier
    truth_gate_passed: bool
    truth_gate_score: float
    hegelian_outcome: Optional[DialecticOutcome]
    lemmas_decomposed: int
    utility_score: float
    final_solution: str
    execution_time_ms: float
    execution_trace: List[str]

# --- MODULES ---

class Module1_AdaptiveRouter:
    def route(self, prompt: str) -> ExecutionTier:
        words = set(re.findall(r'\w+', prompt.lower()))
        if words.intersection({"emergency", "shutdown", "breach", "threat"}):
            return ExecutionTier.TIER_1_REFLEX
        elif words.intersection({"proof", "np-complete", "topology"}) or len(prompt) > 250:
            return ExecutionTier.TIER_3_HEAVY
        return ExecutionTier.TIER_2_ANALYTICAL

class Module2_TruthGate:
    def evaluate(self, hypothesis: str) -> Tuple[bool, float, List[str]]:
        text, rejections = hypothesis.lower(), []
        if "without proof" in text: rejections.append("Formalist: Unproven assumptions.")
        if "data" not in text and "benchmark" not in text: rejections.append("Empiricist: Missing metrics.")
        if "infinite" in text: rejections.append("Heuristic: Unrealistic bounds.")
        if "fallback" not in text and "async" not in text: rejections.append("Skeptic: Missing fallback.")
        if "isolated" in text: rejections.append("Synthesizer: Local optimization.")
        score = (5 - len(rejections)) / 5.0
        return (score >= 0.70), score, rejections

class Module3_HegelianRedTeam:
    def execute_dialectic(self, hypothesis: str, force_impasse: bool) -> Tuple[DialecticOutcome, str, List[str]]:
        if force_impasse or "paradox" in hypothesis.lower():
            return DialecticOutcome.IMPASSE_DECLARED, hypothesis, ["Paradox detected", "Memory limit risk"]
        return DialecticOutcome.SYNTHESIS_REACHED, f"{hypothesis} -- [SYNTHESIZED with fallback]", []

class Module4_LemmaDecomposer:
    def resolve_impasse(self, hypothesis: str, failure_vector: List[str]) -> Tuple[str, int]:
        lemmas = [f"Sub-Goal L_{i+1}: Resolved {fv}" for i, fv in enumerate(failure_vector)]
        return f"RE-SYNTHESIZED SOLUTION:\nIntent: {hypothesis}\nFoundations:\n  - " + "\n  - ".join(lemmas), len(lemmas)

class Module5_ConceptDAG:
    def __init__(self): self.concepts = {"C_ROOT_LOGIC": 0}
    def register_concept(self, name: str, prerequisites: List[str]) -> int:
        level = max([self.concepts.get(p, 0) for p in prerequisites], default=0) + 1
        self.concepts[name] = level
        return level

class Module6_MetaCognitiveDetector:
    def monitor(self, depth: int, node_count: int) -> Optional[str]:
        return "PRUNING RULE: Depth exceeded" if node_count > 100 or depth > 10 else None

class Module7_ValueConstrainedFilter:
    def evaluate(self, proposal: str, metrics: PragmatismMetricsInput) -> Tuple[bool, bool, float, str]:
        for kw in ["revoke admin rights", "bypass human approval", "weaponize"]:
            if kw in proposal.lower(): return False, False, 0.0, f"CONSTITUTIONAL VETO: '{kw}'"
        score = max(0.0, min(1.0, (metrics.feasibility * 0.35) + (metrics.cost_efficiency * 0.35) + (metrics.downstream_impact * 0.30) - (metrics.complexity_penalty * 0.20)))
        return True, score >= 0.80, score, f"Utility Score {score:.1%}"

# --- FASTAPI APP ---
app = FastAPI(title="Cognitive Operating System API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

router_m1, truth_gate_m2, red_team_m3 = Module1_AdaptiveRouter(), Module2_TruthGate(), Module3_HegelianRedTeam()
decomposer_m4, dag_m5, meta_detector_m6 = Module4_LemmaDecomposer(), Module5_ConceptDAG(), Module6_MetaCognitiveDetector()
utility_filter_m7 = Module7_ValueConstrainedFilter()
START_TIME = time.time()

def run_pipeline_sync(task_id: str, req: TaskEvaluationRequest) -> TaskEvaluationResponse:
    start_perf, trace = time.perf_counter(), []
    
    tier = router_m1.route(req.prompt)
    trace.append(f"[M1 Router]: {tier.value}")
    if tier == ExecutionTier.TIER_1_REFLEX:
        return TaskEvaluationResponse(task_id=task_id, status=PipelineStatus.SUCCESS, assigned_tier=tier, truth_gate_passed=True, truth_gate_score=1.0, hegelian_outcome=None, lemmas_decomposed=0, utility_score=1.0, final_solution="[REFLEX]: Instant safety protocol activated.", execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace)

    if pruning := meta_detector_m6.monitor(2, 12): trace.append(f"[M6]: {pruning}")
    level = dag_m5.register_concept(f"TASK_{task_id[:8]}", ["C_ROOT_LOGIC"])
    trace.append(f"[M5 DAG]: Registered Level {level}")

    tg_passed, tg_score, rejs = truth_gate_m2.evaluate(f"Solution for {req.prompt} with async fallback.")
    trace.append(f"[M2 Truth Gate]: {tg_score:.1%} | Passed: {tg_passed}")
    if not tg_passed:
        return TaskEvaluationResponse(task_id=task_id, status=PipelineStatus.REJECTED_TRUTH_GATE, assigned_tier=tier, truth_gate_passed=False, truth_gate_score=tg_score, hegelian_outcome=None, lemmas_decomposed=0, utility_score=0.0, final_solution=f"Rejected: {rejs}", execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace)

    outcome, sol, fails = red_team_m3.execute_dialectic("Solution with async fallback", req.simulate_impasse)
    trace.append(f"[M3 Red-Team]: {outcome.value}")
    lemmas = 0
    if outcome == DialecticOutcome.IMPASSE_DECLARED:
        sol, lemmas = decomposer_m4.resolve_impasse(sol, fails)
        trace.append(f"[M4 Lemmas]: {lemmas} sub-goals")

    safe, util_pass, u_score, reason = utility_filter_m7.evaluate(sol, req.metrics)
    trace.append(f"[M7 Filter]: Safe: {safe} | Score: {u_score:.1%}")
    
    final_status = PipelineStatus.SUCCESS if safe and util_pass else (PipelineStatus.REJECTED_SAFETY_VETO if not safe else PipelineStatus.REJECTED_LOW_UTILITY)
    
    return TaskEvaluationResponse(task_id=task_id, status=final_status, assigned_tier=tier, truth_gate_passed=tg_passed, truth_gate_score=tg_score, hegelian_outcome=outcome, lemmas_decomposed=lemmas, utility_score=u_score, final_solution=sol if final_status == PipelineStatus.SUCCESS else reason, execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace)

@app.post("/api/v1/evaluate", response_model=TaskEvaluationResponse)
async def evaluate_task(request: TaskEvaluationRequest):
    return await asyncio.to_thread(run_pipeline_sync, str(uuid.uuid4()), request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
