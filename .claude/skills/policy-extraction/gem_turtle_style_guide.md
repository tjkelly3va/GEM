---
name: gem-turtle-style-guide
description: "The Turtle/OWL formatting and naming conventions for the GEM (Medicare coverage policy) ontology project. Use whenever creating, formatting, or reviewing GEM Turtle files -- GEM_ontology.ttl (schema) or GEM_policy_instances.ttl (instances). This guide is GEM-specific and DIFFERS from the Sherlock project's turtle-style-guide; where they conflict, this guide governs for GEM files."
---

# GEM Turtle / OWL Style Guide

## Purpose

Consistent formatting, naming, and structural conventions for the **GEM** ontology — the Medicare coverage-policy ontology serialized in Turtle. This guide is the GEM-specific counterpart to the generic `turtle-style-guide` skill (which was written for the Sherlock Holmes project). The two guides share most mechanics but differ in namespaces, source-document modeling, and a few annotation rules. **For any GEM `.ttl` file, this guide governs; where it is silent, fall back to the generic `turtle-style-guide`.**

This guide pairs with `gem_reference.md` (the GEM term list) and `worklist_schema.md` (the worklist structure). It is the formatting authority; `gem_reference.md` is the vocabulary authority.

---

## Key Differences from the Sherlock Turtle Style Guide

These are the points where GEM intentionally departs from the generic guide. Read this section first if you already know the Sherlock conventions.

| Topic | Sherlock guide | GEM guide |
|-------|----------------|-----------|
| Term namespace | `ex:` | `gem:` |
| Individual namespace | `:` (default) | `gemi:` |
| External code namespaces | n/a | `icd10:`, `hcpcs:`, `cpt:`, `rbcs:` |
| Source-document modeling | A `schema:Book` individual per document, referenced by `dc:source` | **No source-document individuals. No `schema:` prefix.** `dc:source` rules below. |
| `dc:source` target | The source-document individual (`:someDoc`) | **Policy individuals → the document URL; all other minted individuals → the policy individual's `gemi:` URI** (see "The dc:source Rule") |
| Annotation property prefix | `ex:prefLabel`, `ex:description`, `ex:memberOfOntology` | `gem:prefLabel`, `gem:description`, `gem:memberOfOntology` |

**Do not declare or use the `schema:` prefix in GEM files.** Source documents are represented by their URL (a plain IRI literal in `dc:source`), not by a `schema:Book` individual. This is the single most important GEM-specific departure and the one most likely to be introduced by habit from the Sherlock guide.

---

## Namespace Conventions

GEM uses a strict three-way separation plus external code vocabularies.

| Prefix | URI | Purpose | Examples |
|--------|-----|---------|----------|
| `gem:` | `http://www.cms.hhs.gov/ontology/2026/07/GEM/` | Ontological terms (classes, properties) | `gem:NCDpolicy`, `gem:refersToClinicalConcept` |
| `gemi:` | `http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/` | All instances and minted individuals | `gemi:ncd240.2`, `gemi:conceptHypoxemia` |
| `rbcs:` | `http://www.cms.hhs.gov/ontology/2026/07/RBCS/` | Restructured B/E Cost-Sharing terms (reserved; used where RBCS concepts appear) | `rbcs:...` |
| `icd10:` | `http://purl.bioontology.org/ontology/ICD10CM/` | External ICD-10-CM code IRIs | `icd10:J96.11` |
| `hcpcs:` | `http://purl.bioontology.org/ontology/HCPCS/` | External HCPCS code/modifier IRIs | `hcpcs:E1390`, `hcpcs:KX` |
| `cpt:` | `https://www.ama-assn.org/cpt#` | External CPT (HCPCS Level I) code IRIs; sourced from `cpt.ttl`, typed `gem:CPTprocedure` by `gem_cpt_conversion.rq` | `cpt:95860` |

Standard external prefixes also declared in every GEM file:

