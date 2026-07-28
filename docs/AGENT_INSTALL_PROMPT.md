# Agent Install & Activation Prompts

Copy-paste prompts for installing Captain's Compass into a product repository, then activating its operating model for real feature work.

Control repository: https://github.com/loganware05/captains-compass-cursor  
Companion guide: [`PRODUCT_ONBOARDING.md`](PRODUCT_ONBOARDING.md)

Replace `/ABSOLUTE/PATH/TO/captains-compass-cursor` with the real path to your local control-repo clone.

---

## Prompt 1 — Install Compass (product repo)

Use this in Cursor while the **product** repository is open (or when the agent can reach both repos). Workflow install only — no product feature work yet.

```text
Install Captain's Compass into this product repository.

Control repo (source of truth):
  /ABSOLUTE/PATH/TO/captains-compass-cursor

Follow docs/PRODUCT_ONBOARDING.md from the control repo. Do not invent a custom install.

Rules:
1. Do NOT modify product application code. This is a workflow install only.
2. Work on branch: chore/install-captains-compass (create from the default base branch).
3. Never install into the control repo itself.
4. Prefer a clean install without --force. Only use --force if the Captain explicitly requests refreshing an existing Compass install.
5. Do not overwrite existing product memory docs (PROJECT_CONTEXT.md, DECISIONS.md, etc.).

Steps:
1. Confirm the control repo exists and run:
   /ABSOLUTE/PATH/TO/captains-compass-cursor/scripts/doctor.sh
2. Confirm this directory is a Git repo and is not the control repo.
3. Create/checkout chore/install-captains-compass.
4. Run:
   /ABSOLUTE/PATH/TO/captains-compass-cursor/scripts/install.sh "$(pwd)"
5. Verify:
   /ABSOLUTE/PATH/TO/captains-compass-cursor/scripts/doctor.sh "$(pwd)"
6. Summarize what was added (especially .cursor/, root docs, .agent/COMPASS_VERSION).
7. If PROJECT_CONTEXT.md / TESTING.md / DECISIONS.md are still templates, note that Prompt 2 (activation) should run next — do not invent false stack details yet.
8. Stage and prepare a commit message:
   chore(workflow): install Captain's Compass
   Do NOT commit or push unless the Captain asks.
9. Stop and report next steps: open this product repo alone in Cursor, then paste Prompt 2 to activate the operating model and fill PROJECT_CONTEXT.md.

If anything conflicts or doctor fails, stop and report — do not force-overwrite without approval.
```

---

## Prompt 2 — Activate the operating model (after install)

Use this **after** Compass is installed and the product repo is open alone in Cursor. This is what gets real product work started: the agent adopts the Compass process and interviews you to fill project memory.

```text
I've recently installed an agentic engineering workflow template called Captain's Compass into this project. What I'd like you to do is utilize its operational model for future feature development and deployment.

Start by reading AGENTS.md, PROJECT_CONTEXT.md, DECISIONS.md, PROGRESS.md, TESTING.md, and IMPLEMENTATION_PLAN.md. Inspect the Git status and active branch.

Then ask me focused questions and fill out as much of PROJECT_CONTEXT.md as possible (product summary, users, stack, repo map, environments, constraints, terminology, commands, priorities). Update TESTING.md and DECISIONS.md only where you have clear answers from me or strong evidence in the repo — do not invent facts.

Rules while doing this:
1. You are the First Mate; I am the Captain.
2. Follow the Compass approval gate: for any request that changes product behavior, write or update IMPLEMENTATION_PLAN.md, set it to AWAITING APPROVAL, present it, and stop before changing product implementation files.
3. Prefer evidence from the repository over assumptions; mark unknowns explicitly.
4. Do not start feature implementation in this turn — memory and process first.

When PROJECT_CONTEXT.md is in good shape, summarize what you filled in, what is still unknown, and confirm you will use the Compass operating model (plan → approve → branch/worktree → implement → validate → PR) for subsequent feature work.
```

### Shorter variant

```text
I've recently installed Captain's Compass into this project. Use its operational model for future feature development and deployment. Start by asking me questions and filling out as much of PROJECT_CONTEXT.md as possible. Follow AGENTS.md and the approval gate — plan first, no product code changes until I approve IMPLEMENTATION_PLAN.md.
```

---

## Suggested sequence

1. Run **Prompt 1** (or install manually per [`PRODUCT_ONBOARDING.md`](PRODUCT_ONBOARDING.md)).
2. Merge the install PR if you used a branch.
3. Open the product repository alone in Cursor.
4. Paste **Prompt 2**.
5. After `PROJECT_CONTEXT.md` is solid, request the next feature — expect an `IMPLEMENTATION_PLAN.md` at **AWAITING APPROVAL** before implementation.
