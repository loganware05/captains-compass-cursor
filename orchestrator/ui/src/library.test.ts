import assert from "node:assert/strict";
import { createStreamingParser } from "@openuidev/lang-core";
import { test } from "node:test";
import { northstarOpenUILibrary } from "./library";

test("library schema parses PlanApproval fixture", () => {
  const schema = northstarOpenUILibrary.toJSONSchema();
  const parser = createStreamingParser(schema, "NorthStarStack");
  const lang = [
    'card = PlanApprovalCard("openui-control-plane", "Open UI", "APPROVED", "hooks=7", "orchestrator/ui", "implementation-agent", "plan-approval-check.sh")',
    "root = NorthStarStack([card])",
    "",
  ].join("\n");
  const result = parser.push(lang, true);
  assert.equal(result.meta.errors.length, 0, JSON.stringify(result.meta.errors));
  assert.ok(result.root);
});

test("system prompt mentions PlanApprovalCard", () => {
  const prompt = northstarOpenUILibrary.prompt();
  assert.match(prompt, /PlanApprovalCard/);
  assert.match(prompt, /openui-lang/i);
});