```turtle
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix sh:    <http://www.w3.org/ns/shacl#> .
@prefix dc:    <http://purl.org/dc/elements/1.1/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .
```

### Required namespace header for GEM_policy_instances.ttl

A fresh or emptied instances file MUST begin with exactly this prefix block (after the comment banner). This is the canonical template — copy it verbatim so an emptied file always starts correctly. Note there is **no `schema:` line**.

```turtle
@prefix rdf:   <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
@prefix rdfs:  <http://www.w3.org/2000/01/rdf-schema#> .
@prefix owl:   <http://www.w3.org/2002/07/owl#> .
@prefix skos:  <http://www.w3.org/2004/02/skos/core#> .
@prefix sh:    <http://www.w3.org/ns/shacl#> .
@prefix dc:    <http://purl.org/dc/elements/1.1/> .
@prefix xsd:   <http://www.w3.org/2001/XMLSchema#> .

@prefix hcpcs: <http://purl.bioontology.org/ontology/HCPCS/> .
@prefix icd10: <http://purl.bioontology.org/ontology/ICD10CM/> .

@prefix gem:   <http://www.cms.hhs.gov/ontology/2026/07/GEM/> .
@prefix gemi:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/> .
@prefix rbcs:  <http://www.cms.hhs.gov/ontology/2026/07/RBCS/> .
```

### Code group instances file: GEM_code_group_instances.ttl

`gem:CodeGroup` instances live in their own canonical file, **`GEM_code_group_instances.ttl`** (added S103; CRLF like all `.ttl` files; parsed into the audit/validation graph but excluded from the `GEM_policy_instances.ttl` triple count). Its prefix block is the instances template above plus a `cpt:` line (`@prefix cpt:   <https://www.ama-assn.org/cpt#> .`, since CPT members are possible) and without the `rbcs:` line. A group's predicate order follows the standard ordering: `a gem:CodeGroup`, `gem:prefLabel`, `gem:description`, then `gem:codeGroupOwner`, `gem:identifiesClinicalConcept`, the `skos:narrower` members, `gem:memberOfOntology`, and `dc:source` last; `skos:narrower` targets are listed one per line, alphabetically.

**`dcterms:` prefix (ontology only).** S103 added `@prefix dcterms: <http://purl.org/dc/terms/> .` to `GEM_ontology.ttl` so `gem:codeGroupOwner` can be `rdfs:subPropertyOf dcterms:rightsHolder` (`rightsHolder` is a DC **Terms** term, not DC Elements 1.1). Instance files do not need `dcterms:`; they use `gem:codeGroupOwner` directly.

---

## URI Naming Conventions

### Instances (`gemi:` prefix)

| Entity type | Pattern | Examples |
|-------------|---------|----------|
| NCD policy | `ncd` + section number (dots preserved) | `gemi:ncd240.2`, `gemi:ncd280.1` |
| LCD policy | `lcd` + numeric ID | `gemi:lcd33797` |
| Article policy | `a` or `article` + numeric ID (match existing) | `gemi:a52514` |
| Transmittal | `tn` + number + **mandatory** manual token: `CIM` (Pub. 6) / `NCD` (100-03) / `CP` (100-04) / `OTN` (100-20); must match `gem:publicationNumber` | `gemi:tn11263NCD`, `gemi:tn144CIM`, `gemi:tn961CP`, `gemi:tn1194OTN` |
| NCA | `cag` + id (preserve N/R casing) — equals `gem:identifier` minus `CAG-`; enforced by the audit's `nca_uri_derivation` check | `gemi:cag00296N`, `gemi:cag00296R2` |
| Clinical concept | `concept` + UpperCamelCase label | `gemi:conceptHypoxemia`, `gemi:conceptPO2` |
| Provider credential | `credential` + UpperCamelCase | `gemi:credentialTreatingPractitioner` |
| Qualification group | `group` + Roman numeral | `gemi:groupI`, `gemi:groupII` |
| Healthcare setting | `setting` + UpperCamelCase(prefLabel), punctuation dropped; prefLabel is the bare place phrase — qualifier-first, no parentheses, never the word "setting"; hierarchy is `skos:broader` among individuals (no setting subclasses) | `gemi:settingHome`, `gemi:settingClinic`, `gemi:settingPhysiciansOffice`, `gemi:settingAnywhere` |

