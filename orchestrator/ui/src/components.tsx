import { defineComponent } from "@openuidev/react-lang";
import { z } from "zod/v4";
import type { CSSProperties, ReactNode } from "react";

const shell: CSSProperties = {
  fontFamily: '"IBM Plex Sans", "Source Sans 3", "Segoe UI", sans-serif',
  color: "#0f172a",
  background:
    "linear-gradient(160deg, #f0f7f4 0%, #e8eef7 45%, #f7f3ea 100%)",
  border: "1px solid #c5d0c8",
  borderRadius: 12,
  padding: "1rem 1.15rem",
  marginBottom: "0.75rem",
};

const titleStyle: CSSProperties = {
  fontFamily: '"Fraunces", "Iowan Old Style", Georgia, serif',
  fontSize: "1.25rem",
  margin: "0 0 0.35rem",
  letterSpacing: "-0.02em",
};

const muted: CSSProperties = { color: "#475569", fontSize: "0.92rem", margin: 0 };

function Section({
  title,
  children,
}: {
  title: string;
  children: ReactNode;
}) {
  return (
    <section style={shell} aria-label={title}>
      <h2 style={titleStyle}>{title}</h2>
      {children}
    </section>
  );
}

export const NorthStarStack = defineComponent({
  name: "NorthStarStack",
  description: "Root stack for NorthStar Open UI control widgets",
  props: z.object({
    children: z.array(z.any()).describe("Child widgets"),
  }),
  component: ({ props }) => (
    <div
      role="region"
      aria-label="NorthStar Open UI control plane"
      style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}
    >
      {props.children}
    </div>
  ),
});

export const PlanApprovalCard = defineComponent({
  name: "PlanApprovalCard",
  description: "Interactive plan approval summary with risk context",
  props: z.object({
    planId: z.string().describe("Plan ID"),
    title: z.string().describe("Plan title"),
    status: z.string().describe("Plan status"),
    riskSummary: z.string().describe("Risk / hook / specialist summary"),
    affectedFiles: z.string().describe("Affected files summary"),
    specialists: z.string().describe("Specialist agent assignments"),
    hookStatus: z.string().describe("Safety hook inventory"),
  }),
  component: ({ props }) => (
    <Section title="Plan approval">
      <p style={muted}>
        <strong>{props.title}</strong> · <code>{props.planId}</code>
      </p>
      <p style={muted}>
        Status: <strong>{props.status}</strong>
      </p>
      <details>
        <summary>Risk scorecard</summary>
        <p style={muted}>{props.riskSummary}</p>
        <p style={muted}>Files: {props.affectedFiles}</p>
        <p style={muted}>Specialists: {props.specialists}</p>
        <p style={muted}>Hooks: {props.hookStatus}</p>
      </details>
      <div
        style={{
          display: "flex",
          flexWrap: "wrap",
          gap: "0.5rem",
          marginTop: "0.85rem",
        }}
      >
        <button
          type="button"
          aria-label="Approve plan via attested northstar ui approve"
          onClick={() => {
            // Renderer hosts should wire onAction; default is operator CLI.
            console.info(
              "[NorthStar Open UI] APPROVE requires COMPASS_CAPTAIN_APPROVE=1 and: northstar ui approve --enable-gates",
            );
          }}
        >
          Approve plan
        </button>
        <button
          type="button"
          aria-label="Reject plan with feedback via northstar ui reject"
          onClick={() => {
            console.info(
              "[NorthStar Open UI] REJECT: northstar ui reject --feedback \"…\" --enable-gates",
            );
          }}
        >
          Reject with feedback
        </button>
      </div>
      <p style={{ ...muted, marginTop: "0.75rem" }}>
        Buttons never auto-approve. Captain attestation (
        <code>COMPASS_CAPTAIN_APPROVE=1</code>) plus{" "}
        <code>northstar ui approve</code> / <code>reject</code> is required;
        plan-approval-check treats those commands as plan forges.
      </p>
    </Section>
  ),
});

