import {
  BarChart,
  Callout,
  Card,
  CardBody,
  CardHeader,
  Code,
  CollapsibleSection,
  Divider,
  Grid,
  H1,
  H2,
  H3,
  Link,
  Pill,
  Row,
  Spacer,
  Stack,
  Stat,
  Swatch,
  Table,
  Text,
  TodoListCard,
  UsageBar,
  useCanvasState,
  useHostTheme,
  useMemo,
  useState,
} from "cursor/canvas";
import type { TableRowTone, TodoItem } from "cursor/canvas";

type TabId = "overview" | "unfinished" | "defects" | "roadmap";
type CategoryFilter = "All" | "Integrations" | "AI & Models" | "Governance & Formal" | "UX & Ops";

interface UnfinishedItem {
  id: string;
  name: string;
  category: Exclude<CategoryFilter, "All">;
  status: "Fixture-Only" | "Deferred" | "Stub / Partial" | "Experimental";
  tone: TableRowTone;
  location: string;
  currentState: string;
  stillNeeded: string;
  evidence: string;
}

interface DefectItem {
  id: string;
  title: string;
  severity: "High" | "Medium" | "Low";
  tone: TableRowTone;
  location: string;
  detail: string;
  remediation: string;
}

const UNFINISHED_FEATURES: UnfinishedItem[] = [
  {
    id: "UF-01",
    name: "Integrations I2–I6 Live Providers (T3, Apify, Scrimba, WorkOS, I6)",
    category: "Integrations",
    status: "Fixture-Only",
    tone: "warning",
    location: "orchestrator/integrations/{t3,apify,scrimba,workos,i6}/",
    currentState:
      "All five integrations ship schemas, gates, and fixture runners only. Live execution explicitly fails closed with deferred messages (T3 live start unavailable without injected transport; Apify call-actor, Scrimba MCP streaming, WorkOS API sync, and I6 live probes all deferred). Only I1 Sentry implements a real HTTPS client, and even there window_hours is ignored (_ = window_hours).",
    stillNeeded:
      "Implement real transports/API clients behind pilot-scoped approval gates: T3 MCP adapter, Apify Actor client, Scrimba MCP stream consumer, WorkOS AuthKit API sync, and live I6 smoke probes. Wire window_hours into Sentry's query filter.",
    evidence:
      "32 of 56 files in orchestrator/integrations/ are stub/fixture/dry-run; only 1 module (transport.py) performs live HTTP.",
  },
  {
    id: "UF-02",
    name: "Specialized Model Pipeline (Levels 0–3)",
    category: "AI & Models",
    status: "Deferred",
    tone: "danger",
    location: "orchestrator/specialized/{service,scoring,lora,gpu}.py",
    currentState:
      "Level 0, Level 1 (LoRA), and Level 2 (single GPU) all evaluate against canned stub_student_answer JSON fixtures (score_stub_student / _score_adapter_stub). N3 hermetic scorecard reports stub_student_rate=1.0 vs retrieval=1.0 (delta 0.000) and recommends defer. Level 3 (48–80GB GPU, Issue #237) is paused/deferred.",
    stillNeeded:
      "Replace stub fixture scoring with a real local inference evaluator (e.g. Ollama / MLX / vLLM) over held-out tasks so L0 vs L1 vs L2 produce real ROI deltas before reconsidering Level 3.",
    evidence:
      "Issue #237 open since 2026-10-22; docs/plans/SPECIALIZED_MODEL_LEVEL_3.md marks Level 3 DEFERRED.",
  },
  {
    id: "UF-03",
    name: "Bend Policy-Lifecycle Formal Proof Spike",
    category: "Governance & Formal",
    status: "Experimental",
    tone: "warning",
    location: "formal/bend/policy-lifecycle/, orchestrator/formal/",
    currentState:
      "PR #279 merged to main on 2026-11-20, but ADR-110 remains Proposed and Issue #278 is still open. P4 (monotone) and P5 (shadow-before-approval) are proved per-step only (not over arbitrary histories). Evidence gates are boolean abstractions; gate order is AST-pinned rather than proved; Lean is unpinned; --strict-laws is not wired into CI.",
    stillNeeded:
      "Captain go/no-go decision on ADR-110; write transitivity lemma to lift P4/P5 to full sequences; fix Finding 001 and add an entry-state law; replace coarse whole-function AST pin with narrower structural check; pin Lean SHA and wire --strict-laws into GitHub Actions.",
    evidence:
      "10 of 11 skipped unit tests in unittest discover are BendEndToEndTests requiring Bend + Lean + COMPASS_BEND_PROOF_ENABLED=1.",
  },
  {
    id: "UF-04",
    name: "Behavior Intelligence Loop Runtime (M46–M54)",
    category: "Governance & Formal",
    status: "Stub / Partial",
    tone: "warning",
    location: "orchestrator/behavior/ (39 files, 4,606 LOC)",
    currentState:
      "Full code stack exists for evaluate, pattern learn, instruction registry, prompt-eval, policy promotion, provenance, and exemplars, split across 6+ separate COMPASS_*_ENABLED gates. However, all runtime directories under .agent/evaluations/behavior/* and .agent/examples/* are completely empty (.gitkeep only), and Finding 001 bypasses policy entry gates.",
    stillNeeded:
      "Fix ensure_policy_for_instruction() bypass (Finding 001), unify or profile-bundle the 6 opt-in gates, and run live dogfood cycles on real workstreams to validate signal quality instead of fixture-only tests.",
    evidence:
      "0 real files in .agent/evaluations/ and .agent/examples/ in the control repository.",
  },
  {
    id: "UF-05",
    name: "Cognitive Core C6 — REA Deep Analysis",
    category: "AI & Models",
    status: "Stub / Partial",
    tone: "warning",
    location: "orchestrator/rea/service.py",
    currentState:
      "Even when an rea / rea-cli binary is detected on PATH, _live_or_unavailable_packet() refuses to invoke it and emits run_mode='live_stub' with '# live execution stub — Captain must approve explicit REA invoke outside CI'.",
    stillNeeded:
      "Implement bounded, allowlisted live REA invocation with timeout/sandbox controls and real observation parsing when Captain opts in.",
    evidence:
      "orchestrator/rea/service.py lines 281–330 hardcode stub emission even when live_available=True.",
  },
  {
    id: "UF-06",
    name: "B4 Automated Repair Loop (FIX -> TEST -> SUBMIT)",
    category: "UX & Ops",
    status: "Stub / Partial",
    tone: "info",
    location: "orchestrator/repair/loop.py",
    currentState:
      "Implements FIND -> PROVE -> dispatch packet JSON only (dispatch_authorized: False). Default allowlist is hardcoded to loganware05/captain-compass-sandbox. Actual code fixing, test execution, and PR submission remain manual/unwired.",
    stillNeeded:
      "Wire supervised child-agent dispatch from repair packets into isolated worktrees, capture test evidence, and open draft PRs against allowlisted repos under Captain approval.",
    evidence:
      "orchestrator/repair/ contains only loop.py (272 LOC); docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md notes live FIX still gated.",
  },
  {
    id: "UF-07",
    name: "N4 Cross-Stack Benchmark Live Arm",
    category: "AI & Models",
    status: "Fixture-Only",
    tone: "warning",
    location: "orchestrator/benchmark/n4/service.py",
    currentState:
      "Baseline vs evidence-informed scorecard simulates outcomes via fixture boosts (simulate_task_result). Even with mode='live', line 213 records 'Live mode evaluate scaffolding only; outcomes still fixture-driven in v1.75.0'. Costs are synthetic proxy units and Verdant.sys is substituted by sandbox.",
    stillNeeded:
      "Implement real benchmark task execution across target product repos with actual test pass rates, token/wall-time metering, and held-out transfer evaluation.",
    evidence:
      "orchestrator/benchmark/n4/service.py lines 120–231.",
  },
  {
    id: "UF-08",
    name: "OpenUI Control Plane Web Surface",
    category: "UX & Ops",
    status: "Stub / Partial",
    tone: "warning",
    location: "orchestrator/openui/, orchestrator/ui/",
    currentState:
      "Python CLI emits OpenUI Lang strings and offers CLI-based plan approve/reject; TypeScript package defines Zod/React widgets. However, there is no running web server or host app rendering live streams, .agent/ui/ is empty, preview.html is a static hardcoded v1.74.0 mockup (SHA 6432c23), and CI never builds or tests orchestrator/ui/.",
    stillNeeded:
      "Add orchestrator/ui/ typecheck and tests to CI, build a lightweight local server/viewer that renders real .agent/ui/*.openui streams, and retire or dynamically generate preview.html.",
    evidence:
      "orchestrator/ui/preview.html lines 47–78; .github/workflows/ci.yml omits npm/tsc checks.",
  },
  {
    id: "UF-09",
    name: "Connected Operations (Track C3 & Track A2 Ledger Automation)",
    category: "Integrations",
    status: "Stub / Partial",
    tone: "info",
    location: "orchestrator/integrations/{ingress,skills_ledger.py,routine.py}",
    currentState:
      "Webhook server returns 503 unless --mode live is passed; Linear skills ledger defaults to placeholder IDs (--mode fixtures); automated M1–M7 milestone transitions (Track A2) and end-to-end issue -> plan -> approve -> dispatch -> review -> ledger orchestration (Track C3) remain unfinished.",
    stillNeeded:
      "Complete automated evidence-driven Linear status transitions (read-only flight recorder) and prove live GitHub webhook + Slack/Linear routine on sandbox before product repos.",
    evidence:
      "docs/plans/NORTHSTAR_CAPTAIN_CONTINUATION_ROADMAP.md lists C3 and A2 as remaining backlog items.",
  },
  {
    id: "UF-10",
    name: "C2 Session Memory Capture Workflow",
    category: "UX & Ops",
    status: "Stub / Partial",
    tone: "info",
    location: "orchestrator/cognitive/session_memory.py",
    currentState:
      "Dual-gated behind COMPASS_BRAIN_ENABLED + COMPASS_SESSION_MEMORY_ENABLED; explicit manual CLI ingest only (northstar brain memory ingest). .agent/session-memory/ is empty in the repo.",
    stillNeeded:
      "Add an opt-in closeout or session-end capture step (preserving secret redaction and non-canonical boundaries) so session memory accumulates without manual boilerplate.",
    evidence:
      "ADR-108 (v1.86.0); 0 files in .agent/session-memory/.",
  },
  {
    id: "UF-11",
    name: "Hosted Vector DB & Live Embedding / Registry Knowledge Store",
    category: "AI & Models",
    status: "Deferred",
    tone: "neutral",
    location: "orchestrator/knowledge/",
    currentState:
      "Local TF-IDF and 32-dim hash-projection FixtureEmbeddingProvider are default. pgvector adapter and OpenAI-compatible HTTP embedder exist in code, but PROJECT_CONTEXT.md notes hosted vector DBs and live embedding/registry HTTP remain deferred operationally; .agent/knowledge/ holds only 3 files.",
    stillNeeded:
      "Run an end-to-end live embedding + pgvector (e.g. Neon) validation against a populated knowledge base or prune unused hosted vector scaffolding if local TF-IDF suffices.",
    evidence:
      "PROJECT_CONTEXT.md line 112; .agent/knowledge/ has 3 real files.",
  },
  {
    id: "UF-12",
    name: "AI Hedge Fund (AHF) Live Safety Controls",
    category: "Governance & Formal",
    status: "Deferred",
    tone: "neutral",
    location: "orchestrator/integrations/ai_hedge_fund/behavioral.py",
    currentState:
      "Research/shadow adapter only. behavioral.py lines 268–279 explicitly state 'Live-mode kill-switch and exposure limits not implemented (research-only)' and fail closed.",
    stillNeeded:
      "Keep live trading denied unless a separate Captain-approved risk architecture introduces hardware/broker kill-switches, position caps, and independent reconciliation.",
    evidence:
      "orchestrator/integrations/ai_hedge_fund/behavioral.py lines 268–279.",
  },
  {
    id: "UF-13",
    name: "XRV Independent Audit Trail & Ops-Verified State",
    category: "Governance & Formal",
    status: "Stub / Partial",
    tone: "info",
    location: "orchestrator/xrv/, docs/plans/XRV_CROSS_REPOSITORY_VALIDATION.md",
    currentState:
      "W1–W3 and Pilots A (TrapHouse), B (bitcoin-data-collector), and C (PrizePicksBot) baseline EERs are merged, plus RedTailEnergy witness. Final exit criterion — 'Independent auditor can reconstruct full cycles incl. ops-verified states' — remains unchecked.",
    stillNeeded:
      "Record post-deploy / ops-verified EER states across pilot repos and run an independent reconstruction drill using northstar evidence validate + assess portfolio.",
    evidence:
      "docs/plans/XRV_CROSS_REPOSITORY_VALIDATION.md line 44 (unchecked).",
  },
];

