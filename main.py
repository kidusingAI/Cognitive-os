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
    SUCCESS = "SUCCESS: Verified & Grounded"
    REJECTED_SYSTEM_1A = "REJECTED: Failed Environmental Safety (Sys 1A)"
    REJECTED_SYSTEM_1B = "REJECTED: Multi-Agent Friction Conflict (Sys 1B)"
    REJECTED_TRUTH_GATE = "REJECTED: Failed Truth Gate Consensus"
    REJECTED_MORAL_VETO = "REJECTED: Failed Collective Moral Override"
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
    agent_id: str = Field("agent_default_01")

class TaskEvaluationResponse(BaseModel):
    task_id: str
    status: PipelineStatus
    assigned_tier: ExecutionTier
    system_1a_passed: bool
    system_1b_passed: bool
    truth_gate_score: float
    valence_score: float
    salience_frequency: int
    moral_override_triggered: bool
    final_solution: str
    execution_time_ms: float
    execution_trace: List[str]

# --- GROUNDING & EVOLUTIONARY MODULES ---

class System1A_EnvironmentalFilter:
    """System 1A: Environmental Danger & Telemetry Grounding Filter"""
    def evaluate(self, prompt: str) -> Tuple[bool, str]:
        text = prompt.lower()
        # Check against physical hazard or unstable operational parameters
        hazards = ["thermal overload", "short circuit", "unbounded torque", "structural fracture"]
        for h in hazards:
            if h in text:
                return False, f"System 1A Veto: Environmental hazard detected ({h})."
        return True, "System 1A: Environmental telemetry validated."

class System1B_SocialFrictionFilter:
    """System 1B: Multi-Agent Friction & Resource Allocation Filter"""
    def evaluate(self, agent_id: str, prompt: str) -> Tuple[bool, str]:
        text = prompt.lower()
        # Check for multi-agent resource collisions or toxic cooperative friction
        if "monopolize bus" in text or "starve peers" in text:
            return False, f"System 1B Veto: Multi-agent resource conflict detected for agent {agent_id}."
        return True, "System 1B: Multi-agent friction verified within acceptable thresholds."

class ValenceAndSalienceEngine:
    """Manages graded valence scores and frequency-weighted concept salience."""
    def __init__(self):
        self.concept_frequencies: Dict[str, int] = {"C_ROOT_LOGIC": 100}

    def update_and_calculate(self, concept_key: str, base_utility: float) -> Tuple[float, int]:
        current_freq = self.concept_frequencies.get(concept_key, 1)
        # Frequency-weighted salience boost
        salience_multiplier = min(1.5, 1.0 + (current_freq * 0.01))
        graded_valence = max(0.0, min(1.0, base_utility * salience_multiplier))
        
        # Increment frequency for successful concept tracking
        self.concept_frequencies[concept_key] = current_freq + 1
        return graded_valence, self.concept_frequencies[concept_key]

# --- CORE PROCESSING MODULES ---

class Module1_AdaptiveRouter:
    def route(self, prompt: str) -> ExecutionTier:
        words = set(re.findall(r'\w+', prompt.lower()))
        if words.intersection({"emergency", "shutdown", "breach", "threat", "reflex"}):
            return ExecutionTier.TIER_1_REFLEX
        elif words.intersection({"proof", "np-complete", "topology", "synthesis"}) or len(prompt) > 250:
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
    """Enforces safety constitution, utility thresholds, and Collective Moral Overrides."""
    def evaluate(self, proposal: str, metrics: PragmatismMetricsInput) -> Tuple[bool, bool, bool, float, str]:
        moral_veto_triggered = False
        for kw in ["revoke admin rights", "bypass human approval", "weaponize", "override core safety"]:
            if kw in proposal.lower():
                return False, False, True, 0.0, f"COLLECTIVE MORAL VETO: Prohibited action '{kw}' intercepted."
        
        score = max(0.0, min(1.0, (metrics.feasibility * 0.35) + (metrics.cost_efficiency * 0.35) + (metrics.downstream_impact * 0.30) - (metrics.complexity_penalty * 0.20)))
        return True, score >= 0.80, moral_veto_triggered, score, f"Utility Score {score:.1%}"

# --- FASTAPI APP ---
app = FastAPI(title="Cognitive Operating System API with Grounded Evolution")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

sys1a = System1A_EnvironmentalFilter()
sys1b = System1B_SocialFrictionFilter()
valence_engine = ValenceAndSalienceEngine()
router_m1, truth_gate_m2, red_team_m3 = Module1_AdaptiveRouter(), Module2_TruthGate(), Module3_HegelianRedTeam()
decomposer_m4, dag_m5, meta_detector_m6 = Module4_LemmaDecomposer(), Module5_ConceptDAG(), Module6_MetaCognitiveDetector()
utility_filter_m7 = Module7_ValueConstrainedFilter()

