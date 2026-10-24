import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";
import { northstarOpenUILibrary } from "../src/library";

const here = dirname(fileURLToPath(import.meta.url));
const out = join(
  here,
  "..",
  "..",
  "..",
  ".cursor",
  "templates",
  "openui-system-prompt.md",
);
const prompt = northstarOpenUILibrary.prompt();
const body = `# NorthStar Open UI system prompt

> Generated from \`orchestrator/ui\` component library. Models must emit valid
> **openui-lang** only (no markdown wrappers when streaming into the Renderer).

## Governance

- Captain retains final authority. Never auto-approve plans.
- Prefer allowlisted components only (see signatures below).
- On uncertainty, emit a minimal \`NorthStarStack\` with a status badge and fall
  back to markdown/CLI workflows.

---

${prompt}
`;
writeFileSync(out, body, "utf8");
console.log(`wrote ${out}`);