const DEFECTS_AND_DEBT: DefectItem[] = [
  {
    id: "BUG-01",
    title: "Finding 001: Policy Direct-Entry Bypass of Captain & Evidence Gates",
    severity: "High",
    tone: "danger",
    location: "orchestrator/behavior/policy/promote.py:40-88",
    detail:
      "ensure_policy_for_instruction() docstring promises '(starts at candidate)', but lines 55–72 copy any valid approval_state (including 'proven', 'active', 'approved') straight from the instruction JSON into lifecycle_state without calling promote_policy(). This bypasses Captain approval, shadow reports, prompt-eval reports, and all 17 formally proved Bend transition laws.",
    remediation:
      "Force new policies to initialize in 'candidate' (or reject non-candidate instruction states) and extend formal/bend/policy-lifecycle/LAWS.bend with an entry-state invariant.",
  },
  {
    id: "BUG-02",
    title: "Test Suite Mutates Tracked Git Files & Leaks Temp Directories",
    severity: "High",
    tone: "danger",
    location: "tests/orchestrator/ + .gitignore:70-77",
    detail:
      "Running ./tests/run.sh and unittest discover modifies 5 git-tracked files in-place (LATEST_{baseline,compare,with_evidence}.json and 2 train-metrics.json fixtures), creates 9 untracked files under .agent/evidence/, leaks untracked .agent/tmp-plan-waves-tests/ (missing from .gitignore), and leaves 858 leftover files in .agent/tmp-c2-tests/.",
    remediation:
      "Isolate all test writes into tempfile.TemporaryDirectory() with guaranteed tearDown cleanup; remove band-aid .agent/tmp-c*-tests/ gitignore entries once tests clean up after themselves.",
  },
  {
    id: "BUG-03",
    title: "Stale Post-Merge Governance State After PR #279 & PR #248",
    severity: "High",
    tone: "danger",
    location: "PROGRESS.md, IMPLEMENTATION_PLAN.md, GitHub #278 & #247",
    detail:
      "PR #279 (bend-policy-proof-spike) merged into main on 2026-11-20 (38d3563), yet PROGRESS.md still reports it as IN PROGRESS awaiting PR, IMPLEMENTATION_PLAN.md has all 9 acceptance boxes unchecked, and Issue #278 remains open. Separately, Issue #247 (conversation-trajectory-ingest) is still open on GitHub even though PR #248 merged orchestrator/conversation/.",
    remediation:
      "Run a closeout PR to reconcile PROGRESS.md and IMPLEMENTATION_PLAN.md, close Issue #247 (already shipped), and resolve ADR-110 + Issue #278.",
  },
  {
    id: "BUG-04",
    title: "doctor.sh Intermittent SIGPIPE Flake & Missing Skill Checks",
    severity: "Medium",
    tone: "warning",
    location: "scripts/doctor.sh:1407-1417",
    detail:
      "Under set -euo pipefail, piping northstar help (>16 KB) directly into grep -q causes intermittent SIGPIPE failures (measured 4/300 on origin/main). Additionally, 5 of 52 Skills (agent-skills-packaging, finishing-a-development-branch, goose-agent-orchestration, security-audit-procedures, subagent-driven-development) are omitted from doctor.sh explicit skill checks.",
    remediation:
      "Capture northstar help into a shell variable once before grepping; loop dynamically over .cursor/skills/*/SKILL.md in doctor.sh instead of maintaining a hardcoded list.",
  },
  {
    id: "BUG-05",
    title: "Pending Skill Inode Carry-Over Warning Unresolved",
    severity: "Medium",
    tone: "warning",
    location: ".cursor/skills/inodes/index.json",
    detail:
      "doctor.sh emits a standing warning: 'skill inode carry-over pending Captain approval: github-integration,pull-request-preparation' because both entries carry captain_approved: false after content hash updates.",
    remediation:
      "Review diffs on github-integration and pull-request-preparation Skills and record Captain approval (or reset reputation carry-over) so doctor.sh returns 0 warnings.",
  },
  {
    id: "BUG-06",
    title: "CI Never Builds or Tests orchestrator/ui/ TypeScript Package",
    severity: "Medium",
    tone: "warning",
    location: ".github/workflows/ci.yml",
    detail:
      "orchestrator/ui/ declares React 19, Zod 4, TypeScript 5.8, and src/library.test.ts, but CI only executes doctor.sh, tests/run.sh, and tests/evals/run.sh. Type regressions or broken OpenUI schema generation will pass CI undetected.",
    remediation:
      "Add a Node job to .github/workflows/ci.yml running npm ci && npm run typecheck && npm test in orchestrator/ui/.",
  },
  {
    id: "BUG-07",
    title: "Feature-Gate & CLI Surface Sprawl (110 Env Vars, 39 Unrouted Scripts)",
    severity: "Medium",
    tone: "warning",
    location: "scripts/northstar (41 KB), scripts/*.sh (85 files)",
    detail:
      "Codebase defines 110 distinct COMPASS_* environment variables (30+ *_ENABLED gates), 39 of 84 standalone scripts/*.sh are not routed through scripts/northstar, and several orchestrator packages overlap in naming (planner/planning/plan_waves/plan_writer; route/routing; train_bridge/training; openui/ui).",
    remediation:
      "Introduce cohesive profile bundles (e.g. COMPASS_PROFILE=core|review|cognitive|all), route or deprecate legacy standalone scripts, and consolidate overlapping package boundaries.",
  },
  {
    id: "BUG-08",
    title: "Hardcoded Single Model Pin & URL in Jev DecisionProvider",
    severity: "Low",
    tone: "info",
    location: "orchestrator/providers/decision/jev_provider.py:86-121",
    detail:
      "jev_provider.py hardcodes exact equality checks against https://api.typesafe.ai/v1 and a single PINNED_JEV_MODEL_ID from M41, preventing model upgrades or alternative decision endpoints without editing source code.",
    remediation:
      "Move allowlisted base URLs and pinned model revisions into a Captain-reviewed config manifest rather than hardcoded equality checks.",
  },
  {
    id: "BUG-09",
    title: "Repository Hygiene: 195 Stale Remote Branches & Legacy Draft Plans",
    severity: "Low",
    tone: "neutral",
    location: "origin/* branches, docs/plans/P1_AWAITING_APPROVAL.md, P2_AWAITING_APPROVAL.md",
    detail:
      "195 remote branches (mostly merged chore/* and cursor/* branches) and 131 tags accumulate on origin. docs/plans/P1_AWAITING_APPROVAL.md and P2_AWAITING_APPROVAL.md remain as 150-byte obsolete stubs from v1.3/v1.4.",
    remediation:
      "Prune merged remote branches, enable GitHub auto-delete head branches on merge, and archive obsolete P1/P2 placeholder files.",
  },
];