export const ControlTowerTelemetry = defineComponent({
  name: "ControlTowerTelemetry",
  description: "Control tower: agents, Skills, budgets, safety hooks",
  props: z.object({
    activeAgents: z.string().describe("Specialist agent inventory"),
    skillRanking: z.string().describe("Skill ranking / sample Skills"),
    budgetProgress: z.string().describe("Autonomy budget summary"),
    hookGrid: z.string().describe("Safety hook status grid"),
  }),
  component: ({ props }) => (
    <Section title="Control tower">
      <p style={muted}>Agents: {props.activeAgents}</p>
      <p style={muted}>Skills: {props.skillRanking}</p>
      <p style={muted}>Budget: {props.budgetProgress}</p>
      <p style={muted}>Hooks: {props.hookGrid}</p>
    </Section>
  ),
});

export const HermeticScorecard = defineComponent({
  name: "HermeticScorecard",
  description: "N3 hermetic adaptive intelligence scorecard",
  props: z.object({
    phase: z.string(),
    recommendation: z.string(),
    rationale: z.string(),
    metricsSummary: z.string(),
    baselineVsEvidence: z.string(),
  }),
  component: ({ props }) => (
    <Section title="Hermetic scorecard (N3)">
      <p style={muted}>
        Phase: <strong>{props.phase}</strong> · Level 3:{" "}
        <strong>{props.recommendation}</strong>
      </p>
      <p style={muted}>{props.rationale}</p>
      <p style={muted}>Metrics: {props.metricsSummary}</p>
      <p style={muted}>Compare: {props.baselineVsEvidence}</p>
    </Section>
  ),
});

export const CompassStatusBadge = defineComponent({
  name: "CompassStatusBadge",
  description: "Reusable NorthStar status badge (N2 pattern)",
  props: z.object({
    label: z.string(),
    version: z.string(),
    tone: z.string(),
  }),
  component: ({ props }) => (
    <div
      role="status"
      aria-label={`${props.label} ${props.version}`}
      style={{
        ...shell,
        display: "inline-flex",
        alignItems: "baseline",
        gap: "0.5rem",
        padding: "0.55rem 0.85rem",
        background:
          props.tone === "defer"
            ? "linear-gradient(120deg, #f7f0e8, #eef2f7)"
            : shell.background,
      }}
    >
      <span style={{ ...titleStyle, fontSize: "1.05rem", margin: 0 }}>
        {props.label}
      </span>
      <span style={muted}>v{props.version}</span>
      <span style={{ ...muted, textTransform: "uppercase", letterSpacing: "0.04em" }}>
        {props.tone}
      </span>
    </div>
  ),
});

export const CloseoutLedgerWidget = defineComponent({
  name: "CloseoutLedgerWidget",
  description: "N1 closeout ledger with SHA reconciliation view",
  props: z.object({
    snapshotId: z.string(),
    readiness: z.string(),
    shaLocal: z.string(),
    shaRemote: z.string(),
    evidenceSummary: z.string(),
    recommendedActions: z.string(),
  }),
  component: ({ props }) => (
    <Section title="Closeout ledger">
      <p style={muted}>
        Snapshot <code>{props.snapshotId}</code> · readiness{" "}
        <strong>{props.readiness}</strong>
      </p>
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "1fr 1fr",
          gap: "0.75rem",
        }}
      >
        <div>
          <p style={{ ...muted, fontWeight: 600 }}>Local SHA</p>
          <code>{props.shaLocal}</code>
        </div>
        <div>
          <p style={{ ...muted, fontWeight: 600 }}>Compared SHA</p>
          <code>{props.shaRemote}</code>
        </div>
      </div>
      <p style={muted}>Evidence: {props.evidenceSummary}</p>
      <p style={muted}>Actions: {props.recommendedActions}</p>
      <p style={muted}>
        Cleanup remains Captain-gated via{" "}
        <code>northstar status closeout</code> — UI does not auto-close issues.
      </p>
    </Section>
  ),
});

export const RecommendationCard = defineComponent({
  name: "RecommendationCard",
  description: "Advisory recommendation card (e.g. Level 3 deferral)",
  props: z.object({
    topic: z.string(),
    recommendation: z.string(),
    rationale: z.string(),
  }),
  component: ({ props }) => (
    <Section title={`${props.topic} recommendation`}>
      <p style={muted}>
        <strong>{props.recommendation}</strong>
      </p>
      <p style={muted}>{props.rationale}</p>
    </Section>
  ),
});
