# SkillBridge Career Navigator- Scenario 2

 **Candidate Name:** Jhanavi Agarwal
 
 **Scenario Chosen:** Skill-Bridge Career Navigator
 
 **Estimated Time Spent:** 4 hours

## Demo

https://vimeo.com/1175468537?share=copy&fl=sv&fe=ci 

## Quick Start

**Prerequisites:** Python 3.11+, Node 18+, Anthropic API key

**Run Commands:**

```bash
# Backend
cd skillbridge
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
uvicorn backend.main:app --reload --port 8000

# Frontend
cd skillbridge/frontend
npm install && npm run dev
```
Open http://localhost:5173

**Test Commands:**

```bash
cd skillbridge && pytest tests/ -v
```

Swagger UI: http://localhost:8000/docs

---

## Problem Understanding

Students and early-career professionals face a consistent gap between what they know and what job postings require. A typical listing demands 8–12 technical skills, but candidates have no structured way to determine which of those gaps are critical, which are learnable quickly, and what the realistic timeline is to become competitive. Most people compare listings to their resume by eye, which misses semantic equivalences ("React.js" vs "React"), provides no learning priority, and offers zero actionable next steps.

SkillBridge addresses this by running a two-stage analysis. A deterministic engine computes exact skill matches using set intersection. Then an AI layer enhances the result with priority reasoning, semantic skill matching, and a personalized career narrative. The output is a week-by-week learning roadmap with specific course recommendations, milestone checkpoints, and a time estimate — turning a vague "skills gap" into a concrete plan.

**Target users:** Recent graduates comparing their profile against target roles, career switchers identifying transferable skills, and mentors looking for data-backed guidance for their mentees.


## Technical Approach

### Architecture: Deterministic-First, AI-Enhances

Every analysis starts with Python set operations — intersection for matches, difference for gaps, percentage from required skills only. This deterministic baseline is always correct and always available. The AI receives it as input context, so its job is enhancement (priority reasoning, semantic matching, narrative) rather than computation.

This creates a three-tier fallback:

**Tier 1 — AI available and confident:** Full enhanced analysis with semantic skill equivalence detection, priority reasoning with explanations, and a multi-paragraph personalized narrative.

**Tier 2 — AI available but uncertain:** A `<fallback_instruction>` block embedded in the prompt tells the model to default priorities to "important" rather than "critical," recommend official documentation instead of fabricating course names, and self-report confidence via the `confidence_note` field.

**Tier 3 — AI unreachable:** The rule-based engine maps each missing skill to a course from a 54-skill static taxonomy, generates a template narrative, and sets `fallback_used: true` so the frontend shows a warning banner. The user always gets a useful result.

### Why Direct API Over LangChain

The AI interaction is a single structured API call per endpoint. No chains, no agents, no multi-step workflows. This means every failure is a standard HTTP error with a status code, the prompt lives in one readable file (`prompts/templates.py`), and the project installs with five runtime dependencies. For a time-constrained project where a reviewer will `git clone && pip install`, clarity and reliability take priority over framework abstractions.

### Services Layer Separation

Route handlers own HTTP concerns (request parsing, status codes). Service modules own business logic (AI calls, fallback decisions). This separation means the test suite can exercise the full API flow through HTTP, while individual services like `fallback.py` can be tested in isolation.

### Tech Stack

| Layer | Choice | Reasoning |
|-------|--------|-----------|
| Backend | FastAPI (async), Pydantic v2 | Native async, built-in validation, auto-generated Swagger docs |
| AI | Anthropic API direct (claude-sonnet-4-20250514) | Single call pattern, no framework overhead |
| HTTP Client | httpx | Async-native, clean timeout handling |
| Frontend | React 18, Vite, Tailwind CSS | Fast dev server, utility-first styling |
| Testing | pytest + FastAPI TestClient | Synchronous test client for async endpoints |
| Data | Synthetic JSON, in-memory store | No database setup needed, meets "synthetic data only" requirement |

---

## Features

### Core Flow (Create → View → Analyze → Roadmap)
- Create new candidate profiles or use 6 pre-seeded profiles with diverse backgrounds
- Browse and filter 12 job descriptions across 3 roles × 3 seniority levels
- Edit skills on existing profiles before analysis
- Skill gap analysis with match percentage, priority breakdown, and seniority fit assessment
- Career roadmap with AI narrative, course recommendations, milestones, and time estimate