const INITIAL_ROADMAP: TodoItem[] = [
  {
    id: "p0-1",
    content: "P0 — Patch Finding 001 in ensure_policy_for_instruction() + add Bend entry-state law",
    status: "pending",
  },
  {
    id: "p0-2",
    content: "P0 — Isolate test suite writes into TemporaryDirectory() so tests leave git status clean",
    status: "pending",
  },
  {
    id: "p0-3",
    content: "P0 — Reconcile post-merge state: close Issue #247, decide ADR-110 / Issue #278, update PROGRESS.md",
    status: "pending",
  },
  {
    id: "p1-1",
    content: "P1 — Fix doctor.sh SIGPIPE flake (buffer northstar help) & dynamically check all 52 Skills",
    status: "pending",
  },
  {
    id: "p1-2",
    content: "P1 — Resolve pending skill inode carry-over warning (github-integration, pull-request-preparation)",
    status: "pending",
  },
  {
    id: "p1-3",
    content: "P1 — Wire orchestrator/ui/ typecheck & tests into .github/workflows/ci.yml",
    status: "pending",
  },
  {
    id: "p2-1",
    content: "P2 — Replace stub_student fixture scoring with real local model eval in Specialized L0–L2 & N4",
    status: "pending",
  },
  {
    id: "p2-2",
    content: "P2 — Pick 1–2 highest-value integrations (T3 Code or Sentry live) and finish real transport wiring",
    status: "pending",
  },
  {
    id: "p2-3",
    content: "P2 — Consolidate 110 COMPASS_* flags into operator profiles & finish B4 supervised repair loop",
    status: "pending",
  },
  {
    id: "p3-1",
    content: "P3 — Complete XRV ops-verified audit drill, prune 195 remote branches, build live OpenUI viewer",
    status: "pending",
  },
];