**Acronym preservation in concept/credential local names.** When a label contains an all-caps token of length ≥ 2 (an acronym), preserve its casing in the local name; do not lowercase it. `EKG` → `conceptEKG` (not `conceptEkg`); `PO2` → `conceptPO2`; `P pulmonale on EKG` → `conceptPPulmonaleOnEKG`. Lowercase the leading character of the *first* word only when it is not itself an acronym, then capitalize subsequent word initials.

**Dots in policy URIs are intentional and legal.** `gemi:ncd240.2` keeps the section-number dot. Turtle permits internal dots in prefixed local names (only a trailing dot is disallowed). Do not substitute underscores or hyphens for the dot.

### Ontological terms (`gem:` prefix)

| Term type | Convention | Examples |
|-----------|-----------|----------|
| Classes | UpperCamelCase | `gem:CMSpolicy`, `gem:ClinicalConcept`, `gem:QualificationGroup` |
| Object properties | lowerCamelCase | `gem:refersToClinicalConcept`, `gem:coversCondition` |
| Data properties | lowerCamelCase | `gem:policyEffectiveDate`, `gem:manualSectionNumber` |
| Annotation properties | lowerCamelCase | `gem:shortDescription`, `gem:llmDetailedDefinition` |

---

## The dc:source Rule (GEM-specific)

GEM does not mint source-document individuals. `dc:source` is assigned by entity kind:

1. **Policy individuals** (anything typed `gem:CMSpolicy` or a subclass — `gem:NCDpolicy`, `gem:LCDpolicy`, `gem:ArticlePolicy`, `gem:TransmittalPolicy`) take the **document's URL** as a plain IRI:

   ```turtle
   gemi:ncd240.2 a gem:NCDpolicy ;
       ...
       dc:source <https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=169> .
   ```

   This holds for cited-policy **stubs** too: a stub is a policy, so its `dc:source` is *its own* document URL — the URL of the cited document, not the citing policy.

2. **All other minted individuals** (clinical concepts, provider credentials, qualification groups) take the **`gemi:` URI of the policy whose extraction introduced them**:

   ```turtle
   gemi:conceptHypoxemia a gem:ClinicalConcept ;
       ...
       dc:source gemi:ncd240.2 .
   ```

3. **If a policy's URL is not known**, do not invent one and do not omit `dc:source`. Stop and ask the user to provide the URL.

When a clinical concept, credential, or group is *reused* by a later policy (it already exists from an earlier pass), **do not change its `dc:source`** — it keeps the URI of the policy that first introduced it. The later policy's link to it (`gem:refersToClinicalConcept`, etc.) is what records the new appearance.

---

## Required Annotations

| Entity | Required predicates |
|--------|--------------------|
| **New class** | `rdf:type owl:Class`; `rdfs:subClassOf` (unless top-level); `gem:prefLabel`; `gem:description`; `gem:memberOfOntology` |
| **New property** | `rdf:type owl:ObjectProperty`/`owl:DatatypeProperty`/`owl:AnnotationProperty`; `rdfs:subPropertyOf` (if applicable); `gem:prefLabel`; `gem:description`; `rdfs:domain`; `rdfs:range`; `gem:memberOfOntology` |
| **Policy individual** | `rdf:type` (a `gem:CMSpolicy` subclass); `gem:identifier`; `gem:prefLabel`; `gem:description`; metadata data-properties as available; relationship properties; `gem:memberOfOntology`; `dc:source` (URL) |
| **Clinical concept / credential / qualification group** | `rdf:type`; `gem:prefLabel`; `gem:description`; `gem:memberOfOntology`; `dc:source` (policy URI) |
| **Cited-policy stub** | `rdf:type` (best-known `gem:CMSpolicy` subclass, else `gem:CMSpolicy`); `gem:identifier`; `gem:prefLabel`; `gem:description` (states it is a stub); `gem:memberOfOntology`; `dc:source` (URL if known) |

