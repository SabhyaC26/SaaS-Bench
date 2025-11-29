# SaaS-Bench Implementation Plan

## Overview

SaaS-Bench is a benchmark for evaluating AI agents on cross-platform enterprise SaaS workflows. The implementation follows a four-phase approach, building from foundation to full validation.

---

## Phase 1: Foundation

### Objective
Scrape the web for tutorials provided by Databricks and translate them into workflows for the benchmark.

### Key Deliverables

#### 1. Tutorial Processing Service
Build a service that can:
- **Input**: URLs of tutorials provided by SaaS platforms (specifically Databricks)
- **Processing**: Break down tutorials into succinct step-by-step workflows
- **Output**: Translate workflows into realistic workspace states for agent testing

**Technical Stack:**
- OpenAI SDK client with Grok API key for LLM calls
- Web scraping capabilities for tutorial extraction
- Workflow parsing and state generation logic

#### 2. Databricks Domain Components

Based on scraped examples and processed workflows, create:

**State Schema:**
- Pydantic models representing Databricks resources
- Coverage for: clusters, jobs, notebooks, Unity Catalog, permissions
- Pure data structures with no external dependencies

**API Tools:**
- List of API tools derived from scraped tutorial examples
- Each tool as a pure Python function: `(State, Arguments) → (State', Response)`
- Tool specifications with parameters and return types

**Policy Document:**
- Operational rules and constraints
- Best practices from Databricks documentation
- Organizational policies (naming conventions, compute usage, data quality, security)

**Environment Class:**
- Orchestrates agent-user-API interaction
- Manages state transitions
- Handles tool execution

**Basic Evaluation:**
- Goal state comparison logic
- Success/failure determination
- Foundation for milestone and minefield detection

### Success Criteria
- Service successfully processes at least 10 Databricks tutorials
- Generated workflows are realistic and executable
- State schema captures essential Databricks resources
- API tools cover common operations from tutorials
- Basic evaluation can determine task success

---

## Phase 2: Multi-Platform [Depends on Phase 1 Findings]

### Objective
Add remaining platforms and cross-platform tasks.

### Key Deliverables

#### 1. Snowflake Domain
- **State Schema**: warehouses, databases, schemas, tables, access control
- **API Tools**: Snowflake-specific operations
- **Policy Document**: Snowflake best practices and constraints

#### 2. Salesforce Domain
- **State Schema**: objects, fields, triggers, flows, reports
- **API Tools**: Salesforce CRM operations
- **Policy Document**: Salesforce configuration policies

#### 3. Cross-Platform Integration
- **Cross-Platform State Container**: Unified state model spanning multiple platforms
- **Inter-Platform Dependencies**: Handle workflows that span 2-3 platforms
- **Cross-Platform Validation**: Ensure state consistency across platforms

#### 4. Task Library
- **10-15 Tier 3 Tasks**: Cross-platform workflows
- Each task involves 2-3 platforms
- 5-15 API calls per task
- Mostly cooperative user interactions
- Rare failure scenarios

### Success Criteria
- All three platforms (Databricks, Snowflake, Salesforce) fully implemented
- Cross-platform state management working correctly
- At least 10 Tier 3 tasks validated and executable
- Clear documentation of inter-platform dependencies

---

## Phase 3: Difficulty Scaling

### Objective
Implement adversarial features and harder tasks to create challenging evaluation scenarios.

### Key Deliverables

#### 1. User Persona System
- **Configurable Adversarial Behaviors**:
  - Unreliable information provision
  - Changing requirements mid-task
  - Ambiguous confirmations
  - Impatient responses
- **Persona Configuration**: Reliability score, patience level, expertise level
- **LLM-Based Simulation**: Temperature set to 1.0 for diversity

#### 2. Failure Injection Middleware
- **Failure Types**:
  - Rate limits
  - Permission errors
  - Partial failures
  - Transient outages
  - Service unavailability
- **Injection Scheduling**: Trigger-based and probabilistic injection
- **Recovery Testing**: Evaluate agent's ability to handle and recover from failures

#### 3. Dynamic Constraint Engine
- **Runtime Constraints**:
  - Budget limits
  - Resource quotas
  - Time-based restrictions
  - Permission boundaries
- **Constraint Validation**: Continuous monitoring during task execution
- **Violation Detection**: Minefield system for critical constraint violations