const DOMAIN_LOC_CATEGORIES = [
  "integrations (56 files)",
  "providers (28 files)",
  "behavior (39 files)",
  "review (14 files)",
  "knowledge (13 files)",
  "status (18 files)",
  "learning (9 files)",
  "specialized (6 files)",
  "formal (4 files)",
  "cognitive (9 files)",
];

const DOMAIN_LOC_VALUES = [7066, 4910, 4606, 3692, 2281, 1930, 1547, 1487, 1070, 1052];

export default function NorthStarAuditCanvas() {
  const theme = useHostTheme();
  const [activeTab, setActiveTab] = useState<TabId>("overview");
  const [categoryFilter, setCategoryFilter] = useState<CategoryFilter>("All");
  const [roadmap, setRoadmap] = useCanvasState<TodoItem[]>("northstar-audit-roadmap", INITIAL_ROADMAP);

  const filteredUnfinished = useMemo(() => {
    if (categoryFilter === "All") return UNFINISHED_FEATURES;
    return UNFINISHED_FEATURES.filter((item) => item.category === categoryFilter);
  }, [categoryFilter]);

  const toggleTodo = (clicked: TodoItem) => {
    setRoadmap((prev) =>
      prev.map((item) =>
        item.id === clicked.id
          ? { ...item, status: item.status === "completed" ? "pending" : "completed" }
          : item
      )
    );
  };

  return (
    <Stack gap={20} style={{ padding: 20, maxWidth: 1120, margin: "0 auto" }}>
      <Stack gap={6}>
        <Row align="center" justify="space-between" wrap gap={12}>
          <H1>NorthStar Control Repo — Full Engineering Audit</H1>
          <Text size="small" tone="tertiary">
            <Code>loganware05/captains-compass-cursor</Code> · <Code>main @ 38d3563</Code> · v1.87.0 · 2026-11-20
          </Text>
        </Row>
        <Text tone="secondary">
          Forensic evaluation of architecture, live vs. fixture completeness, test hygiene, governance integrity,
          and unfinished subsystems across 319 Python modules, 85 shell scripts, 52 Skills, and 110 ADRs.
        </Text>
      </Stack>

      <Grid columns={4} gap={12}>
        <Card>
          <CardBody>
            <Stat value="941 / 0" label="Python Unit Tests (11 skipped)" tone="success" />
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat value="13" label="Unfinished / Stub Subsystems" tone="warning" />
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat value="3 High" label="Immediate Bugs & Hygiene Gaps" tone="danger" />
          </CardBody>
        </Card>
        <Card>
          <CardBody>
            <Stat value="110" label="COMPASS_* Env Gates (30+ flags)" tone="info" />
          </CardBody>
        </Card>
      </Grid>

      <Callout tone="danger" title="Top 3 Findings Requiring Immediate Attention">
        <Stack gap={4}>
          <Text size="small">
            1. <Text weight="semibold">Unpatched Policy Bypass (Finding 001):</Text>{" "}
            <Code>ensure_policy_for_instruction()</Code> trusts instruction <Code>approval_state</Code>, allowing
            direct creation in <Code>proven</Code> without Captain approval or evidence gates.
          </Text>
          <Text size="small">
            2. <Text weight="semibold">Tests Mutate Tracked Git Files:</Text> Running <Code>tests/run.sh</Code> +{" "}
            <Code>unittest</Code> dirties 5 committed files, writes 9 untracked evidence files, and leaks{" "}
            <Code>.agent/tmp-plan-waves-tests/</Code> plus 858 scratch files in <Code>.agent/tmp-c2-tests/</Code>.
          </Text>
          <Text size="small">
            3. <Text weight="semibold">Scaffolding Ahead of Live Execution:</Text> Most newer subsystems (I2–I6
            integrations, Specialized L0–L3, N4 live arm, REA C6, OpenUI web surface, Behavior runtime) remain
            fixture-only or stubbed with zero populated runtime state.
          </Text>
        </Stack>
      </Callout>

      <Row gap={8} wrap>
        <Pill active={activeTab === "overview"} onClick={() => setActiveTab("overview")}>
          Overview & Footprint
        </Pill>
        <Pill active={activeTab === "unfinished"} onClick={() => setActiveTab("unfinished")}>
          Unfinished Features (13)
        </Pill>
        <Pill active={activeTab === "defects"} onClick={() => setActiveTab("defects")}>
          Defects & Hygiene (9)
        </Pill>
        <Pill active={activeTab === "roadmap"} onClick={() => setActiveTab("roadmap")}>
          Remediation Roadmap
        </Pill>
      </Row>

      <Divider />

      {activeTab === "overview" && (
        <Stack gap={20}>
          <Stack gap={8}>
            <H2>Executive Verdict</H2>
            <Text>
              NorthStar has an unusually disciplined core governance harness: approval-gated planning, fail-closed
              Cursor hooks, 52 well-structured Skills with complete <Code>capability.yaml</Code> sidecars, 137/137
              passing shell/eval tests, and 941 passing Python unit tests. However, rapid milestone velocity
              (v1.0.0 to v1.87.0 in 4 months) has created a stark <Text weight="semibold">breadth-vs-depth gap</Text>:
              the control plane now spans 45,008 LOC of Python and 11,568 LOC of Bash across 44 packages, yet a large
              share of its headline subsystems are hermetic fixture skeletons whose live execution paths are deferred
              or stubbed.
            </Text>
          </Stack>

          <Card>
            <CardHeader trailing="21 Major Subsystems Audited">Subsystem Maturity Distribution</CardHeader>
            <CardBody>
              <Stack gap={12}>
                <UsageBar
                  total={21}
                  topLeftLabel="Operational Maturity Breakdown"
                  topRightLabel="8 Ready · 6 Partial · 4 Fixture/Stub · 3 Deferred"
                  segments={[
                    { id: "ready", value: 8, color: "green" },
                    { id: "partial", value: 6, color: "blue" },
                    { id: "fixture", value: 4, color: "yellow" },
                    { id: "deferred", value: 3, color: "orange" },
                  ]}
                />
                <Row gap={16} wrap>
                  <Row gap={6} align="center">
                    <Swatch color="green" />
                    <Text size="small" tone="secondary">
                      Production-Ready Core (8): Hooks, Installer/Updater, Skills/Agents, Capability Planner, Code
                      Reviewer MVP, Context Inodes, Wave Ledger, XRV EER/Readiness
                    </Text>
                  </Row>
                  <Row gap={6} align="center">
                    <Swatch color="blue" />
                    <Text size="small" tone="secondary">
                      Partial / Unwired Runtime (6): Behavior M46–M54, B4 Repair, OpenUI, C2 Session Memory,
                      Connected Ops C3/A2, Bend Formal Spike
                    </Text>
                  </Row>
                  <Row gap={6} align="center">
                    <Swatch color="yellow" />
                    <Text size="small" tone="secondary">
                      Fixture / Stub-Only (4): Integrations I2–I6, Specialized L0–L2 Scoring, N4 Live Arm, REA C6
                    </Text>
                  </Row>
                  <Row gap={6} align="center">
                    <Swatch color="orange" />
                    <Text size="small" tone="secondary">
                      Explicitly Deferred (3): Specialized L3 GPU (#237), Hosted Vector DB / Live Embeddings, AHF Live
                      Controls
                    </Text>
                  </Row>
                </Row>
              </Stack>
            </CardBody>
          </Card>

          <Stack gap={8}>
            <H2>Codebase Footprint — Top 10 Orchestrator Domains by Lines of Python</H2>
            <Text size="small" tone="tertiary">
              Metric: Python lines of code (LOC) per package under orchestrator/ (horizontal axis: LOC; vertical axis:
              package & file count). Source: loganware05/captains-compass-cursor @ 38d3563 · 2026-11-20. Total across
              all 44 packages: 45,008 LOC in 319 files.
            </Text>
            <BarChart
              categories={DOMAIN_LOC_CATEGORIES}
              series={[{ name: "Python LOC", data: DOMAIN_LOC_VALUES, tone: "info" }]}
              horizontal
              height={320}
              valueSuffix=" LOC"
              showValues
            />
          </Stack>

          <Stack gap={8}>
            <H2>Verified Local Audit Checks</H2>
            <Table
              headers={["Check", "Command", "Measured Result", "Notes"]}
              rows={[
                [
                  "Doctor health check",
                  <Code key="c1">./scripts/doctor.sh</Code>,
                  "0 errors, 1 warning",
                  "Warning on skill inode carry-over; intermittent SIGPIPE flake on northstar help",
                ],
                [
                  "Main shell & eval suite",
                  <Code key="c2">./tests/run.sh</Code>,
                  "137 passed, 0 failed",
                  "Includes 43/43 harness evals; mutates tracked files during run",
                ],
                [
                  "Python unit test suite",
                  <Code key="c3">unittest discover -s tests/orchestrator</Code>,
                  "941 OK (11 skipped)",
                  "10 Bend E2E tests skip without toolchain; 1 sandbox pack skipped",
                ],
                [
                  "OpenUI TypeScript package",
                  <Code key="c4">orchestrator/ui/package.json</Code>,
                  "Not run in CI",
                  "Has library.test.ts and tsconfig.json, omitted from .github/workflows/ci.yml",
                ],
                [
                  "GitHub open issues",
                  <Code key="c5">list_issues(state=open)</Code>,
                  "3 open (#278, #247, #237)",
                  "#247 already merged in PR #248; #278 PR #279 merged without closeout",
                ],
                [
                  "Repo branch & tag hygiene",
                  <Code key="c6">git branch -r / git tag</Code>,
                  "195 branches · 131 tags",
                  "Heavy accumulation of merged chore/* and cursor/* branches on origin",
                ],
              ]}
              rowTone={["warning", "warning", "success", "warning", "danger", "neutral"]}
              striped
            />
          </Stack>
        </Stack>
      )}

      {activeTab === "unfinished" && (
        <Stack gap={16}>
          <Row align="center" justify="space-between" wrap gap={8}>
            <H2>Unfinished Features & Deferred Live Paths ({filteredUnfinished.length})</H2>
            <Row gap={6} wrap>
              {(["All", "Integrations", "AI & Models", "Governance & Formal", "UX & Ops"] as CategoryFilter[]).map(
                (cat) => (
                  <Pill key={cat} active={categoryFilter === cat} size="sm" onClick={() => setCategoryFilter(cat)}>
                    {cat}
                  </Pill>
                )
              )}
            </Row>
          </Row>

          <Table
            headers={["ID", "Subsystem", "Category", "State", "Primary Location"]}
            rows={filteredUnfinished.map((item) => [
              <Code key={item.id}>{item.id}</Code>,
              item.name,
              item.category,
              item.status,
              <Code key={`${item.id}-loc`}>{item.location}</Code>,
            ])}
            rowTone={filteredUnfinished.map((item) => item.tone)}
            striped
          />

          <Stack gap={4}>
            <H3>Detailed Breakdown & Required Next Development</H3>
            <Text size="small" tone="tertiary">
              Expand any row to inspect observed code reality, evidence, and concrete work required to finish it.
            </Text>
          </Stack>

          <Stack gap={2}>
            {filteredUnfinished.map((item, idx) => (
              <CollapsibleSection
                key={item.id}
                title={`${item.id} — ${item.name}`}
                defaultOpen={idx < 3}
                trailing={
                  <Text size="small" tone="tertiary">
                    {item.status} · {item.category}
                  </Text>
                }
              >
                <Stack gap={8} style={{ paddingBottom: 12 }}>
                  <Text size="small">
                    <Text weight="semibold">Location:</Text> <Code>{item.location}</Code>
                  </Text>
                  <Text size="small">
                    <Text weight="semibold">Current Reality:</Text> {item.currentState}
                  </Text>
                  <Text size="small">
                    <Text weight="semibold">Still Needs Development:</Text> {item.stillNeeded}
                  </Text>
                  <Text size="small" tone="secondary">
                    <Text weight="semibold">Audit Evidence:</Text> {item.evidence}
                  </Text>
                </Stack>
              </CollapsibleSection>
            ))}
          </Stack>
        </Stack>
      )}

      {activeTab === "defects" && (
        <Stack gap={16}>
          <H2>Verified Bugs, Security Findings & Operational Debt (9)</H2>
          <Table
            headers={["ID", "Severity", "Finding", "Location"]}
            rows={DEFECTS_AND_DEBT.map((d) => [
              <Code key={d.id}>{d.id}</Code>,
              d.severity,
              d.title,
              <Code key={`${d.id}-loc`}>{d.location}</Code>,
            ])}
            rowTone={DEFECTS_AND_DEBT.map((d) => d.tone)}
            striped
          />

          <Stack gap={10}>
            {DEFECTS_AND_DEBT.map((d) => (
              <Card key={d.id}>
                <CardHeader trailing={`${d.severity} · ${d.id}`}>{d.title}</CardHeader>
                <CardBody>
                  <Stack gap={6}>
                    <Text size="small">
                      <Text weight="semibold">Where:</Text> <Code>{d.location}</Code>
                    </Text>
                    <Text size="small">{d.detail}</Text>
                    <Text size="small" tone="secondary">
                      <Text weight="semibold">Recommended Fix:</Text> {d.remediation}
                    </Text>
                  </Stack>
                </CardBody>
              </Card>
            ))}
          </Stack>
        </Stack>
      )}

      {activeTab === "roadmap" && (
        <Stack gap={16}>
          <Stack gap={6}>
            <H2>Prioritized Remediation & Completion Roadmap</H2>
            <Text tone="secondary">
              Click any item below to track completion as you resolve each gap. Ordered by risk reduction and
              leverage rather than adding new milestones.
            </Text>
          </Stack>

          <TodoListCard todos={roadmap} defaultExpanded onTodoClick={toggleTodo} />

          <Callout tone="info" title="Strategic Recommendation: Consolidate Before Adding Milestones">
            <Text size="small">
              NorthStar does not need M56+ or new integration stubs. The highest-leverage next cycle is a focused
              stabilization pass: fix Finding 001 and test-suite git pollution, close out #278/#247, replace stub
              scorers in Specialized/N4 with one real local-model harness, and wire live execution for the 1–2
              integrations actively used by your product repos.
            </Text>
          </Callout>

          <Row gap={12} wrap style={{ borderTop: `1px solid ${theme.stroke.tertiary}`, paddingTop: 12 }}>
            <Text size="small" tone="tertiary">
              Audited Repository:
            </Text>
            <Link href="https://github.com/loganware05/captains-compass-cursor">
              loganware05/captains-compass-cursor
            </Link>
            <Spacer />
            <Link href="https://github.com/loganware05/captains-compass-cursor/issues/278">Issue #278</Link>
            <Link href="https://github.com/loganware05/captains-compass-cursor/issues/247">Issue #247</Link>
            <Link href="https://github.com/loganware05/captains-compass-cursor/issues/237">Issue #237</Link>
          </Row>
        </Stack>
      )}
    </Stack>
  );
}