Note GEM uses `gem:prefLabel`/`gem:description`/`gem:memberOfOntology` as **GEM-defined annotation properties** (not `skos:`/`rdfs:` equivalents). Match the existing schema exactly. Ontology terms carry `gem:memberOfOntology gem:gemOntology`; instances carry the same.

There is **no `dc:source` on schema terms** in the convention used by `GEM_ontology.ttl`'s relationship/class definitions (they end at `gem:memberOfOntology`). Match the file you are editing.

---

## Optional Schema-Term Enrichment

These properties are defined in `GEM_ontology.ttl` and may be applied to schema terms (classes and properties) to enrich them with reading-aid metadata. None are required on any term; add them only where the enrichment provides real value.

### Brief description: `gem:shortDescription`

A subproperty of `gem:description` that holds a single concise sentence summarizing what the term represents — useful where a brief gloss is wanted in addition to the full description. When both are present on the same term, place `gem:shortDescription` immediately **before** `gem:description` (see `gem:identifier`).

### Primary-class flag: `gem:isaPrimaryClass`

A datatype property with domain `owl:Class` and range `xsd:boolean`. When asserted with value `true` on a class, it marks that class as one of the ontology's most important or frequently used classes (current: `gem:Beneficiary`, `gem:CMSpolicy`, `gem:HCPCSprocedure`, `gem:ICDdiagnosis`, `gem:MedicareClaim`). Apply only to classes — never to instances or to non-class terms. A class that is not primary simply omits the property; do not assert `false`.

### LLM-scaffolding annotations (`gem:llm*`)

Six annotation properties giving an LLM consumer the context it needs to reason about a schema term. All have domain `owl:Thing`, range `xsd:string`, and are optional. Pick the one that matches the kind of guidance being captured; do not invent string-typed annotations outside this set without first adding the new annotation property to the ontology.

| Annotation | When to use |
|-----------|------------|
| `gem:llmDetailedDefinition` | Extended explanation of the term's meaning, modeling rationale, and disambiguation — longer and more explanatory than `gem:description`. |
| `gem:llmCardinalityNote` | Expected count or multiplicity constraints on this property's usage on instances. |
| `gem:llmEnumeratedValues` | Closed list of valid string values for a datatype property, with a short definition of each value. |
| `gem:llmInverseNote` | Whether inverse or symmetric relationships are explicitly materialized or must be inferred, and what this means for query strategy. |
| `gem:llmScopingNote` | Boundary conditions, applicability constraints, or contextual limitations on when this schema element applies. |
| `gem:llmTraversalHint` | Procedural guidance for navigating a chain or graph structure formed by this property — start points, direction, terminal conditions. |