#### 4. Advanced Task Library
- **15-20 Tier 4 Tasks**:
  - 2-3 platforms per task
  - 10-20 API calls
  - Unreliable user personas
  - Occasional failures injected
- **5-10 Tier 5 Tasks**:
  - 3-4 platforms per task
  - 15-30 API calls
  - Adversarial user behavior
  - Frequent failures
  - Multi-actor workflows

### Success Criteria
- User simulator produces realistic adversarial behaviors
- Failure injection reliably triggers at specified points
- Constraint violations properly detected
- Tier 4-5 tasks are significantly more challenging than Tier 1-3
- Clear difficulty gradient observable across tiers

---

## Phase 4: Validation & Baseline

### Objective
Validate the benchmark and establish baseline performance metrics for state-of-the-art agents.

### Key Deliverables

#### 1. Baseline Agent Evaluation
Run comprehensive evaluation on:
- **GPT-4o**: Latest OpenAI flagship model
- **Claude 3.5 Sonnet**: Latest Anthropic model
- Other competitive models as available

**Metrics to Compute:**
- `pass^1`: Single-trial success rate
- `pass^4`: Four-trial consistency
- `pass^8`: Eight-trial consistency
- Per-tier performance breakdown
- API call efficiency metrics

#### 2. Failure Analysis
- **Categorize Failure Modes**:
  - Policy violations
  - API usage errors
  - Cross-platform coordination failures
  - Constraint violations
  - Recovery failures
- **Causal Attribution**: Identify root causes
- **Pattern Detection**: Common failure patterns across agents

#### 3. Benchmark Calibration
Target performance distribution:
- **Tier 1-2**: ~60-80% success rate (baseline competency)
- **Tier 3**: ~40-60% success rate (cross-platform challenge)
- **Tier 4-5**: <30% success rate (adversarial/complex scenarios)

**Calibration Actions:**
- Adjust task difficulty if tiers too easy/hard
- Refine goal states for clarity
- Balance milestone distribution
- Tune failure injection rates

#### 4. Validation Studies
- **Simulation Fidelity**:
  - Documentation review against real platform docs
  - Spot checks with actual platform behavior
  - Expert review by engineers with platform experience
- **Task Quality**:
  - Run each task 40+ times for statistical validity
  - Verify unique outcome distribution
  - Iteratively refine instructions based on failures
  - Ensure no trivial shortcuts exist

### Success Criteria
- SOTA models score **below 50% overall** (ensures challenge)
- Clear **difficulty gradient** across tiers (each tier harder than previous)
- **pass^k drops as k increases** (demonstrates consistency issues)
- Failure categories well-distributed (no single failure mode dominates)
- Expert validation confirms simulation realism

---

## Task Difficulty Tiers

### Tier 1: Single Action
- **Platforms**: 1
- **API Calls**: 1-2
- **User Behavior**: Cooperative
- **Failures**: None
- **Example**: List available catalogs, create a single table

### Tier 2: Multi-Step
- **Platforms**: 1
- **API Calls**: 3-7
- **User Behavior**: Cooperative
- **Failures**: None
- **Example**: Create ETL pipeline with multiple transformations

### Tier 3: Cross-Platform
- **Platforms**: 2-3
- **API Calls**: 5-15
- **User Behavior**: Mostly cooperative
- **Failures**: Rare
- **Example**: Sync data from Snowflake to Databricks, configure Salesforce reporting

### Tier 4: Adversarial
- **Platforms**: 2-3
- **API Calls**: 10-20
- **User Behavior**: Unreliable
- **Failures**: Occasional
- **Example**: Configure pipeline with changing requirements and rate limit handling

### Tier 5: Enterprise
- **Platforms**: 3-4
- **API Calls**: 15-30
- **User Behavior**: Adversarial
- **Failures**: Frequent
- **Example**: Multi-actor workflow with permission conflicts and system outages

---

## Evaluation Methodology

### Primary Metric: Goal State Comparison
- Compare final platform state to annotated goal state
- Objective and reproducible
- Binary success/failure at top level

### Reliability Metric: pass^k
- Probability that ALL k independent trials succeed
- `pass^k = (success_rate)^k`
- Reveals consistency issues as k increases

### Partial Credit: Milestones
- Intermediate checkpoints for long-horizon tasks
- Points awarded for completing sub-goals
- Enables fine-grained performance analysis