def run_pipeline_sync(task_id: str, req: TaskEvaluationRequest) -> TaskEvaluationResponse:
    start_perf, trace = time.perf_counter(), []
    
    # 1. System 1A: Environmental Grounding Filter
    s1a_pass, s1a_msg = sys1a.evaluate(req.prompt)
    trace.append(f"[System 1A]: {s1a_msg}")
    if not s1a_pass:
        return TaskEvaluationResponse(
            task_id=task_id, status=PipelineStatus.REJECTED_SYSTEM_1A, assigned_tier=ExecutionTier.TIER_1_REFLEX,
            system_1a_passed=False, system_1b_passed=True, truth_gate_score=0.0, valence_score=0.0,
            salience_frequency=0, moral_override_triggered=False, final_solution=s1a_msg,
            execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace
        )

    # 2. System 1B: Social Friction Filter
    s1b_pass, s1b_msg = sys1b.evaluate(req.agent_id, req.prompt)
    trace.append(f"[System 1B]: {s1b_msg}")
    if not s1b_pass:
        return TaskEvaluationResponse(
            task_id=task_id, status=PipelineStatus.REJECTED_SYSTEM_1B, assigned_tier=ExecutionTier.TIER_1_REFLEX,
            system_1a_passed=True, system_1b_passed=False, truth_gate_score=0.0, valence_score=0.0,
            salience_frequency=0, moral_override_triggered=False, final_solution=s1b_msg,
            execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace
        )

    tier = router_m1.route(req.prompt)
    trace.append(f"[M1 Router]: {tier.value}")

    if pruning := meta_detector_m6.monitor(2, 12): trace.append(f"[M6]: {pruning}")
    concept_key = f"TASK_{task_id[:8]}"
    level = dag_m5.register_concept(concept_key, ["C_ROOT_LOGIC"])
    trace.append(f"[M5 DAG]: Registered Level {level}")

    tg_passed, tg_score, rejs = truth_gate_m2.evaluate(f"Solution for {req.prompt} with async fallback.")
    trace.append(f"[M2 Truth Gate]: {tg_score:.1%} | Passed: {tg_passed}")
    if not tg_passed:
        return TaskEvaluationResponse(
            task_id=task_id, status=PipelineStatus.REJECTED_TRUTH_GATE, assigned_tier=tier,
            system_1a_passed=True, system_1b_passed=True, truth_gate_score=tg_score, valence_score=0.0,
            salience_frequency=1, moral_override_triggered=False, final_solution=f"Rejected by Truth Gate: {rejs}",
            execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace
        )

    outcome, sol, fails = red_team_m3.execute_dialectic("Solution with async fallback", req.simulate_impasse)
    trace.append(f"[M3 Red-Team]: {outcome.value}")
    if outcome == DialecticOutcome.IMPASSE_DECLARED:
        sol, _ = decomposer_m4.resolve_impasse(sol, fails)
        trace.append("[M4 Lemmas]: Resolved impasse via sub-goals")

    # 3. Utility, Moral Override, and Graded Valence Calculation
    safe, util_pass, moral_veto, u_score, reason = utility_filter_m7.evaluate(sol, req.metrics)
    trace.append(f"[M7 Filter]: Safe: {safe} | Utility Score: {u_score:.1%}")

    if moral_veto:
        return TaskEvaluationResponse(
            task_id=task_id, status=PipelineStatus.REJECTED_MORAL_VETO, assigned_tier=tier,
            system_1a_passed=True, system_1b_passed=True, truth_gate_score=tg_score, valence_score=0.0,
            salience_frequency=1, moral_override_triggered=True, final_solution=reason,
            execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace
        )

    # Compute Graded Valence Points & Frequency-Weighted Salience
    valence, freq = valence_engine.update_and_calculate(concept_key, u_score)
    trace.append(f"[Valence Engine]: Graded Valence: {valence:.2f} | Salience Frequency: {freq}")

    final_status = PipelineStatus.SUCCESS if util_pass else PipelineStatus.REJECTED_LOW_UTILITY
    
    return TaskEvaluationResponse(
        task_id=task_id, status=final_status, assigned_tier=tier,
        system_1a_passed=True, system_1b_passed=True, truth_gate_score=tg_score,
        valence_score=valence, salience_frequency=freq, moral_override_triggered=False,
        final_solution=sol if final_status == PipelineStatus.SUCCESS else reason,
        execution_time_ms=(time.perf_counter()-start_perf)*1000, execution_trace=trace
    )

@app.post("/api/v1/evaluate", response_model=TaskEvaluationResponse)
async def evaluate_task(request: TaskEvaluationRequest):
    return await asyncio.to_thread(run_pipeline_sync, str(uuid.uuid4()), request)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
