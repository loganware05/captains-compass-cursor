# Conversation trajectory ingest

Gated operator surface for ChatGPT / Obsidian AI Exporter / T3 attachment
markdown exports. Evidence-only — never grants execution authority.

## Gate

```bash
COMPASS_CONVERSATION_INGEST_ENABLED=1
```

Fail-closed when unset.

## Commands

```bash
COMPASS_CONVERSATION_INGEST_ENABLED=1 \
  ./scripts/northstar conversation ingest --path export.md \
  [--source chatgpt|obsidian-ai-exporter|t3-attachment] \
  [--model LABEL] [--draft-exemplar positive|negative]

COMPASS_CONVERSATION_INGEST_ENABLED=1 \
  ./scripts/northstar conversation show --id conv-…-t000

COMPASS_CONVERSATION_INGEST_ENABLED=1 \
  ./scripts/northstar conversation list
```

## Storage

| Path | Contents |
|---|---|
| `.agent/conversations/trajectories/` | Schema-validated turn records |
| `.agent/conversations/ingest-log/` | Ingest summaries |
| `.agent/conversations/exemplar-drafts/` | Optional proposal-only drafts |
| `.agent/knowledge/items/know-conv-*` | Knowledge Steward summaries |

Each trajectory stores `user_prompt`, `model_or_source`, `assistant_suggestion`,
`claim_kind: external`, and authority locks (`approved_for_execution`,
`authority_mutation`, `auto_promoted` always false).

## Parser target

Obsidian AI Exporter ChatGPT markdown with YAML frontmatter and callouts:

- `> [!QUESTION] User`
- `> [!NOTE] ChatGPT`

## Security

- Secret-like source paths rejected
- External chat is never treated as repository truth
- No auto-promotion of Skills, Policies, or routing
- C7 training export of conversations is out of scope for v1.77.0

## Fixture

`tests/fixtures/conversations/obsidian-chatgpt-sample.md`