### Critical Failures: Minefields
- States that indicate severe violations
- Examples: data leakage, budget overruns, security violations
- Result in immediate task failure regardless of other progress

---

## Technical Architecture

### State Management
- **Pydantic Schemas**: Type-safe state representation
- **Pure Functions**: API tools as `(State, Args) → (State', Response)`
- **Immutable Updates**: State transitions create new state objects
- **No External Dependencies**: State is self-contained data structure

### Simulation Approach
- **State-Machine Model**: Following τ-bench methodology
- **No Real Platform Access**: Simulated environments only
- **Deterministic Core**: API implementations are deterministic
- **Stochastic Layer**: User simulation and failure injection add randomness

### Agent-Environment Interface
- **Turn-Based Execution**: Agent ↔ User ↔ Tools loop
- **Tool Registry**: Available APIs exposed to agent
- **Conversation History**: Full trace for evaluation
- **State Snapshots**: Capture state at each turn for debugging

---

## Research Questions Enabled

1. **Cross-Platform Generalization**: Do agents trained on single-platform tasks transfer to multi-platform workflows?

2. **Failure Recovery**: How do agents handle partial failures mid-workflow?

3. **Constraint Satisfaction**: Can agents respect dynamic constraints (budgets, quotas, permissions)?

4. **User Adversariality**: How does performance degrade with unreliable users?

5. **Consistency**: What architectural choices improve pass^k for higher k?

6. **Efficiency**: Are there tradeoffs between success rate and API call efficiency?

---

## Dependencies Between Phases

```
Phase 1 (Foundation)
    ↓
    ├─→ Phase 2 (Multi-Platform) [depends on Phase 1 findings]
    │       ↓
    │       └─→ Phase 3 (Difficulty Scaling)
    │               ↓
    └───────────────→ Phase 4 (Validation & Baseline)
```

**Key Decision Points:**
- Phase 2 scope may adjust based on Phase 1 tutorial processing results
- Phase 3 difficulty calibration informed by Phase 2 task performance
- Phase 4 may require iteration back to Phase 3 for task refinement

---

## Timeline Considerations

### Phase 1: 3-4 weeks
- Week 1: Tutorial scraping service
- Week 2: State schema and API tools
- Week 3: Environment and evaluation
- Week 4: Testing and refinement

### Phase 2: 4-6 weeks
- Weeks 1-2: Snowflake domain
- Weeks 2-3: Salesforce domain
- Weeks 3-4: Cross-platform integration
- Weeks 4-6: Tier 3 task development and testing

### Phase 3: 4-5 weeks
- Week 1: User persona system
- Week 2: Failure injection middleware
- Week 3: Dynamic constraint engine
- Weeks 4-5: Tier 4-5 task development

### Phase 4: 3-4 weeks
- Week 1: Baseline agent runs
- Week 2: Failure analysis
- Week 3: Calibration and refinement
- Week 4: Validation studies and documentation

**Total Estimated Timeline**: 14-19 weeks

---

## Success Metrics Summary

### Phase 1
✓ 10+ Databricks tutorials successfully processed  
✓ Realistic state schema covers core resources  
✓ API tools executable and correct  
✓ Basic evaluation determines success accurately

### Phase 2
✓ 3 platforms fully implemented  
✓ 10+ cross-platform tasks validated  
✓ State consistency across platforms  
✓ Clear inter-platform dependency handling

### Phase 3
✓ User simulator produces diverse behaviors  
✓ Failure injection works reliably  
✓ 20+ Tier 4-5 tasks created  
✓ Observable difficulty gradient

### Phase 4
✓ SOTA models <50% overall success  
✓ pass^k decreases as k increases  
✓ Expert validation confirms realism  
✓ Clear performance tier stratification

---

## Risk Mitigation

### Technical Risks
- **Simulation Fidelity**: Mitigate with expert review and spot checks
- **API Complexity**: Start simple, iterate based on tutorial patterns
- **State Explosion**: Use focused schemas, avoid over-modeling

### Research Risks
- **Tasks Too Easy**: Phase 4 calibration allows adjustment
- **Tasks Too Hard**: Milestone system provides partial credit signal
- **Benchmark Saturation**: Tiered structure allows adding harder tiers

### Resource Risks
- **Timeline Slippage**: Phases 2-3 are adjustable in scope
- **LLM Costs**: Use efficient models for user simulation
- **Platform Changes**: Document version/date of simulated behavior