### AI Integration + Fallback
- Anthropic Claude API for priority reasoning, semantic skill matching, and narrative generation
- Rule-based fallback using 54-skill taxonomy when AI is unavailable
- `fallback_used` flag in every response, surfaced as a yellow warning banner in the UI
- Health check endpoint polled every 30 seconds, displayed as a live status indicator in the navbar

### Interview Prep
- AI-generated interview questions targeting specific skill gaps
- Questions contextualized to the target job, not generic
- Difficulty levels (hard/medium/easy) mapped to skill priority
- Collapsible "What interviewers look for" hints per question

### Data Safety
- All candidate and job data is synthetic — no real personal information
- Sample CSV included (`data/sample_profiles.csv`) for import/export demonstration
- API keys loaded from `.env` file, never committed (`.env.example` provided)

---

## Testing

Four tests covering the scoring pillars:

| Test | What It Validates | Pillar |
|------|-------------------|--------|
| `test_happy_path_gap_analysis` | Profile creation → gap analysis → valid match data | Technical Rigor |
| `test_happy_path_full_roadmap` | Full pipeline → courses, milestones, narrative present | Prototype Quality |
| `test_zero_skill_match_edge_case` | 0% match returns 200 (not 500), graceful degradation | Responsible AI |
| `test_input_validation_empty_skills` | Empty skills list → 422 rejection | Technical Rigor |

```
$ pytest tests/ -v
tests/test_skillbridge.py::test_happy_path_gap_analysis        PASSED
tests/test_skillbridge.py::test_happy_path_full_roadmap        PASSED
tests/test_skillbridge.py::test_zero_skill_match_edge_case     PASSED
tests/test_skillbridge.py::test_input_validation_empty_skills  PASSED
4 passed in 0.25s
```

---

## Data

| File | Contents |
|------|----------|
| `data/resumes.json` | 6 synthetic candidate profiles (fresh grad, bootcamp grad, career switcher, self-taught, PM→tech, strong new grad) |
| `data/jobs.json` | 12 job descriptions across Cloud Engineer, Frontend Developer, Security Analyst × junior/mid/senior |
| `data/courses.json` | 18 curated learning resources mapped to job skills |
| `data/fallback_skill_taxonomy.json` | 54 skill→course mappings for rule-based recommendations |
| `data/sample_profiles.csv` | CSV export of all profiles (pipe-separated skills) |

---

## AI Disclosure

**Did you use an AI assistant?** Yes — Claude (Anthropic) for architecture design assistance, code generation, and synthetic data creation.

**Runtime model:** claude-sonnet-4-20250514 via direct API integration.

**How did you verify suggestions?** Every generated file was read, understood, and tested against the running server. All 4 pytest tests validate correctness. Every API endpoint was smoke-tested via curl before frontend integration.

**One example of a suggestion I rejected:** Claude suggested a LangGraph stateful agent workflow for multi-step analysis. I rejected it — it added framework debugging risk, a dozen transitive dependencies, and no evaluator-visible benefit. Replaced with a clean async service pattern that is easier to test, debug, and review.

---

## Tradeoffs & Prioritization

**What I cut:**

- GitHub profile parser for auto-populating skills — 2+ hours for a feature synthetic data demonstrates equally well
- User authentication and persistent storage — in-memory store resets on restart but is sufficient for demo
- Chart-based skill visualization — green/red pill layout communicates the same information without a charting dependency

**What I would build next:**

- Resume PDF parser using Claude's document API — upload a resume instead of entering skills manually
- GitHub URL input — infer skills from repository languages and README content
- Job description paste field — analyze any real JD, not just pre-loaded ones
- Side-by-side comparison — analyze one profile against multiple jobs simultaneously
- Skill trend indicators — badge each missing skill with demand frequency across the dataset
- Persistent PostgreSQL database with user accounts
- Embeddings-based semantic matching for the fallback engine

**Known limitations:**

- In-memory storage resets on server restart; only pre-seeded profiles persist from JSON
- Semantic skill matching depends on AI availability; fallback uses exact string matching
- Course recommendations come from a static taxonomy, not a live catalog
- Dataset covers three role categories; expanding requires additional synthetic data