In current usage these annotations target **schema terms** (e.g., `gem:description`, `gem:prefLabel`, `gem:memberOfOntology` carry them) and, as of S140 (extended S156), all five **controlled-vocabulary (enumerated-value) families** in the `gem:` namespace: every `gem:RuleType`, `gem:RuleDomain`, `gem:RestrictionType`, `gem:NextPlannedStep`, and `gem:SourceAvailability` individual (e.g. `gem:ruleType_coverageScope`) carries `gem:llmDetailedDefinition`, whose value is verbatim from the individual's governing enumeration `gem:llmEnumeratedValues` per-value definition (drift-proof by construction — `ruleType`/`ruleDomain`/`restrictionType` from the respective property annotation, `nextPlannedStep` and `sourceAvailability` from the `gem:NextPlannedStep` / `gem:SourceAvailability` class annotation, those two classes carrying the detailed per-value form). These 33 individual-level definitions are also mirrored for LLM/developer consumers in the tracked canonical file **`gem_llm_annotations.json`** (14th canonical file, hash-tracked; `GEM_ontology.ttl` remains authoritative). `gem_audit.py`'s `llm_annotation_drift` check keeps the mirror in sync and its autofix regenerates it from the graph. An *existing* family gaining a new individual flows into the mirror automatically once that individual carries `gem:llmDetailedDefinition`; a new **family** does **not** — `gem_audit.py`'s `LLM_ANNOTATED_VOCAB_CLASSES` is a hand-maintained roster and must be edited when one is added (S156 finding; the S140 wording here implied otherwise and was corrected at S160). These enrichments are still **not** applied to `gemi:` instance-data individuals (policies, rules, code groups, clinical concepts); if a future use case justifies that, document it here.

---

## Predicate Ordering

Within any individual or term definition, order predicates:

1. `rdf:type` (`a`)
2. `rdfs:subClassOf` / `rdfs:subPropertyOf` (if applicable); `skos:broader` on vocabulary individuals (hierarchy slot — e.g. healthcare settings, work item [95])
3. **Identifier / naming** — `gem:identifier`, `gem:prefLabel`, `skos:altLabel`
4. **Descriptive annotations** — `gem:shortDescription` (if present), `gem:description`, `gem:workflowDescription` (if present), then any `gem:llm*` enrichment annotations (alphabetical: `gem:llmCardinalityNote`, `gem:llmDetailedDefinition`, `gem:llmEnumeratedValues`, `gem:llmInverseNote`, `gem:llmScopingNote`, `gem:llmTraversalHint`)
5. **Structural metadata** — `rdfs:domain`, `rdfs:range` (on property definitions); `gem:isaPrimaryClass` (on class definitions, only when `true`)
6. **Domain data-properties** (on instances) — `gem:publicationNumber`, `gem:manualSectionNumber`, `gem:priorManualSectionNumber` (repeatable; sort its values as a group, immediately after `gem:manualSectionNumber` — S152), `gem:policyVersion`, `gem:policyEffectiveDate`, `gem:policyImplementationDate`, …
7. **Relationship (object) properties** — grouped by predicate, each predicate's targets sorted; recommended group order: `gem:requiresProviderCredential`, `gem:referencesPolicy`, `gem:refersToQualificationGroup`, `gem:refersToClinicalConcept`, code links (`gem:coversCondition`, `gem:excludesCondition`, `gem:coversProcedure`, `gem:excludesProcedure`, `gem:refersToHCPCSmodifier`). On `gem:PolicyRule` subjects the object properties are `gem:ruleDomain`, `gem:ruleType`, then `gem:delegatesCoverageTo` (S167; contractor-discretion delegatee, range `gem:ProviderCredential`) — in that order, immediately before `gem:memberOfOntology`. The setting-polarity family (S197, first asserted S198) follows `gem:delegatesCoverageTo`: `gem:coversInHealthcareSetting`, `gem:exclusivelyCoversInHealthcareSetting`, `gem:excludesHealthcareSetting` — in that order where a rule carries more than one, each predicate's targets sorted alphabetically by local name. NCD 160.7.1's R9 / R14 / R15 are the first-use example.
8. `gem:memberOfOntology` — **always second-to-last**
9. `dc:source` — **always last**

Within a repeated object property (e.g., 40 `gem:refersToClinicalConcept` lines), sort targets for stable diffs. The order is **two-tier**, and the tier depends on the predicate:

1. **Numbered children — numeric order.** `gem:hasPolicyRule`, `gem:hasPolicyGroup`, `gem:hasPolicyCodingRule` and `gem:hasAnchoredCodingScope` point at a policy's own `_r<N>` / `_group<N>` individuals, and those sort by the **number**: `_r1, _r2, … _r9, _r10, _r11`. Sorting them as text gives `_r1, _r10, _r11, _r2`, which no block in the corpus has ever used.
2. **Everything else — lexicographic by local name.** Concepts, policies, credentials, benefit categories, settings, change requests, and code targets (`icd10:`, `hcpcs:`, `cpt:`). Codes sort as **text**, so `icd10:J96.11` precedes `icd10:J96.9`; do not "fix" that to numeric order.

**Read the two tiers as a pair — each one is what stops the other being over-applied.** Through S260 this paragraph stated tier 2's rule alone, without exception, and that wording was wrong: measured across the corpus at S261, `gem:hasPolicyRule` is **131/131** numerically sorted and **0/51** lexicographically sorted among blocks carrying ten or more rules. A sweep written from the sentence as it stood would have reordered every large policy's rule links into `_r1, _r10, _r11, _r2` and reported success. Tier 2 is stated just as explicitly for the mirror-image reason: `gem:exclusivelyCoversCondition` is **21/23** lexicographic, so applying tier 1 globally would have mis-sorted the ICD lists instead.

Enforced by `gem_audit.py`'s `predicate_target_sort` check (YELLOW, autofixable), whose self-test variants **V110** and **V111** pin the two tiers against each other — collapsing the check to either tier alone turns the suite red. (Two-tier rule confirmed by Tom, S261.)

**`gem:workflowDescription` sits immediately after `gem:description` (S151).** The two are adjacent on purpose — a reader scanning a block sees the consumer-facing account and the extraction's notepad next to each other, and the split is self-evident. `gem:description` carries what the entity is; `gem:workflowDescription` carries how the record got here (session provenance, token derivation, source-resolution method or pending state, borderline decisions, methodology cross-references). Single-valued, like `gem:description`. Defined in `GEM_ontology.ttl` at S151; see `SKILL.md` §Policy Description Style for the content split, and `gem_reference.md` §1a for the term listing. The audit's `predicate_ordering` check enforces only that `gem:memberOfOntology` is second-to-last and `dc:source` last, so this position is a style-guide convention rather than a checked one — keep it by hand. **Backfilled at S173:** individuals minted before S151 that carried workflow prose inside `gem:description` were cleaned in the S173 leak-cleanup (~220 subjects moved to `gem:workflowDescription`; `deferred_proposals[100]` complete). Leftover workflow/verbatim material in `gem:description` is now a finding — the `description_workflow_leak` guard flags it YELLOW (group-(b) OWL schema terms, SHACL NodeShapes, and the five controlled-vocab families excluded), and also flags a `gem:workflowDescription` with no `gem:description` (RED) or a `gem:description` byte-identical to its `gem:workflowDescription` (RED). The guard checks leak *content*, not predicate *position*; the immediately-after ordering above remains a hand-kept convention.

---

## Polarity Predicates (GEM-specific vocabulary)

Coverage polarity uses sub-properties of polarity-neutral parents (see `gem_reference.md` for full definitions):

- **ICD-10:** `gem:coversCondition` / `gem:excludesCondition` — sub-properties of `gem:refersToICDdiagnosis`.
- **HCPCS:** `gem:coversProcedure` / `gem:excludesProcedure` / `gem:requiresProcedure` — sub-properties of `gem:refersToHCPCSprocedure`.
- **Modifiers:** `gem:refersToHCPCSmodifier` — single, no polarity pair.
- **Healthcare settings (S197):** `gem:coversInHealthcareSetting` / `gem:exclusivelyCoversInHealthcareSetting` / `gem:excludesHealthcareSetting` — sub-properties of `gem:refersToHealthcareSetting`, normally asserted on a `gem:PolicyRule` subject. **The parent is an exception to the rule above:** it stays directly asserted on the policy as a presence link, because a rule-subject child entails nothing about the policy. Settings take polarity because a claim carries a place of service; `gem:excludedHealthcareSetting` is a different predicate belonging to the deferred coverage-qualifier layer and is not used.

