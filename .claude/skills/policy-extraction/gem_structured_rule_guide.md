# Structured Rule Decomposition — Design Guide

## Purpose

This guide documents a proposed decomposition of verbatim rule strings (the `gem:ruleDescription` values now carried on `gem:PolicyRule` individuals) into structured RDF/OWL triples that a downstream process can consume to generate executable IF-THEN-ELSE logic. It uses **NCD 240.2 Group I sleep criterion** as the single worked example, sketches the schema model needed, enumerates the supporting instance individuals, and surfaces the open design choices that need resolution before the structured-decomposition schema is codified.

This document's **structured-decomposition** design does not propose immediate ontology changes (the first-class-rule *attachment* substrate it builds on — `gem:PolicyRule`, `gem:hasPolicyRule`, the narrowed `gem:ruleDescription` domain — is already codified and instance-promoted; see Status). It is a design artifact that informs the deferred ζ-schema extension (carry-forward from S49) and clarifies how today's verbatim-string rule-description methodology relates to tomorrow's structured form.

## Status

- **Substrate fully codified and instance-promoted; structured decomposition deferred.** The schema substrate for first-class rule entities, coverage qualifiers, and rule categorization is fully codified in `GEM_ontology.ttl`, and the instance migration onto it is complete. The substrate was reached in three steps: S67 Phase 1 codified `gem:PolicyRule` (the class), `gem:hasPolicyRule` (the predicate linking policies to rules), and `gem:ruleDescription` with domain extended to include `gem:PolicyRule` (later narrowed to `gem:PolicyRule` exclusively at S86 — see Migration path). S69 Phase 3 sub-cycle (a) codified the CoverageQualifier hierarchy (S68 Cycle 3): `gem:CoverageQualifier` (abstract parent), `gem:CoverageRestriction` and `gem:CoverageExclusion` (concrete subclasses), `gem:CoverageOutcome` (stub class), the umbrella predicate `gem:hasCoverageQualifier` with sub-properties `gem:hasCoverageRestriction` and `gem:hasCoverageExclusion`, the `gem:RestrictionType` controlled-vocabulary class with four initial values, and supporting properties (`gem:restrictionType`, `gem:restrictionConcept`, `gem:restrictionDescription`, `gem:excludedConcept`, `gem:exclusionDescription`). S69 Phase 3 sub-cycle (b+c) codified the rule-categorization vocabulary (S68 Cycle 5): `gem:RuleDomain` and `gem:RuleType` as peer controlled-vocabulary classes (no umbrella) with the supporting properties `gem:ruleDomain` and `gem:ruleType` on `gem:PolicyRule`, the 3 RuleDomain values (`_screening`, `_hibc`, `_crossCutting`), and the 15 RuleType values (`_coverageScope`, `_eligibility`, `_frequency`, `_settingDefinition`, `_credentialedActor`, `_serviceDefinition`, `_serviceStandard`, `_riskFactor`, `_riskDetermination`, `_documentation`, `_nonCoverage`, `_costSharing`, `_concurrentServices`, `_statutoryFraming`, `_definition`). **Instance promotion is complete:** all 391 `gem:PolicyRule` individuals have been minted from the existing `gem:ruleDescription` strings, with `gem:ruleType` (and `gem:ruleDomain` where applicable) triples attached — Phase 3 migrated `gem:CMSpolicy`-scope rules (S85) and Phase 4 extended the pattern to `gem:AnchoredCodingScope` subjects and narrowed `gem:ruleDescription`'s domain to `gem:PolicyRule` exclusively (closeout S86). What remains deferred is the **structured decomposition**: the properties on `gem:CoverageOutcome` (`gem:decision`, the `gem:CoverageDecision` controlled vocabulary, and the gem:LogicalExpression family) remain pending Phase 2 design refinement per the Deferment Posture below until the claim-data substrate is better understood.
- **Canonical file set member** since S68 Cycle 1.
- **Source-of-truth boundary preserved.** The verbatim rule string (in `gem:ruleDescription`) remains the authoritative source; the structured form is derived. This matches the existing architectural pattern in GEM (e.g., `gem:ClinicalConcept` carries verbatim Governing Text in `gem:description`; the concept's identity is the atomic structured form).
- **Design decisions:** six of seven open design decisions are resolved as of S68; one is wholly deferred (Decision 5 — measurement context composition) and two have evaluation-component deferrals (Decisions 4 and 7). See §Deferment Posture for the deferment rationale.

## Deferment Posture

Some design questions in this document concern how a structured rule will be *evaluated* against claim data — what concrete data shape the rule operates over, how matching is defined, how derived quantities are computed. These questions are intentionally deferred until the project has a clearer view of the Medicare Claim properties that rules will be evaluated against.

The reasoning: structural choices that govern *shape* (which classes exist, how individuals are typed, how they reference one another) can be made well from policy prose alone. Evaluation choices that govern *semantics* (how a comparator binds to a claim property's datatype, what "decrease from baseline" computes over, whether a multi-context predicate is conjunctive or disjunctive) depend on the data substrate. Locking in evaluation choices before that substrate is understood risks designing for the wrong target.

When a decision in this document is marked **Status (Sxx): Deferred**, the deferment reasoning is recorded with it. Resolved and deferred decisions coexist; the structural form continues to evolve from policy prose while the evaluation form waits for the claim-data work.

## Background

The current `gem:ruleDescription` property is a datatype property whose range is `xsd:string`. Its own schema description acknowledges the intentional non-atomicity:

> The string form is intentionally non-atomic; future schema work will decompose rules into atomic component properties.

The S49 carry-forward (per userMemories: *"first-class `gem:Rule` entities with `gem:parentRule` structural links (ζ schema extension)"*) sketched the direction without resolving the model. This guide's worked walk-through informed the resolution; S67 Phase 1 codified the schema substrate, naming the rule class `gem:PolicyRule` rather than the bare `gem:Rule` originally sketched (and the linking predicate from policies to rules `gem:hasPolicyRule` rather than `gem:parentRule`).

---

## Worked Scenario: NCD 240.2 Group I Sleep Criterion

### Source text (verbatim)

From NCD 240.2 Section B, Group I, second bullet:

> *Sentence 1:* An arterial PO2 at or below 55 mm Hg, or an arterial oxygen saturation at or below 88%, taken during sleep for a patient who demonstrates an arterial PO2 at or above 56 mm Hg, or an arterial oxygen saturation at or above 89%, while awake; or a greater than normal fall in oxygen level during sleep (a decrease in arterial PO2 more than 10 mm Hg, or decrease in arterial oxygen saturation more than 5%) associated with symptoms or signs reasonably attributable to hypoxemia (e.g., impairment of cognitive processes and nocturnal restlessness or insomnia).
>
> *Sentence 2:* In either of these cases, coverage is provided only for use of oxygen during sleep, and then only one type of unit will be covered.
>
> *Sentence 3:* Portable oxygen, therefore, would not be covered in this situation.

### Logical analysis

Sentence 1 contains two qualifying scenarios separated by *"; or"*. Both scenarios lead to the same coverage outcome (Sentences 2 + 3).

**Statement A — Low absolute thresholds during sleep with awake baseline:**

```
IF (PO2_during_sleep ≤ 55 mm Hg  OR  SpO2_during_sleep ≤ 88%)
   AND (PO2_while_awake ≥ 56 mm Hg  OR  SpO2_while_awake ≥ 89%)
THEN cover oxygen during sleep only, one unit only, no portable oxygen
```

**Statement B — Oxygen-fall during sleep with hypoxemia symptoms:**

```
IF (PO2_decrease_during_sleep > 10 mm Hg  OR  SpO2_decrease_during_sleep > 5%)
   AND patient has symptoms or signs reasonably attributable to hypoxemia
THEN cover oxygen during sleep only, one unit only, no portable oxygen
```

The internal `OR`s within each scenario (PO2-vs-SpO2; PO2-decrease-vs-SpO2-decrease) do not fork into additional IF statements — they are disjunctive conditions within a single Boolean expression. Each scenario produces one IF.

### Today's representation (verbatim string form)

Two `gem:ruleDescription` strings on `gemi:ncd240.2`, one per qualifying scenario, each absorbing the shared outcome footer (Sentences 2 + 3) verbatim. The *"either of these cases"* phrasing survives in both rule strings. The apparent dangling resolves when both rules sit in the graph together (jigsaw-puzzle-piece principle in microcosm; cross-policy resolution mechanism applied within a single policy).

### Tomorrow's representation (structured form, proposed)

Two `gem:PolicyRule` individuals, each pointing at:
- Its own `gem:LogicalAnd` qualifying-condition tree (with `gem:LogicalOr` branches and `gem:AtomicPredicate` leaves), and
- The **same** `gem:CoverageOutcome` individual (the shared outcome that *"either of these cases"* names in the source).

The discourse-level *"either"* back-reference becomes a structural link: both Rules point at one Outcome. No paraphrasing required because the structured form does not carry source discourse — that job belongs to the verbatim string.

---

## Schema Model

### Conceptual layering

```
gem:PolicyRule
   ├── dc:source                        →  gem:CMSpolicy / gem:AnchoredCodingScope     [EXISTING]
   ├── gem:refersToQualificationGroup   →  gem:QualificationGroup                       [EXISTING, optional]
   ├── gem:ruleDescription              →  xsd:string                                   [EXISTING; domain = gem:PolicyRule exclusively (S86)]
   ├── gem:ruleDomain                   →  gem:RuleDomain (0..n)                        [S68-PROPOSED]
   ├── gem:ruleType                     →  gem:RuleType (0..n)                          [S68-PROPOSED]
   ├── gem:ruleQualifyingCondition      →  gem:LogicalExpression                        [PROPOSED]
   │                                          ├── gem:LogicalAnd       [PROPOSED, subclass]
   │                                          ├── gem:LogicalOr        [PROPOSED, subclass]
   │                                          ├── gem:LogicalNot       [PROPOSED, subclass]
   │                                          └── gem:AtomicPredicate  [PROPOSED, subclass]
   │                                                  ├── gem:NumericPredicate     [PROPOSED]
   │                                                  └── gem:ConditionalPredicate [PROPOSED]
   └── gem:ruleOutcome                  →  gem:CoverageOutcome                          [PROPOSED]
                                              ├── gem:decision         →  gem:CoverageDecision           [PROPOSED, controlled vocab]
                                              ├── gem:hasCoverageRestriction      →  gem:CoverageRestriction (0..n) [PROPOSED]
                                              └── gem:hasCoverageExclusion        →  gem:CoverageExclusion (0..n)   [PROPOSED]
```

### New entity types

#### `gem:PolicyRule`

A first-class rule entity. The class `gem:PolicyRule` is codified in `GEM_ontology.ttl` since S67 Phase 1, along with the umbrella predicate `gem:hasPolicyRule` linking a `gem:CMSpolicy` (or `gem:AnchoredCodingScope`) to its rules. The property `gem:ruleDescription` — which previously held verbatim rule strings on policies and anchor-scope subjects — had its domain extended in S67 Phase 1 to also accept `gem:PolicyRule` subjects, and was narrowed to `gem:PolicyRule` exclusively at the S86 Phase-4 closeout (rule strings now attach only to `gem:PolicyRule` individuals, reached from policy / anchor-scope subjects via `gem:hasPolicyRule`).

Properties on `gem:PolicyRule`:
- `dc:source` (object) — the source policy or anchored coding scope. Carried over from today's pattern.
- `gem:ruleDescription` (xsd:string) — the source-of-truth verbatim text. Existing property; its domain was extended to `gem:PolicyRule` at S67 Phase 1 and narrowed to `gem:PolicyRule` exclusively at S86.
- `gem:ruleQualifyingCondition` (object → `gem:LogicalExpression`) — the IF clause, expressed as a Boolean tree. [Proposed.]
- `gem:ruleOutcome` (object → `gem:CoverageOutcome`) — the THEN clause. [Proposed.]
- `gem:refersToQualificationGroup` (object → `gem:QualificationGroup`, optional) — if the rule is scoped to a qualifier group like Group I. Existing property; its domain is currently `gem:CMSpolicy` (it was **not** extended to `gem:PolicyRule` during the Phase 3/4 attachment migration). Attaching it to a rule individual — as the worked turtle below illustrates — belongs to the deferred structured-decomposition work (`deferred_proposals[72]` Phase 2) and would require extending the property's domain to include `gem:PolicyRule` when that work is taken up.
- `gem:ruleDomain` (object → `gem:RuleDomain`, 0..n) — see §`gem:RuleDomain`. [S68-proposed.]
- `gem:ruleType` (object → `gem:RuleType`, 0..n) — see §`gem:RuleType`. [S68-proposed.]

#### `gem:LogicalExpression` (abstract)

An abstract superclass for the Boolean composition tree. Never instantiated directly; its instances are always one of the four subclasses.

Subclasses:
- `gem:LogicalAnd` — conjunction; carries `gem:operand` (one or more, range `gem:LogicalExpression`).
- `gem:LogicalOr` — disjunction; same property shape.
- `gem:LogicalNot` — negation; carries exactly one `gem:operand`.
- `gem:AtomicPredicate` — the leaf type (see below).

Property:
- `gem:operand` (object → `gem:LogicalExpression`) — child node(s) in the Boolean tree. Used by `LogicalAnd`/`LogicalOr` (cardinality ≥ 2 by convention) and `LogicalNot` (cardinality exactly 1).

#### `gem:AtomicPredicate` (abstract)

The leaf of the Boolean tree. A single condition that evaluates to a Boolean. Two concrete subclasses:

##### `gem:NumericPredicate`

A numeric comparison. Used when the source asserts a measurement-against-threshold condition.

Properties:
- `gem:measurementVariable` (object → `gem:MeasurementVariable`)
- `gem:measurementContext` (object → `gem:MeasurementContext`)
- `gem:comparator` (object → `gem:Comparator`)
- `gem:thresholdValue` (xsd:decimal)
- `gem:thresholdUnit` (xsd:string — or perhaps an object reference to a unit vocabulary; see open design question)

Worked example: *"arterial PO2 at or below 55 mm Hg, taken during sleep"* →
```
variable    = gemi:conceptArterialPO2
context     = gemi:contextDuringSleep
comparator  = gem:atOrBelow
value       = 55
unit        = "mm Hg"
```

##### `gem:ConditionalPredicate`

A non-numeric clinical/conceptual condition. Used when the source asserts a presence/absence of some named condition or concept, rather than a measurement threshold.

Properties:
- `gem:clinicalConcept` (object → `gem:ClinicalConcept`) — what the condition is about.
- `gem:presence` (object → `gem:PresenceQualifier`) — controlled vocabulary: `gem:present`, `gem:absent`, possibly `gem:suspected`.

Worked example: *"associated with symptoms or signs reasonably attributable to hypoxemia"* →
```
clinicalConcept = gemi:conceptHypoxemiaSymptoms (or equivalent)
presence        = gem:present
```

#### `gem:MeasurementVariable`

What is being measured. Examples from NCD 240.2:
- arterial PO2
- arterial oxygen saturation
- arterial PO2 decrease (a delta — see deferred design question below)
- arterial oxygen saturation decrease

**Resolution (S68): peer class to `gem:ClinicalConcept`, with overlap.** MV and CC are independent classes; some entities play both roles, others play only one. An entity that plays both roles is minted as a single individual with both class memberships asserted directly (`rdf:type gem:ClinicalConcept, gem:MeasurementVariable`); no `owl:sameAs` aliasing, no separate URI per role. URI naming convention: dual-typed individuals use the `gemi:concept*` prefix (e.g., `gemi:conceptArterialPO2`); MV-only individuals use the `gemi:var*` prefix.

**Deferred (S68): delta-variable handling.** The "arterial PO2 decrease" case — a measurement derived from two readings of a base variable — likely warrants a `gem:DerivedMeasurementVariable` subclass with an operation reference, but the schema scope (single base vs. positional multi-base, operator vocabulary, claim-data binding) is deferred pending claim-data substrate understanding. See §Deferment Posture.

#### `gem:MeasurementContext`

When/how the measurement is taken. A controlled-vocabulary class — instances are project-defined named individuals.

Initial vocabulary (from NCD 240.2):
- `gem:contextDuringSleep`
- `gem:contextWhileAwake`
- `gem:contextAtRest`
- `gem:contextDuringExercise`
- `gem:contextBreathingRoomAir` (modifier, may compose with the above — pending the deferred composition decision)

**Deferred (S68): composition model.** How a single conjunctive context like *"at rest, breathing room air"* is represented — atomic single URI, base-plus-modifier compositional, or list-on-predicate — is deferred pending claim-data substrate understanding. The broader question of how predicate evaluation handles conjunctions and disjunctions across measurement-variable / clinical-concept references (including the matching cardinality of `gem:measurementContext`) is part of this deferment. See §Deferment Posture.

#### `gem:Comparator`

A small controlled vocabulary of comparison operators. Defined as named individuals in the ontology (not the instance file).

Vocabulary (initial; expanded as policy rules require):
- `gem:atOrBelow` (≤)
- `gem:atOrAbove` (≥)
- `gem:greaterThan` (>)
- `gem:lessThan` (<)
- `gem:equals` (=)
- (possibly more for ranges: `gem:between`, etc.)

**Resolution (S68): Project-defined named individuals.** SHACL constraint vocabulary and OWL2 datatype facets exist for adjacent concerns (data-shape constraints and datatype restrictions, respectively) — neither aligns with the IF/THEN evaluation use case. Project-defined named individuals keep semantics aligned with the rule-evaluation purpose. Naming convention: unprefixed form (`gem:atOrBelow`, etc.) — the surrounding `gem:comparator` predicate identifies the role.

**Deferred (S68): full vocabulary scope and datatype binding.** The initial numeric comparators above are a starting set. Additional categories may be needed as concrete policy rules surface them: temporal comparators (*"within 30 days of …"*), set-membership comparators (*"diagnosis code in this list"*), string/code comparators, range comparators. How each comparator binds to specific claim-data datatypes (e.g., does `gem:atOrBelow` know to compare numerically or lexically based on the operand type?) is also deferred. See §Deferment Posture.

#### `gem:CoverageOutcome`

Wraps the THEN clause of an IF/THEN: what coverage decision is reached, plus the restrictions and exclusions that apply when the decision is reached.

Properties:
- `gem:decision` (object → `gem:CoverageDecision`) — controlled vocabulary: `gem:covered`, `gem:notCovered`, possibly `gem:mac_discretion`.
- `gem:hasCoverageRestriction` (object → `gem:CoverageRestriction`, 0..n) — modifies the decision (e.g., "covered, but only X").
- `gem:hasCoverageExclusion` (object → `gem:CoverageExclusion`, 0..n) — explicitly excluded sub-cases (e.g., "covered, but not portable oxygen").

Outcome **sharing** across Rules is supported when source-justified: two distinct Rules can point at the same `gem:CoverageOutcome` individual when ONE source act names that outcome for the multiple Rules (this is how the source's *"either of these cases"* resolves structurally). When *different* source acts produce semantically-identical outcomes, the extractor mints distinct outcomes; SME may later assert `owl:sameAs` if equivalence holds. This matches the project-wide *catalog phrasings; don't consolidate* posture.

#### `gem:CoverageQualifier` (abstract)

A condition that qualifies the scope of coverage when an outcome's positive decision applies. Two concrete subclasses — `gem:CoverageRestriction` (narrows the use case of what's covered) and `gem:CoverageExclusion` (carves out a sub-type that's not covered) — share this abstract parent because they both qualify the coverage decision in the same structural role on the outcome.

Properties on `gem:CoverageOutcome`:
- `gem:hasCoverageQualifier` (object → `gem:CoverageQualifier`, 0..n) — umbrella predicate covering any qualifier.
- `gem:hasCoverageRestriction` — `rdfs:subPropertyOf gem:hasCoverageQualifier`, range narrowed to `gem:CoverageRestriction`.
- `gem:hasCoverageExclusion` — `rdfs:subPropertyOf gem:hasCoverageQualifier`, range narrowed to `gem:CoverageExclusion`.

This follows the S60 precedent established for `gem:AnchoredCodingScope` over `gem:PolicyGroup` + `gem:PolicyCodingRule`.

##### `gem:CoverageRestriction`

A restriction on a positive coverage decision. Subclass of `gem:CoverageQualifier`. Carries enough structure for downstream evaluation.

Worked examples from this scenario:
- `gemi:restrictionOxygenDuringSleepOnly` — restricts the use case (oxygen *only* during sleep).
- `gemi:restrictionOneUnitOnly` — restricts the count (only one type of unit).

Properties (proposed):
- `gem:restrictionType` (object → controlled vocab: use-case, count, duration, frequency, …)
- `gem:restrictionConcept` (object → `gem:ClinicalConcept`, optional) — what the restriction is about.
- `gem:restrictionValue` (mixed datatype, optional) — for count/duration/frequency restrictions. **Deferred at S69 Phase 3a** pending claim-data substrate understanding; see §Deferment Posture. Until codified, the value lives within `gem:restrictionDescription`.
- `gem:restrictionDescription` (xsd:string) — human-readable summary.

##### `gem:CoverageExclusion`

An explicit exclusion within a coverage outcome. Subclass of `gem:CoverageQualifier`. Distinct from `gem:CoverageRestriction` because exclusions name something that is *not* covered, while restrictions narrow what *is* covered.

Worked example: `gemi:exclusionPortableOxygen` — references `gemi:conceptPortableOxygen` as the excluded item.

Properties (proposed):
- `gem:excludedConcept` (object → `gem:ClinicalConcept`)
- `gem:exclusionDescription` (xsd:string)

#### `gem:RuleDomain`

What clinical activity within a policy a rule applies to. A controlled-vocabulary class — instances are project-defined named individuals in `GEM_ontology.ttl`. Human-readable definitions and evolution history for each value live in `gem_rule_categories.md`.

Initial vocabulary (mirrors `gem_rule_categories.md` §Axis 1 — Domain applicability):
- `gem:ruleDomain_screening` — applies to STI laboratory screening only (NCD 210.10).
- `gem:ruleDomain_hibc` — applies to HIBC behavioral counseling only (NCD 210.10).
- `gem:ruleDomain_crossCutting` — applies to both/either service within a multi-domain policy.

Extend with new domain values as new multi-activity policies arrive.

Property on `gem:PolicyRule`:
- `gem:ruleDomain` (object → `gem:RuleDomain`, 0..n) — a rule may carry multiple domain values when the source's framing applies to multiple activities.

A rule with no `gem:ruleDomain` triple is acceptable: single-domain policies don't always need an explicit domain tag (the policy itself names the domain). Domain tagging is most useful when one policy spans multiple activities.

#### `gem:RuleType`

What kind of evaluator criterion a rule expresses. A controlled-vocabulary class — instances are project-defined named individuals in `GEM_ontology.ttl`. Human-readable definitions and evolution history for each value live in `gem_rule_categories.md`.

Initial vocabulary (mirrors `gem_rule_categories.md` §Axis 2 — Rule type; MD-file hyphenated strings are mapped to camelCase in URI local names):
- `gem:ruleType_coverageScope` — what is covered, at what level.
- `gem:ruleType_eligibility` — who/when is eligible.
- `gem:ruleType_frequency` — how often / repeat-screening intervals.
- `gem:ruleType_settingDefinition` — what setting is required (positive definition + exclusions).
- `gem:ruleType_credentialedActor` — who can order/perform/provide.
- `gem:ruleType_serviceDefinition` — defines a service itself.
- `gem:ruleType_serviceStandard` — technical standards (FDA, CLIA, etc.).
- `gem:ruleType_riskFactor` — enumerates risk factors.
- `gem:ruleType_riskDetermination` — who/how determines risk.
- `gem:ruleType_documentation` — documentation requirements.
- `gem:ruleType_nonCoverage` — what is NOT covered.
- `gem:ruleType_costSharing` — patient cost obligations.
- `gem:ruleType_concurrentServices` — what services can be billed on the same date / together.
- `gem:ruleType_statutoryFraming` — scope-defining reference to statute.
- `gem:ruleType_definition` — generic catch-all for definitional rules not covered above.

Extend with new rule-type values as new policies surface them. Retired values are documented in `gem_rule_categories.md` §Retired rule-type values.

Property on `gem:PolicyRule`:
- `gem:ruleType` (object → `gem:RuleType`, 0..n) — a rule may carry multiple rule-type values when its content spans multiple criterion categories.

### Reused existing GEM entities

| Existing entity | Role in structured form |
|:---|:---|
| `gem:CMSpolicy` | `gem:PolicyRule` traces back via `dc:source`. |
| `gem:AnchoredCodingScope` | `gem:PolicyRule` traces back via `dc:source` when scoped. |
| `gem:ClinicalConcept` | Referenced by `gem:ConditionalPredicate`, `gem:CoverageRestriction`, and `gem:CoverageExclusion`. Possibly the supertype of `gem:MeasurementVariable`. |
| `gem:QualificationGroup` | Rules carry `gem:refersToQualificationGroup` linking back to (e.g.) `gemi:groupI`. |
| `gem:ProviderCredential` | (Not directly used in this scenario, but Rules whose qualifying conditions involve "the test was performed by a qualified provider" would link to credentials.) |

### Today's `gem:ruleDescription` — how it relates

The string-form `gem:ruleDescription` property carries the **verbatim** text that the structured PolicyRule will derive from. In the migration to structured form:

- The string has moved from being a `gem:ruleDescription` value on a `gem:CMSpolicy` (or anchor-scope subject) to being a `gem:ruleDescription` value on the `gem:PolicyRule` individual. Since the S86 closeout, `gem:ruleDescription` on a policy or anchor-scope subject is no longer schema-legal — its domain is `gem:PolicyRule` exclusively — and the subject links to its rules via `gem:hasPolicyRule`.
- The structured decomposition (`gem:ruleQualifyingCondition` + `gem:ruleOutcome`) is added alongside the verbatim string, not in place of it.
- The verbatim string remains the **source-of-truth provenance**; the structured form remains a **derived interpretation**.

This mirrors how `gem:ClinicalConcept` works today — verbatim Governing Text in `gem:description`, structured identity in the URI and `gem:prefLabel`.

---

## Worked Decomposition

### Required supporting instance individuals

The two Rules below need the following supporting instances. Some already exist in the graph; others would be minted as part of this Rule's instantiation. Delta-variable individuals (the two "decrease from baseline" entries below) are deferred from this cycle's instantiation pending the deferred `gem:DerivedMeasurementVariable` resolution.

#### Measurement variables

| URI | Label | Status |
|:---|:---|:---|
| `gemi:conceptArterialPO2` | arterial PO2 | Dual-typed (`gem:ClinicalConcept` + `gem:MeasurementVariable`). If already minted as a CC, add MV typing; otherwise mint with both types. |
| `gemi:conceptArterialOxygenSaturation` | arterial oxygen saturation | Dual-typed. Same pattern. |
| *(deferred)* | arterial PO2 decrease from baseline | **Deferred (S68)** — pending `gem:DerivedMeasurementVariable` resolution. |
| *(deferred)* | arterial oxygen saturation decrease from baseline | **Deferred (S68)** — same. |

#### Measurement contexts

| URI | Label | Status |
|:---|:---|:---|
| `gemi:contextDuringSleep` | during sleep | New |
| `gemi:contextWhileAwake` | while awake | New |
| `gemi:contextAtRest` | at rest, breathing room air | New (composition open question) |
| `gemi:contextDuringExercise` | during exercise | New |

#### Comparators (ontology-level named individuals)

| URI | Symbol | Status |
|:---|:---|:---|
| `gem:atOrBelow` | ≤ | New, ontology-level |
| `gem:atOrAbove` | ≥ | New, ontology-level |
| `gem:greaterThan` | > | New, ontology-level |
| `gem:lessThan` | < | New, ontology-level |

#### Clinical concept references

| URI | Status |
|:---|:---|
| `gemi:conceptHypoxemiaSymptoms` | New (or repurpose `gemi:conceptHypoxemia` with the symptom-presence framing) |
| `gemi:conceptPortableOxygen` | **Exists** (already minted on NCD 240.2) |
| `gemi:conceptOxygen` | **Exists** |

#### Coverage restrictions and exclusions

| URI | Label | Status |
|:---|:---|:---|
| `gemi:restrictionOxygenDuringSleepOnly` | oxygen use restricted to during sleep | New |
| `gemi:restrictionOneUnitOnly` | one type of unit only | New |
| `gemi:exclusionPortableOxygen` | portable oxygen excluded | New |

### Statement A — full turtle

```turtle
# --- The Rule ---

gemi:rule_ncd240.2_groupI_sleep_lowThresholds a gem:PolicyRule ;
    dc:source gemi:ncd240.2 ;
    gem:refersToQualificationGroup gemi:groupI ;
    gem:ruleDescription "An arterial PO2 at or below 55 mm Hg, or an arterial oxygen saturation at or below 88%, taken during sleep for a patient who demonstrates an arterial PO2 at or above 56 mm Hg, or an arterial oxygen saturation at or above 89%, while awake. In either of these cases, coverage is provided only for use of oxygen during sleep, and then only one type of unit will be covered. Portable oxygen, therefore, would not be covered in this situation." ;
    gem:ruleQualifyingCondition gemi:cond_ncd240.2_groupI_sleep_lowThresholds_AND ;
    gem:ruleOutcome gemi:outcome_ncd240.2_groupI_sleep_shared .

# --- Qualifying condition tree (top-level AND of two ORs) ---

gemi:cond_ncd240.2_groupI_sleep_lowThresholds_AND a gem:LogicalAnd ;
    gem:operand gemi:cond_sleepMeasurement_low_OR ;
    gem:operand gemi:cond_awakeMeasurement_baseline_OR .

# Branch 1: sleep measurement low (PO2 OR SpO2)
gemi:cond_sleepMeasurement_low_OR a gem:LogicalOr ;
    gem:operand gemi:pred_PO2_duringSleep_atOrBelow_55 ;
    gem:operand gemi:pred_SpO2_duringSleep_atOrBelow_88 .

# Branch 2: awake measurement at or above baseline (PO2 OR SpO2)
gemi:cond_awakeMeasurement_baseline_OR a gem:LogicalOr ;
    gem:operand gemi:pred_PO2_whileAwake_atOrAbove_56 ;
    gem:operand gemi:pred_SpO2_whileAwake_atOrAbove_89 .

# --- Atomic numeric predicates (leaves) ---

gemi:pred_PO2_duringSleep_atOrBelow_55 a gem:NumericPredicate ;
    gem:measurementVariable gemi:conceptArterialPO2 ;
    gem:measurementContext gemi:contextDuringSleep ;
    gem:comparator gem:atOrBelow ;
    gem:thresholdValue "55"^^xsd:decimal ;
    gem:thresholdUnit "mm Hg" .

gemi:pred_SpO2_duringSleep_atOrBelow_88 a gem:NumericPredicate ;
    gem:measurementVariable gemi:conceptArterialOxygenSaturation ;
    gem:measurementContext gemi:contextDuringSleep ;
    gem:comparator gem:atOrBelow ;
    gem:thresholdValue "88"^^xsd:decimal ;
    gem:thresholdUnit "%" .

gemi:pred_PO2_whileAwake_atOrAbove_56 a gem:NumericPredicate ;
    gem:measurementVariable gemi:conceptArterialPO2 ;
    gem:measurementContext gemi:contextWhileAwake ;
    gem:comparator gem:atOrAbove ;
    gem:thresholdValue "56"^^xsd:decimal ;
    gem:thresholdUnit "mm Hg" .

gemi:pred_SpO2_whileAwake_atOrAbove_89 a gem:NumericPredicate ;
    gem:measurementVariable gemi:conceptArterialOxygenSaturation ;
    gem:measurementContext gemi:contextWhileAwake ;
    gem:comparator gem:atOrAbove ;
    gem:thresholdValue "89"^^xsd:decimal ;
    gem:thresholdUnit "%" .
```

### Statement B — full turtle

```turtle
# --- The Rule ---

gemi:rule_ncd240.2_groupI_sleep_oxygenFall a gem:PolicyRule ;
    dc:source gemi:ncd240.2 ;
    gem:refersToQualificationGroup gemi:groupI ;
    gem:ruleDescription "A greater than normal fall in oxygen level during sleep (a decrease in arterial PO2 more than 10 mm Hg, or decrease in arterial oxygen saturation more than 5%) associated with symptoms or signs reasonably attributable to hypoxemia (e.g., impairment of cognitive processes and nocturnal restlessness or insomnia). In either of these cases, coverage is provided only for use of oxygen during sleep, and then only one type of unit will be covered. Portable oxygen, therefore, would not be covered in this situation." ;
    gem:ruleQualifyingCondition gemi:cond_ncd240.2_groupI_sleep_oxygenFall_AND ;
    gem:ruleOutcome gemi:outcome_ncd240.2_groupI_sleep_shared .

# --- Qualifying condition tree (top-level AND of fall-OR and symptoms predicate) ---

gemi:cond_ncd240.2_groupI_sleep_oxygenFall_AND a gem:LogicalAnd ;
    gem:operand gemi:cond_oxygenFall_OR ;
    gem:operand gemi:pred_hypoxemiaSymptoms_present .

# Branch: fall in PO2 OR fall in SpO2
gemi:cond_oxygenFall_OR a gem:LogicalOr ;
    gem:operand gemi:pred_PO2decrease_duringSleep_gt_10 ;
    gem:operand gemi:pred_SpO2decrease_duringSleep_gt_5 .

# --- Atomic numeric predicates (fall thresholds) ---
# NOTE: The two predicates below reference delta variables (`gemi:varArterialPO2Decrease`,
# `gemi:varArterialOxygenSaturationDecrease`). Per S68, the `gem:DerivedMeasurementVariable`
# schema (which would govern their proper typing and derivation-operation structure) is
# deferred pending claim-data substrate understanding. URIs and references are shown for
# continuity; final form is contingent on that deferred resolution.

gemi:pred_PO2decrease_duringSleep_gt_10 a gem:NumericPredicate ;
    gem:measurementVariable gemi:varArterialPO2Decrease ;          # deferred (S68)
    gem:measurementContext gemi:contextDuringSleep ;
    gem:comparator gem:greaterThan ;
    gem:thresholdValue "10"^^xsd:decimal ;
    gem:thresholdUnit "mm Hg" .

gemi:pred_SpO2decrease_duringSleep_gt_5 a gem:NumericPredicate ;
    gem:measurementVariable gemi:varArterialOxygenSaturationDecrease ;  # deferred (S68)
    gem:measurementContext gemi:contextDuringSleep ;
    gem:comparator gem:greaterThan ;
    gem:thresholdValue "5"^^xsd:decimal ;
    gem:thresholdUnit "%" .

# --- Conditional predicate (clinical condition, not a numeric comparison) ---

gemi:pred_hypoxemiaSymptoms_present a gem:ConditionalPredicate ;
    gem:clinicalConcept gemi:conceptHypoxemiaSymptoms ;
    gem:presence gem:present .
```

### Shared coverage outcome (referenced by both Statement A and Statement B)

```turtle
gemi:outcome_ncd240.2_groupI_sleep_shared a gem:CoverageOutcome ;
    gem:decision gem:covered ;
    gem:hasCoverageRestriction gemi:restrictionOxygenDuringSleepOnly ;
    gem:hasCoverageRestriction gemi:restrictionOneUnitOnly ;
    gem:hasCoverageExclusion gemi:exclusionPortableOxygen .

# --- Restrictions ---

gemi:restrictionOxygenDuringSleepOnly a gem:CoverageRestriction ;
    gem:restrictionType gem:restrictionType_useCase ;
    gem:restrictionConcept gemi:contextDuringSleep ;
    gem:restrictionDescription "Coverage is provided only for use of oxygen during sleep." .

gemi:restrictionOneUnitOnly a gem:CoverageRestriction ;
    gem:restrictionType gem:restrictionType_count ;
    gem:restrictionValue "1"^^xsd:int ;                            # deferred (S69)
    gem:restrictionDescription "Only one type of unit will be covered." .

# --- Exclusion ---

gemi:exclusionPortableOxygen a gem:CoverageExclusion ;
    gem:excludedConcept gemi:conceptPortableOxygen ;
    gem:exclusionDescription "Portable oxygen would not be covered in this situation." .
```

### Triple count summary

For just the sleep bullet (Statements A + B + shared outcome):

| Component | Triples |
|:---|---:|
| Rule individuals (2 Rules × ~5 properties each) | ~10 |
| Logical composition nodes (2 top-level ANDs, 3 ORs) | ~10 |
| Atomic predicates (6 numeric + 1 conditional) | ~35 |
| Shared CoverageOutcome | 4 |
| Restrictions (2) + Exclusion (1) | ~10 |
| Supporting individuals (variables, contexts, restrictions, exclusion) — minted once | ~25 |
| **Total — first instantiation** | **~95** |
| **Total — incremental (per additional similar bullet, reusing supporting individuals)** | **~60** |

By comparison, today's representation of the same content is **2 triples** (two `gem:ruleDescription` strings on `gemi:ncd240.2`).

The cost ratio of ~30–50× is consistent with the principle that structured forms trade verbosity for queryability and downstream consumability.

---

## Open Design Decisions

Surfaced here for resolution before ζ-schema codification. None are resolved by this document.

### 1. `gem:MeasurementVariable` — subclass of `gem:ClinicalConcept` or peer?

`gemi:conceptPO2` already exists as a `gem:ClinicalConcept`. A `gem:MeasurementVariable` named "arterial PO2" is conceptually the same thing in the variable role. Two options were considered:

- **Subclass.** `gem:MeasurementVariable rdfs:subClassOf gem:ClinicalConcept`. Every MV would also be a CC by subsumption.
- **Peer.** Independent classes with possible overlap. Some entities play both roles; some play only one.

**Resolution (S68): Peer classes with overlap.** Some clinical concepts are measurement variables (e.g., `gemi:conceptArterialPO2`), but many are not (e.g., `gemi:conceptHypoxemiaSymptoms` — a clinical condition, not a measurable parameter). Some measurement variables are not clinical concepts on their own (the derived deltas — see the deferred sub-question below). Entities that play both roles are minted as a single individual with both class memberships asserted directly (`rdf:type gem:ClinicalConcept, gem:MeasurementVariable`). URI naming convention: `gemi:concept*` for dual-typed individuals; `gemi:var*` for MV-only individuals.

**Deferred (S68): delta-variable handling.** The "arterial PO2 decrease from baseline" case requires an operation over two readings of a base variable, suggesting a `gem:DerivedMeasurementVariable` subclass with a derivation-operation reference. The schema scope — single-base vs. multi-base operators, positional roles for asymmetric operations, what operator vocabulary is needed, how operations bind to claim-data evaluation — is deferred pending claim-data substrate understanding. See §Deferment Posture.

### 2. Outcome sharing across Rules — supported or per-Rule?

The sleep bullet decomposition shares one `gem:CoverageOutcome` between two `gem:PolicyRule`s. This is compact and structurally honest to the source's *"either of these cases"* framing. But it adds coupling — modifying the outcome affects both Rules.

- **Sharing supported.** As demonstrated. Outcomes are first-class individuals.
- **Per-Rule outcomes only.** Each Rule gets its own outcome, even when they're semantically identical. Cleaner isolation; more verbose.

**Resolution (S68): Sharing supported, when source-justified.** Two distinguishable source patterns drive the extractor's behavior:

- **Pattern A** (worked-example case): ONE source act names ONE outcome for multiple conditions/Rules (the *"In either of these cases…"* framing). → Mint one shared outcome individual; both Rules reference it. Source-faithful.
- **Pattern B** (cross-source case): DIFFERENT source acts produce semantically-identical-looking outcomes. → Mint distinct outcome individuals per source act; SME may later assert `owl:sameAs` if equivalence holds.

This is consistent with the project-wide *catalog phrasings; don't consolidate* principle — the extractor reads source structure, never adjudicates semantic equivalence across source acts.

### 3. Restriction and exclusion — distinct classes or polarity-flagged single class?

`gem:CoverageRestriction` and `gem:CoverageExclusion` are similar shapes — both reference a concept and provide a description. They differ in semantics: restriction *narrows* a positive decision; exclusion *carves out* a negative within a positive decision.

- **Distinct classes** (as drafted). Different downstream consumers might handle them differently; the type itself carries semantic information.
- **Polarity-flagged single class.** One class with `gem:polarity ∈ {restrict, exclude}`.

**Resolution (S68): Distinct classes under an abstract `gem:CoverageQualifier` parent.** Concrete subclasses `gem:CoverageRestriction` and `gem:CoverageExclusion` keep their distinct shapes — the semantic distinction (narrowing vs. carving out) is real and durable, and type-driven dispatch is cleaner downstream than polarity-flag inspection. An abstract `gem:CoverageQualifier` parent class captures what restrictions and exclusions ontologically share (both qualify the scope of coverage when the outcome's decision applies) and enables polymorphic queries over both via the umbrella predicate `gem:hasCoverageQualifier` (with `gem:hasCoverageRestriction` and `gem:hasCoverageExclusion` as sub-properties). This follows the S60 precedent established for `gem:AnchoredCodingScope` over `gem:PolicyGroup` + `gem:PolicyCodingRule`. See the `gem:CoverageQualifier` definition in the Schema Model section above.

### 4. Comparator vocabulary — project-defined or reuse a standard?

The drafted comparators (`gem:atOrBelow`, etc.) are project-defined named individuals. Alternatives:

- **Reuse SHACL.** `sh:lessThan`, `sh:lessThanOrEquals`, etc. — but SHACL comparators are constraints, not predicates over instance data.
- **Reuse OWL2 datatype facets.** `xsd:minInclusive`, `xsd:maxInclusive`, etc. — but these are for datatype restrictions, not data comparisons.
- **Project-defined.** Drafted above. Simple, expressive, fits the domain.

**Resolution (S68): Project-defined named individuals.** Structural choice: comparators are defined as named individuals in `GEM_ontology.ttl` under the `gem:` namespace, with the unprefixed form (`gem:atOrBelow`, `gem:greaterThan`, etc.). SHACL and OWL2 facets exist for adjacent concerns and would create semantic mismatch.

**Deferred (S68): full vocabulary scope and datatype binding.** The initial numeric vocabulary is a starting set; categories like temporal comparators, set-membership comparators, range comparators, and string/code comparators will be added as concrete policy rules surface the need. How each comparator binds to specific claim-data datatypes is deferred pending claim-data substrate understanding. See §Deferment Posture.

### 5. Measurement context composition

The source carries composite contexts like *"at rest, breathing room air"*. Options:

- **Atomic contexts only.** Mint `gemi:contextAtRestBreathingRoomAir` as one indivisible context.
- **Compositional contexts.** Allow `gem:contextModifier` to compose: `gemi:contextAtRest gem:contextModifier gemi:modifierBreathingRoomAir`.
- **List of contexts on the predicate.** `gem:measurementContext` becomes 0..n; the predicate carries multiple contexts simultaneously.

**Status (S68): Deferred — pending claim-data substrate understanding.** Choosing among these options requires understanding (a) how a predicate's matching semantics work against actual claim data (single-value match vs. any-of-list match; conjunctive vs. disjunctive aggregation) and (b) how multi-property conjunctions (*"at rest" AND "breathing room air"*) interact with multi-instance disjunctions (*"PO2 OR oxygen saturation"*). The project is still in the phase of collecting verbatim policy rules; additional worked examples are needed to evaluate the design options. See §Deferment Posture.

### 6. `gem:PolicyRule` categorization axes

Today's rule categorization (the `gem_rule_categories.md` axis-1/axis-2 taxonomy) attaches to `gem:ruleDescription` strings via the rule-categories file. Under the structured form, this could become first-class triples on `gem:PolicyRule` individuals:

```
gemi:rule_… a gem:PolicyRule ;
    gem:ruleDomain gem:ruleDomain_crossCutting ;
    gem:ruleType   gem:ruleType_eligibility .
```

**Resolution (S68): Promote categorization to first-class triples on `gem:PolicyRule` individuals.**

- **Property naming:** semantic, not positional — `gem:ruleDomain` and `gem:ruleType` (rather than `gem:ruleAxis1` / `gem:ruleAxis2`). Future additional axes are additive (e.g., `gem:ruleScope`, `gem:ruleJurisdiction`) without requiring positional-slot renumbering.
- **Vocabulary classes:** `gem:RuleDomain` and `gem:RuleType` as peer classes (no abstract `gem:RuleCategory` umbrella — domain and rule-type are independent classifications, not two flavors of a common concept; consumers query per-axis, not polymorphically).
- **Value-individual naming:** full-mirror form — `gem:ruleDomain_<value>` and `gem:ruleType_<value>`. The value's URI prefix matches the property name that takes it.
- **MD-file role transition:** at Phase 3 (when rule individuals are minted), `gem_rule_categories.md`'s per-policy assignment tables are read and promoted to `gem:ruleDomain` / `gem:ruleType` triples on each rule individual. The MD file evolves to focus on vocabulary definitions and evolution history; assignment tables become provenance/historical record.

Schema details for `gem:RuleDomain` and `gem:RuleType` are documented in the Schema Model section above.

### 7. Negation handling

`gem:LogicalNot` is drafted but not exercised in the sleep bullet. Worked example for §C: *"Angina pectoris in the absence of hypoxemia"* would decompose as:

```
LogicalAnd (
    ConditionalPredicate(clinicalConcept = anginaPectoris, presence = present),
    LogicalNot ( ConditionalPredicate(clinicalConcept = hypoxemia, presence = present) )
)
```

Or alternatively as a `ConditionalPredicate` with `presence = absent`, sidestepping `LogicalNot`. Both work; choosing one consistently matters more than which.

**Resolution (S68): Prefer `presence = absent` for single-concept negations; reserve `gem:LogicalNot` for negating compound expressions** (`LogicalAnd` or `LogicalOr` subtrees). Structural choice: this is an extractor consistency convention. When source prose says *"in the absence of X"* (single-concept negation), the extractor mints `ConditionalPredicate(X, presence = absent)`; when source prose negates a compound condition, the extractor mints `LogicalNot(compound)`. The convention keeps the Boolean tree shallow for the common case.

**Deferred (S68): semantic interpretation of "absent" against claim data.** What "absent" *means* in evaluation depends on the claim-data substrate. Possible interpretations: strong absence (concept not recorded anywhere), documented absence (explicitly recorded as absent or ruled-out), claim-specific absence (not on this claim's diagnoses), or temporal absence (not present at time-of-test). The two structural forms are not quite semantically equivalent under all interpretations — `LogicalNot(presence = present)` evaluates as "the assertion of presence is false" (which can include the no-information case), while `presence = absent` could be interpreted as either "absence is asserted as a positive fact" (requires documented absence) or as semantically identical to `LogicalNot(present)`. The eventual evaluation-layer designer must make this distinction explicit. See §Deferment Posture.

---

## Architectural Implications

### Relationship to current verbatim-string methodology

The verbatim string is and will remain the **source-of-truth provenance**. The structured form is **derived**. This preserves:

- **Source-fidelity (SKILL.md Core Principle #8)** — the verbatim string is the policy's prose; nothing is lost in translation because the translation is additive.
- **Verbatim-capture posture (SKILL.md §Rule Patterns corollary #3)** — the rule string retains the policy's wording including discourse-level back-references like *"either of these cases"*; the structured form replaces discourse with structural links, but does not replace the string.
- **Verbatim-cross-reference posture (corollary #4)** — when source rules reference other sections, the verbatim string preserves the reference; the structured form may or may not resolve it (depending on downstream needs).
- **Jigsaw-puzzle-piece principle (Core Principle #10)** — the structured form makes cross-policy composition more queryable but doesn't change the policy-by-policy authorship pattern.

### Granularity choices today should anticipate the structured form

The most important implication for today's verbatim-string rule-description backfill: **the granularity of `gem:ruleDescription` strings today should match the granularity of `gem:PolicyRule` individuals tomorrow.** When today's choice is "one rule string or two", ask the IF/THEN question:

> *If a downstream process were generating Python IF/THEN code from this source paragraph, how many IF statements would it produce?*

The answer to that question equals the natural count of `gem:PolicyRule` individuals — and therefore the natural count of `gem:ruleDescription` strings to write today.

This guidance is what produced the two-rule resolution for the sleep bullet at NCD 240.2 B4.

### Migration path

The attachment-substrate migration is complete (instance + schema). S67 Phase 1 codified the schema substrate (`gem:PolicyRule`, `gem:hasPolicyRule`, `gem:ruleDescription` domain-extended to `gem:PolicyRule`). The phases below are now done, except for the deferred structured decomposition in step 3:

1. ✅ **Codify the remaining schema vocabulary** in `GEM_ontology.ttl` — *complete.* S69 Phase 3a codified the CoverageQualifier hierarchy; S69 Phase 3 sub-cycle (b+c) codified the RuleDomain / RuleType vocabularies and their value individuals. Future cycles may add further terms (e.g., the deferred `gem:restrictionValue`, the `gem:CoverageDecision` controlled vocabulary, and any `gem:LogicalExpression`-family terms) when the claim-data substrate is better understood.
2. ✅ **Mint a `gem:PolicyRule` individual per existing `gem:ruleDescription` string** and re-attach the string to that rule individual — *complete.* All 391 rule strings were promoted: Phase 3 for `gem:CMSpolicy`-scope rules (S85) and Phase 4 for `gem:AnchoredCodingScope`-scope rules (S83–S85). A freshly promoted rule individual may be initially incomplete (no qualifying-condition tree, no outcome) — promoting the string to a first-class entity is enough.
3. **Decompose progressively (deferred — Phase 2).** Add the qualifying-condition tree and the coverage outcome incrementally, per rule, as the deferred structured-decomposition work proceeds. Rules without decomposition still serve their primary purpose (verbatim provenance + queryable string).
4. ✅ **Policy-direct attachments retired.** The S86 Phase-4 closeout formally **narrowed** `gem:ruleDescription`'s domain to `gem:PolicyRule` exclusively: a `gem:ruleDescription` triple on a `gem:CMSpolicy` or `gem:AnchoredCodingScope` subject is no longer schema-legal. The narrowing is enforced by `rdfs:domain`, by `gem:PolicyRuleShape`, and by the audit's `check_ruledescription_domain_conformance` (run on the asserted graph so a stray non-PolicyRule subject is caught at source rather than masked by RDFS domain inference).

The migration is non-breaking at each step: every `gem:PolicyRule` with `gem:ruleDescription` but no structured decomposition is still a valid rule. Downstream consumers that don't yet handle the structured form continue to read the verbatim string.

**Phase 3 vs Phase 4 boundary.** The instance-promotion work in point 2 above operates on `gem:ruleDescription` strings attached to policy instances ("Phase 3" within work item #72). The parallel promotion for strings attached to `gem:AnchoredCodingScope` subjects (`gem:PolicyGroup`, `gem:PolicyCodingRule`) is **Phase 4**, following Phase 3. Per-subject inventory is graph-recoverable at any time (SPARQL: `?s a gem:PolicyGroup ; gem:ruleDescription ?d`, and the parallel pattern for `gem:PolicyCodingRule`); per-policy deferral is also recorded in the Phase 3 migration stamps in `gem_rule_categories.md`. Phase 4 methodology — predicate from an anchor-scope subject to its `gem:PolicyRule` individuals, URI naming convention, migration-stamp shape, and SHACL coverage — was codified and executed across S83–S85, and the Phase-4 schema closeout (S86) narrowed `gem:ruleDescription`'s domain to `gem:PolicyRule` exclusively. Its operational prerequisites `deferred_proposals[75]` (SHACL coverage scan) and `deferred_proposals[77]` (SHACL invocation pattern) were both resolved at S78, ahead of Phase 4 execution.

**Phase 4 inventory tracking in handoffs.** Session handoffs report Phase 4 anchor-scope inventory as **two distinct lines**, not one. Line (i) — *Phase-3-deferred anchor-scope* — is a cumulative running count of anchor-scope `gem:ruleDescription` triples deferred *during* a Phase 3 cycle's policy migration (i.e., triples that were on `gem:PolicyGroup` or `gem:PolicyCodingRule` subjects of a policy whose policy-level rules were promoted in that cycle, and that were intentionally not promoted alongside). Line (ii) — *Phase 4 promotion inventory* — is the comprehensive count of all anchor-scope `gem:ruleDescription` triples on `gem:PolicyGroup` and `gem:PolicyCodingRule` subjects across the graph, regardless of origin, and is what Phase 4 will operate on when execution begins. The two counts diverge whenever anchor-scope `gem:ruleDescription` triples reach the graph by paths other than Phase 3 deferral (e.g., direct extraction on a policy that has not yet entered a Phase 3 cycle). Both lines are reconcilable to the graph via SPARQL; the two-line structure exists because (i) tracks Phase 3 cycle decisions session-by-session, while (ii) drives Phase 4 sizing. *Codified S75 (2026-06-21) after the S74 handoff's §3 line ambiguously conflated the two.* **Now historical:** Phase 4 was executed across S83–S85 and closed out at the schema level at S86; the anchor-scope `gem:ruleDescription` inventory is exhausted (0 remaining), so this two-line convention is retained as a record of how the migration was tracked rather than as an active reporting requirement.

### SHACL invocation pattern

A standalone SHACL run validating a shape whose `sh:property` blocks use `sh:class` against a controlled-vocabulary value (a `gem:RuleDomain` / `gem:RuleType` / `gem:RestrictionType` / `gem:NextPlannedStep` individual, or any of the named-class individuals minted on the schema side) must pass the ontology file into the **data graph**, not only into the shapes graph. SHACL's `sh:class` constraint inspects the data graph for `rdf:type` triples on the value nodes; the typing triples that declare an individual to be a member of the named class (e.g. `gem:ruleType_eligibility a gem:RuleType`) live in `GEM_ontology.ttl`, not `GEM_policy_instances.ttl`. Loading the ontology only as `shapes_graph` leaves the data graph blind to those typing triples and produces spurious `sh:class` violations for every controlled-vocabulary value.

The required invocation, expressed in Python `rdflib` + `pyshacl`:

```python
from rdflib import Graph
from pyshacl import validate

# Merge EVERY TTL_FILES member into the data_graph; the ontology also serves
# as shacl_graph. The data graph is the whole tracked TTL set, not a fixed
# two-file list -- a shape's sh:class constraint is blind to any typing
# triple in a file left out, and reports its absence as a violation.
data_g = Graph()
data_g.parse("GEM_policy_instances.ttl",    format="turtle")
data_g.parse("GEM_code_group_instances.ttl", format="turtle")
data_g.parse("GEM_ontology.ttl",            format="turtle")

shape_g = Graph()
shape_g.parse("GEM_ontology.ttl",        format="turtle")

conforms, results_g, results_text = validate(
    data_graph=data_g,
    shacl_graph=shape_g,
    inference=None,
    abort_on_first=False,
)
```

**The data graph is the tracked TTL set, not a two-file list (corrected S145).** As written before S145 this block loaded only `GEM_policy_instances.ttl` + `GEM_ontology.ttl` — the TTL set as it stood when the pattern was codified at S78. `GEM_code_group_instances.ttl` was split out as a first-class `TTL_FILES` member at S103–S104 and `gem:refersToCodeGroup` links landed at S104, but this block was not updated, so the documented invocation returned **56 spurious violations** — one per materialized link, each reporting that a `gemi:codeGroup*` value "must be a `gem:CodeGroup` individual" when the typing triple simply sat in the unloaded file. Exactly the failure this section was written to prevent, recurring one file later: the rule generalizes to *every* member of the tracked TTL set, and a hardcoded file list silently narrows it each time the set grows. Adding the third file restores `conforms: True`. When `TTL_FILES` next gains a member, this block gains a line. (`gem_audit.py` was never affected — its `parse_graph` builds from `TTL_FILES` itself, which is why the practice stayed correct while the documentation drifted, and why the drift produced no visible symptom for ~40 sessions. See `SKILL.md` §Common Failure Modes → "a block-extent claim decays with every append" for the general shape.)

The same merging is also what `sh:targetClass` needs to follow `rdfs:subClassOf` for shapes like `gem:CMSpolicyShape` whose targeted instances are typed as subclasses (`gem:ArticlePolicy`, `gem:LCDpolicy`, etc.) -- the subclass-axis triples live in the ontology and must be visible to the SHACL engine through the data graph.

**In-namespace vs code-namespace range enforcement.** The merging trick above works only for classes whose typing triples are in the ontology file. It does NOT work for the externally-populated code-namespace classes (`gem:HCPCSprocedure`, `gem:HCPCSmodifier`, `gem:ICDdiagnosis`, `gem:ICDgrouping`) -- the comment block in `GEM_ontology.ttl` that introduces the HCPCS code set explicitly notes that individual codes are typed by `gem_hcpcs_conversion.rq` against the BioPortal source ontology and are *not* defined in `GEM_ontology.ttl`. Consequently, shapes that constrain code-namespace values use `sh:nodeKind sh:IRI` + `sh:pattern` (IRI-pattern matching against the namespace URL form) rather than `sh:class`. The existing `gem:HCPCSmodifierShape` / `gem:HCPCSprocedureShape` / `gem:HCPCScodeShape` / `gem:ICDdiagnosisShape` / `gem:ICDgroupingShape` definitions all follow this approach; `gem:CMSpolicyShape` and `gem:AnchoredCodingScopeShape` extend it to the property-block level for predicates whose declared range is one of those code-namespace classes (15 `sh:property` slots across the two shapes). Predicates whose range is an in-namespace gem: class (e.g., `gem:ProviderCredential`, `gem:ClinicalConcept`, `gem:PolicyGroup`, `gem:CMSpolicy`, `gem:NextPlannedStep`) continue to use `sh:class` -- the typing triples for those instances live in the same files the audit-time validation graph already loads. Future SHACL coverage Generates should keep this distinction explicit at Plan time: the predicate is one or the other, and the SHACL encoding follows.

This pattern is **not required for `gem_audit.py`**, which constructs a single rdflib graph that already merges both files before running its hand-written queries (so neither `sh:class` nor `sh:targetClass` subclass targeting is at risk). It matters for any future GraphDB validation pipeline, CI hook, or developer-side standalone SHACL run against the ontology.

The pattern was first observed at S73 Cycle 1 when a naïve `validate(data_graph="instances", shacl_graph="ontology")` returned 50 spurious `sh:class` violations against `gem:PolicyRuleShape` (every `gem:ruleType_*` and `gem:ruleDomain_*` value flagged as "not a `gem:RuleType` / `gem:RuleDomain` individual" despite the typing triples existing in the ontology file). Logged as `deferred_proposals[77]`; resolved S78 alongside the SHACL coverage Generate that added `gem:CMSpolicyShape` and `gem:AnchoredCodingScopeShape` (`deferred_proposals[75]`), whose `sh:class` and `sh:targetClass` constraints make the invocation pattern broadly relevant. The in-namespace vs code-namespace distinction was the S78 Borderline #4 issue: the first SHACL Generate attempted `sh:class` uniformly across all object-property ranges, which produced 3,613 spurious violations on code-namespace values; the IRI-pattern strategy documented above replaced that approach before any state was committed.
