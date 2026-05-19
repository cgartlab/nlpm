---
title: Vocabulary design principles
outline: [2, 3]
---

# Vocabulary Design Principles

Six principles that govern controlled-vocabulary work in NLPM. Copied from `eou-foundry/dev-docs/04-vocabulary-principles.md`, battle-tested against OntoClean, DDD, ISO 25964, and BPMN/Event Storming.

## P1 — One term per distinct identity, at uniform granularity, within a declared scope {#P1}

Two terms merge when they share the same identity criterion, operate at the same level of specificity, and live within the same scope. A term legitimately meaning different things across scopes is not a violation — it is a boundary that must be named. Never apply the merge test globally across undeclared scope boundaries.

**Scope-timing rule:** scope must be declared *before* a vocabulary decision enters review. A scope boundary declared after the fact to resolve a collision is a retroactive exemption, not a valid scope, and is treated as a P1 violation.

**Sibling-granularity rule:** sibling terms in the vocabulary must be at comparable levels of specificity. A vocabulary that mixes crisp acts (`diagnose`) with vague phases (`process`) at the same level fails this principle even if each term individually passes the merge test.

## P2 — Nouns are rigid artifacts; verbs are state-changing acts {#P2}

A noun belongs in the inventory when it is *rigid* — it remains the same kind of thing regardless of what state it is in — and has a testable criterion for identity across time.

A state of an artifact is not a noun. `candidate`, `pending-approval`, `active` are field values on artifacts, not standalone nouns. The artifact they modify is the noun.

A verb belongs when it either changes the authority-state of a named artifact or produces a new rigid artifact that governance can act on independently. Sub-steps that serve a named verb without changing anything a stakeholder needs to react to separately are not top-level verbs.

## P3 — A verb is top-level only if it gates or produces {#P3}

A verb earns its place when it either:

(a) changes what the executor is permitted to do next, or
(b) produces a named artifact that governance can act on independently.

A **governed artifact** is any artifact with a declared schema, a file path, and an owner. This includes advisory artifacts — recommendations, no-change records, audit reports — not only active state-changers. An act that produces only ephemeral output or internal prose does not qualify.

An act that evaluates and recommends but does not meet either condition above is a sub-step, not a top-level verb.

**Pipeline-membership override:** when an act is a required named step in a declared governance pipeline, P5 naming pressure overrides the gates-or-produces test. The act is named regardless of whether it independently satisfies (a) or (b). For cross-scope pipeline steps, the naming obligation belongs to the scope that *produces* the step's output artifact, not the scope that consumes it.

## P4 — The vocabulary is closed under its own operations, within scope {#P4}

Every verb applies to at least one noun. Every noun is the target of at least one verb. A term that never appears in a verb+noun combination within its scope has no structural role and is a deletion candidate. Evaluate closure per declared scope, not globally.

A closure gap — a noun with no producing verb, or a verb whose artifacts are only described in prose — is evidence of an unnamed act.

**Cross-scope nouns:** a noun produced in one scope and consumed in another is a *cross-scope noun*, not a closure gap. It must be formally designated as such, naming the producing scope explicitly. A bare "application-domain" without naming the scope is not a valid designation — it is a deferment that must be recorded and revisited.

## P5 — Comprehensive means no unnamed judgment {#P5}

The vocabulary is comprehensive when every significant decision point has a name that forces the practitioner to surface what they are actually deciding.

If practitioners routinely describe an act as "we just checked" or "it felt right," or if documentation describes a step without assigning it a verb from the canonical set, the vocabulary has a gap.

## P6 — A term requires warrant before it enters {#P6}

A term earns inclusion through at least one of:

- **Literary warrant** — it appears in actual domain artifacts (specs, rules, schemas).
- **User warrant** — practitioners reach for it unprompted when describing their work.
- **Structural warrant** — the vocabulary hierarchy requires it for coherence. **Must cite a specific P4 closure requirement or P1 hierarchy coherence requirement.** Self-referential structural warrant ("the hierarchy needs this term") is not valid without naming which other term's relationship breaks without it.
- **Domain warrant** — the operational domain requires the distinction to prevent a specific failure.

Intuition alone is not warrant. Absence of warrant is grounds for exclusion or demotion to a sub-step or field value.

---

## Conflict resolution: precedence order {#precedence}

When two or more principles point in different directions, apply them in this order:

```
P2 > P3 > P1 > P4 > P5 > P6
```

- **P2 first** — artifact integrity and the noun/verb distinction are non-negotiable. If a candidate term fails the rigid-artifact or state-changing-act test, no other principle can reinstate it.
- **P3 second** — gatekeeping purity. A verb that neither gates nor produces (by P3's definition, including the pipeline-membership override) does not enter regardless of naming pressure from P5.
- **P1 third** — scope discipline and merge decisions. After identity and gatekeeping are settled, resolve collisions by scope.
- **P4 fourth** — closure. Use P4 to identify gaps after the vocabulary is otherwise stable; do not use it to force terms into the vocabulary before P2 and P3 have been satisfied.
- **P5 fifth** — comprehensiveness. Naming pressure from P5 can trigger addition only after P2–P4 have been evaluated. P5 overrides P3 only via the pipeline-membership override, not generally.
- **P6 last** — warrant is an entry check, not a veto over terms that satisfy P2–P5. A term that satisfies all five structural principles enters; P6 then confirms it has evidence. **If warrant is absent, the term is deferred, not permanently rejected.**

---
