---
name: bounded-decision-arbiter
description: "Use bounded decisions with Arbiter/Laya."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [arbiter, laya, mcp, decisions, classification, scoring, safety]
---

# Bounded Decisions with Arbiter/Laya

## When to Use

Use this skill when Hermes must choose among closed alternatives, estimate the probability of a statement, score an ordered scale, evaluate an action before execution, or group several decisions about the same context.

## Purpose

Laya, accessed through the `arbiter` MCP server, is a fast engine for bounded, structured decisions. Consider it when there is a closed set of alternatives, a classification, a score, a probability estimate, an action evaluation, or several related decisions.

Do not use it as a substitute for open-ended reasoning. Reason with Hermes first when:

- the problem is open-ended or requires a long explanation;
- the alternatives are not yet defined;
- new information must be researched;
- creativity or content generation is required; or
- the context has not been synthesized and requires deep understanding.

After the problem is synthesized, Laya can help when a clean, bounded decision remains. Do not force an open problem into a poor classification merely to use Laya.

## Available Tools and Selection

Use only the MCP tools from the `arbiter` server:

| Tool | Use when | Examples |
|---|---|---|
| `arbiter_check` | The question is essentially a binary/probabilistic statement. | “Is this error likely an authentication failure?”; “Does this incident require human intervention?” |
| `arbiter_classify` | Choose one option from a closed set of mutually distinguishable options. | `ignore / investigate / escalate`; `database / network / auth / application`; `low / medium / high`. |
| `arbiter_score` | The output is an ordered scale. | Severity 1–5; priority 1–10; risk 1–4. |
| `arbiter_gate` | Evaluate a proposed action before executing it. | A potentially destructive command or a risky operation. |
| `arbiter_decide` | Several related questions share the same state/context. | Get `severity`, `category`, `needs_human`, and `action` in one call. |

Prefer one `arbiter_decide` call over several separate calls when the questions share context and can be evaluated together.

### `arbiter_gate` Is Advisory

The expected semantics are `allow`, `confirm`, or `block`, but initially the tool is **ADVISORY**. Never automatically authorize, block, or execute a dangerous action solely because of Laya's response. Combine it with deterministic rules, existing policies, and human confirmation when appropriate.

## Building the `state`

Before calling Laya:

1. Reduce the context to relevant facts.
2. Remove irrelevant conversation, redundant logs, and internal reasoning.
3. Preserve important evidence.
4. Avoid biasing the state toward a desired answer.
5. Use structured data when it helps separate facts.
6. Do not invent facts to complete the context.

Good state:

```text
The PostgreSQL container exceeded its memory limit, was restarted by Docker, the API was unavailable for 90 seconds, and it recovered automatically.
```

Bad state:

```text
PostgreSQL had a terrible critical failure and obviously needs escalation.
```

## Criteria and Options

For `arbiter_classify`:

- define mutually distinguishable options;
- give each option a clear semantic description;
- avoid ambiguous names;
- keep comparable detail across options;
- do not put the desired answer into the instructions; and
- use no more options than the tool supports; do not invent additional categories.

For `arbiter_score`, always order levels from lowest to highest and describe each level clearly.

For `arbiter_check`, phrase the question as the concrete statement whose probability you want to estimate, not as a vague request for explanation.

## Interpreting Results

Do not use only the `choice` field. Consider probabilities, `confidence`, and the separation between the two best options.

For a classification, conceptually calculate:

```text
margin = top1_probability - top2_probability
```

A top-1 option can still be a weak signal. For example:

```text
investigate = 0.42
ignore       = 0.34
escalate     = 0.24
```

Here `investigate` wins, but the margin is small; do not treat it as a firm conclusion.

### Provisional Confidence Policy

These thresholds are provisional guardrails, not statistical calibration for the environment:

- `confidence >= 0.50`: strong signal; use automatically only for low-risk, reversible actions.
- `0.20 <= confidence < 0.50`: intermediate signal; use as a recommendation, not authorization.
- `confidence < 0.20`: ambiguous signal; request more context, reason with the LLM, or escalate to the user.

For important decisions, also require a reasonable top-1/top-2 margin. If the tool does not return all fields needed to evaluate uncertainty, conservatively treat it as a recommendation.

## Risk and Actions

Laya is never the sole authority for:

- deleting data;
- destructive production changes;
- changing credentials, certificates, or keys;
- commands with a large blast radius;
- publishing information;
- irreversible actions; or
- critical security decisions.

In these cases:

1. use Laya as an advisor if useful;
2. consider the result together with the evidence;
3. apply deterministic rules and existing policies;
4. request human confirmation when appropriate; and
5. verify the result after any authorized action.

## Usage Examples

### 1. OOM Incident

Use `arbiter_classify` with a factual state and options such as:

```text
ignore: No action required
investigate: Investigate root cause
escalate: Immediate human escalation
```

Interpret the option together with probabilities, confidence, and margin. Do not escalate automatically merely because it is top-1.

### 2. Severity

Use `arbiter_score` when an explicit ordinal scale is needed, such as severity levels 1–5 ordered from low to high. Use `arbiter_classify` when categories are semantic and do not necessarily represent ordered distance.

### 3. Dangerous Action

You may use `arbiter_gate` to evaluate:

```text
docker system prune -af
```

Treat the result as advisory. Laya does not replace command policy, impact review, or required confirmation.

### 4. Several Related Decisions

Use one `arbiter_decide` call for the same synthesized incident to ask for:

- `severity`;
- `category`;
- `needs_human`; and
- `action`.

This is preferable to four separate calls when all questions share the same state.

## Interaction with Other Tools

Do not mix responsibilities:

- `tool-output-compactor` reduces outputs;
- `progress-guard` detects loops and lack of progress; and
- Arbiter/Laya classifies, scores, and evaluates bounded decisions.

This skill does not change or control those plugins and does not implement new tools or inference code.

## General Rule

Before using a large LLM for a simple, closed decision, consider whether it can be cleanly expressed as an Arbiter/Laya call. If it cannot be defined with a state, instructions, and clear criteria, continue reasoning with Hermes and do not force Laya into the workflow.