Polarity assignment is binary (see the policy-extraction SKILL.md Polarity section): a code stated as denied/non-covered → `excludes…`; a code that is covered or silent (including an explicit disclaimer of polarity, or no statement) → `covers…`. The neutral parents (`gem:refersToICDdiagnosis`, `gem:refersToHCPCSprocedure`) are **not asserted directly** by new extraction — they are reached only by entailment. A polarity-bearing link entails the neutral parent, so never assert both for the same code. (Binary rule established Session 19, superseding the prior three-tier scheme; legacy L33797 neutral triples await backfill.)

---

## Formatting Rules

| Element | Convention |
|---------|-----------|
| Line endings | **CRLF only.** A lone LF is a defect even though it parses. |
| Indentation | **4 spaces.** Never tabs (zero tab characters in the file). |
| Continuation lines | 4-space indent under the subject |
| Statement termination | Every definition ends with `.` (never a dangling `;`) |
| File termination | File ends with `.\r\n` |
| String escaping | Escape `"` as `\"` and `\` as `\\` inside literals; collapse newlines inside a literal to spaces |
| Typed literals | Dates as `"YYYY-MM-DD"^^xsd:date` |
| Section headers | `#` comment banners delimiting POLICY INSTANCE / PROVIDER CREDENTIAL INDIVIDUALS / QUALIFICATION GROUP INDIVIDUALS / CLINICAL CONCEPT INDIVIDUALS / REFERENCED-POLICY STUBS |
| Code IRIs | Preserve dots in ICD-10 (`icd10:J96.11`); codes are facts and freely linkable; never copy AMA description text into the TTL |

---

## File Structure (instances file, per policy block)

Each processed policy appends a block in this order:

1. Section banner naming the policy, version, effective date, extraction date.
2. **POLICY INSTANCE** — the `gem:CMSpolicy`-subclass individual with all its links.
3. **PROVIDER CREDENTIAL INDIVIDUALS** — any newly minted credentials.
4. **QUALIFICATION GROUP INDIVIDUALS** — any newly minted groups.
5. **CLINICAL CONCEPT INDIVIDUALS** — newly minted concepts, alphabetical by local name.
6. **REFERENCED-POLICY STUBS** — stubs for cited policies not yet processed.

Reused individuals (already present from an earlier policy) are **not** re-emitted; only the new link from the current policy is added to that policy's instance block. The "Policies processed:" line in the file's comment banner is updated each pass.

---

## Verification Checklist (GEM)

After any GEM `.ttl` creation or modification:

- [ ] File parses as Turtle (rdflib).
- [ ] No `schema:` prefix and no `schema:Book` individuals.
- [ ] `dc:source` convention: policy individuals → URL; all other minted individuals → policy `gemi:` URI.
- [ ] Every reference / concept / credential / group target resolves to a typed individual.
- [ ] `gem:memberOfOntology` second-to-last, `dc:source` last, in every definition.
- [ ] CRLF line endings only; zero lone-LF; zero tab characters.
- [ ] File ends with `.\r\n`.
- [ ] Concept/credential/group local names use acronym-preserving CamelCase.
- [ ] Policy URIs preserve section-number dots.
- [ ] `GEM_ontology.ttl` triple count unchanged unless new schema terms were approved this pass.
- [ ] No duplicate `gemi:` local names within the file.
- [ ] Neutral parents (`refersToICDdiagnosis` / `refersToHCPCSprocedure`) are not asserted directly in new extraction; every code carries a `covers…` / `excludes…` predicate (binary polarity rule).
- [ ] If new annotation properties were defined, they match the existing `gem:llm*` shape (domain `owl:Thing`, range `xsd:string`, `prefLabel`/`description`/`memberOfOntology`). New string-typed annotations outside the established set need explicit user approval before being added to the ontology.
