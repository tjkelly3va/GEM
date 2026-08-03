# gem_reference.md — GEM Terms and Conventions for Policy Extraction

This file lists the GEM terms to **reuse**, the project terms now **established** in `GEM_ontology.ttl`, the GEM **conventions** all new terms must follow, and the governance for **proposing further terms**. It is a working reference, updated as the user approves new terms.

The GEM schema namespace is `gem: <http://www.cms.hhs.gov/ontology/2026/07/GEM/>`. Policy instances and the individuals this skill mints (policies, credentials, clinical concepts, cited-policy stubs) use the **instance namespace** `gemi: <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/>`, kept distinct from the schema namespace. External code namespaces declared in the GEM `.ttl` files:
- `icd10: <http://purl.bioontology.org/ontology/ICD10CM/>`
- `hcpcs: <http://purl.bioontology.org/ontology/HCPCS/>`
- `cpt: <https://www.ama-assn.org/cpt#>` — CPT (HCPCS Level I) code IRIs; sourced from `cpt.ttl`, typed `gem:CPTprocedure` by `gem_cpt_conversion.rq`; declared in `GEM_policy_instances.ttl` (S88)

`GEM_ontology.ttl` also declares `rbcs: <http://www.cms.hhs.gov/ontology/2026/07/RBCS/>`, a sibling component of the GEM ontology unrelated to policy extraction; the policy-extraction skill does not write `rbcs:` terms. Always read the prefix block of the live `GEM_ontology.ttl` / `GEM_policy_instances.ttl` at the start of a session — the namespace date path is set by those files, and the skill mints with the `gem:` / `gemi:` prefixes so it inherits whatever the files declare.

---

## 1. Pre-Existing GEM Terms to Reuse

Reuse these exactly as defined in `GEM_ontology.ttl`. Do not redefine them. These predate the policy-extraction work.

| Term | Kind | Use in this skill |
|------|------|-------------------|
| `gem:CMSpolicy` | class | Base class for every policy instance. Each instance is typed to one of the three subclasses in §2. |
| `gem:refersToICDdiagnosis` | object property | Policy → `gem:ICDdiagnosis` link. Domain `gem:CMSpolicy`, range `gem:ICDdiagnosis`. **Polarity-neutral parent** of the polarity-bearing pair `gem:coversCondition` / `gem:excludesCondition` (§2c). |
| `gem:ICDdiagnosis` | class | The class of real ICD-10-CM diagnosis codes. ICD-10 IRIs the skill links to are members of this class. |
| `gem:ICDdiagnosisShape` | SHACL shape | IRI pattern an ICD-10 diagnosis IRI must satisfy: `icd10:` namespace, local name `<letter><digit><alphanumeric>(.<1–4 alphanumerics>)?`. **Preserve the dot** (e.g., `icd10:J96.11`). |
| `gem:prefLabel` | annotation | **Required** human-readable label on every term and individual. |
| `gem:description` | annotation | **Required** on every term and individual. Defines scope/meaning for a class or property; describes the entity for an instance. **Written for data consumers** — what the entity *is*, not how the record was built (S151). Extraction-process prose belongs in `gem:workflowDescription` (§1a). |
| `gem:memberOfOntology` | annotation | **Required** on every term and individual; always `gem:gemOntology`. Second-to-last predicate. |
| `gem:identifier` | datatype property | Authority-issued unique identifier string. Used for a policy's identifier (e.g. `"NCD 240.2"`, `"L33797"`, `"A52514"`). |

**ICD-10 linking:** the skill links a policy to an existing external code IRI; it does not mint diagnosis individuals. Example object: `icd10:J96.11`. The code's dot is part of the local name and must be kept.

### 1a. Optional enrichment annotations

These are also pre-existing in `GEM_ontology.ttl` and are **never required**. Add them only when the enrichment provides real value. See §4 below and `gem_turtle_style_guide.md` ("Optional Schema-Term Enrichment") for the per-annotation usage rules and the predicate-ordering placement.

| Term | Kind | Use |
|------|------|-----|
| `gem:shortDescription` | annotation | Brief one-sentence gloss; subproperty of `gem:description`. When both are present on a term, place `gem:shortDescription` **before** `gem:description`. |
| `gem:workflowDescription` | annotation | **The extraction process's own notepad (S151).** How the record got here, not what it is: session provenance, URI/manual-token derivation and its priority level, source-resolution method or pending state, borderline decisions and the alternative considered, cross-references to `SKILL.md` / `gem_rule_categories.md` / `deferred_proposals`. No domain or range; single-valued; ordered **immediately after** `gem:description`. Carries no coverage-domain content — claim-facing queries can ignore it. **Forward-compliant only:** defined at S151, so individuals minted earlier still carried workflow prose inside `gem:description`; the S173 leak-cleanup moved that prose into `gem:workflowDescription` for ~220 subjects (`deferred_proposals[100]` complete). The `description_workflow_leak` audit guard is now live (S173): it flags a subject with `gem:workflowDescription` but no `gem:description` (RED, structural), a `gem:description` byte-identical to its `gem:workflowDescription` (RED), and a workflow/verbatim leak marker left in `gem:description` (YELLOW) — the last with group-(b) excluded (OWL schema terms, SHACL NodeShapes, and the five controlled-vocab families carry provenance in their glosses by convention). Scope call (S151): schema-term change history stays in `gem:description`. See `SKILL.md` §Policy Description Style. |
| `gem:llmDetailedDefinition` | annotation | Extended explanation written for LLM consumption — longer and more explanatory than `gem:description`. |
| `gem:llmCardinalityNote` | annotation | Expected count or multiplicity constraints on this property's usage on instances. |
| `gem:llmEnumeratedValues` | annotation | Closed list of valid string values for a datatype property, with a short definition of each. |
| `gem:llmInverseNote` | annotation | Whether inverse/symmetric relationships are materialized or must be inferred, and what this means for queries. |
| `gem:llmScopingNote` | annotation | Boundary conditions, applicability constraints, or contextual limitations on when this schema element applies. |
| `gem:llmTraversalHint` | annotation | Procedural guidance for navigating a chain or graph structure formed by this property. |
| `gem:isaPrimaryClass` | datatype property | Marker — domain `owl:Class`, range `xsd:boolean`. Asserted `true` only on classes designated as primary/heavily-used (current: `gem:Beneficiary`, `gem:CMSpolicy`, `gem:HCPCSprocedure`, `gem:ICDdiagnosis`, `gem:MedicareClaim`). Apply only to classes; omit on non-primary classes (do not assert `false`). |

---

## 2. Established Project Terms

The terms below were proposed during the first policies, approved by the user, and now exist in `GEM_ontology.ttl`. **Treat them exactly like pre-existing GEM terms — reuse them; do not re-propose them.** A policy that uses only these terms adds zero schema terms.

### 2a. Policy document-type subclasses

Subclasses of `gem:CMSpolicy`:

| URI | Parent | prefLabel | Scope |
|-----|--------|-----------|-------|
| `gem:NCDpolicy` | `gem:CMSpolicy` | "NCD Policy" | National Coverage Determinations. |
| `gem:LCDpolicy` | `gem:CMSpolicy` | "LCD Policy" | Local Coverage Determinations. |
| `gem:ArticlePolicy` | `gem:CMSpolicy` | "Article Policy" | MCD Articles (esp. Billing & Coding Articles). |
| `gem:TransmittalPolicy` | `gem:CMSpolicy` | "Transmittal Policy" | A CMS Manual transmittal that revises one or more coverage policies (NCDs, LCDs, or Articles). Minted as a `gem:TransmittalPolicy` stub at first citation regardless of manual chapter (Pub. 100-02, Pub. 100-04, etc.) per the Session 45 ratchet-forward methodology. Newly-minted stubs carry `gem:nextPlannedStep = gem:planPromote`; the decision to advance to full extraction is made at each transmittal's own Plan turn. |
| `gem:ProgramMemorandumPolicy` | `gem:CMSpolicy` | "Program Memorandum Policy" | Pre-MAC-era Program Memoranda (PM B-XX-NN, PM A-XX-NN, PM AB-XX-NN), the predecessor publication of transmittals. Sibling class of `gem:TransmittalPolicy`; same handling. Introduced 2026-06-08 (Session 45). |
| `gem:NCAdocument` | `gem:CMSpolicy` | "NCA Document" | National Coverage Analyses — the deliberative records (Tracking Sheets, Proposed/Final Decision Memos, Public Comments) that precede NCD action. Stub-only by default at first citation; promotion to full extraction is per-policy at user direction. NCAs default to `gem:nextPlannedStep = gem:planPromote` regardless of `gem:isInEffect`, indicating future extraction is in scope. |
| `gem:ChangeRequest` | `gem:CMSpolicy` | "Change Request" | A numbered CMS Change Request (CR) — the instruction work-item mandating a coverage/operational/system update. Paired with a Transmittal (its delivery vehicle). Minted as a `gem:ChangeRequest` stub when an extracted transmittal delivers (`gem:transmitsChangeRequest`) or cites (`gem:referencesChangeRequest`) it; `gem:nextPlannedStep = gem:planPromote`. A transmitted CR's `dc:source` is its delivering transmittal's IRI. Introduced 2026-06-26 (Session 95). |

`NCDpolicy`, `LCDpolicy`, `ArticlePolicy` are the document types every policy is *read* as. `TransmittalPolicy` and `ProgramMemorandumPolicy` are sibling stub-default subclasses for the change-instruction publication categories. `NCAdocument` is the stub-default subclass for NCAs. All five carry `gem:nextPlannedStep` and `gem:isInEffect` (see §2k).

The principle behind treating transmittals and PMs as first-class policy documents: codes and concepts attach to the document that actually contains the guidance, so a downstream evaluator can read the operative instruction even when it currently lives only in a transmittal/PM and has not yet been folded into the manual section it revises. Whether a transmittal's change has already landed in its affected policy is a finding worth recording but does NOT gate its typing — observation is the project's response, not escalation.

### 2b. Policy-to-policy reference property

| URI | Kind | Domain | Range | prefLabel |
|-----|------|--------|-------|-----------|
| `gem:referencesPolicy` | object property | `gem:CMSpolicy` | `gem:CMSpolicy` | "References Policy" |
| `gem:transmitsChangeRequest` | object property | `gem:CMSpolicy` | `gem:ChangeRequest` | "Transmits Change Request" |
| `gem:changeRequestTransmittedBy` | object property | `gem:ChangeRequest` | `gem:CMSpolicy` | "Change Request Transmitted By" |
| `gem:referencesChangeRequest` | object property | `gem:CMSpolicy` | `gem:ChangeRequest` | "References Change Request" |

Links a policy to another policy it cites. Created even when the cited policy is not yet processed — the object is a stub, populated later. Complements, does not replace, the worklist entry.

`gem:transmitsChangeRequest` (delivery; transmittal → CR) and `gem:referencesChangeRequest` (mention; policy → CR) are sub-properties of `gem:referencesPolicy` for Change Requests (range `gem:ChangeRequest`). `gem:transmitsChangeRequest` has inverse `gem:changeRequestTransmittedBy` (asserted forward-only, like `revisedByPolicy`). A transmitted CR's `dc:source` is the delivering transmittal's IRI; if that transmittal is not yet a node, mint it as a `gem:TransmittalPolicy` stub first.

### 2c. Covered / non-covered code reference properties

Coverage polarity is modeled with **separate predicates**, organized as polarity-bearing sub-properties of a polarity-neutral parent — so a query on the neutral parent still returns references of either polarity.

**ICD-10 diagnoses:**

| URI | Super-property | Domain | Range | Meaning |
|-----|----------------|--------|-------|---------|
| `gem:refersToICDdiagnosis` | — (pre-existing; the neutral parent) | `gem:CMSpolicy` | `gem:ICDdiagnosis` | Polarity-neutral parent. **Not asserted directly by new extraction** (binary polarity rule, Session 19); retained in the schema only as the parent reached by entailment from a polarity-bearing sub-property. |
| `gem:coversCondition` | `gem:refersToICDdiagnosis` | `gem:CMSpolicy` | `gem:ICDdiagnosis` | References this diagnosis as **supporting** coverage / medical necessity. The **default** whenever a code is not denied — explicit coverage, an explicit disclaimer of polarity, or no stated polarity all map here. The sub-property `gem:exclusivelyCoversCondition` (§2j) further narrows by claiming closure: the union of its objects is the complete coverage scope. |
| `gem:exclusivelyCoversCondition` | `gem:coversCondition` | `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` | `gem:ICDdiagnosis` | A sub-property of `gem:coversCondition` carrying the additional closed-list claim: the union of objects for a given subject (a policy or an anchored coding scope) is the COMPLETE set of conditions covered by that subject; any ICD-10 code not in the union is implicitly excluded. Used at policy level for non-anchored policies whose source makes the closure explicit (proposal #34's Type-1 pattern). Used at the anchor-scope level for anchored-scope-structured policies. See §2j. |
| `gem:excludesCondition` | `gem:refersToICDdiagnosis` | `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` | `gem:ICDdiagnosis` | References this diagnosis as **not supporting** medical necessity / denied / excluded. Used at policy level for policy-wide exclusions, and at the anchor-scope level for per-anchor diagnostic exclusions (the A52519 Group 1A pattern; the domain extension to `gem:AnchoredCodingScope` was added in S60). See §2j. |

**HCPCS procedures / items:**

| URI | Super-property | Domain | Range | Meaning |
|-----|----------------|--------|-------|---------|
| `gem:refersToHCPCSprocedure` | — (the neutral parent) | `gem:CMSpolicy` | `gem:HCPCSprocedure` | Polarity-neutral parent. **Not asserted directly by new extraction** (binary polarity rule, Session 19); retained in the schema only as the parent reached by entailment from a polarity-bearing sub-property. |
| `gem:coversProcedure` | `gem:refersToHCPCSprocedure` | `gem:CMSpolicy` | `gem:HCPCSprocedure` | References this procedure/item as covered. The **default** whenever a code is not denied — explicit coverage, an explicit disclaimer of polarity, or no stated polarity all map here. The sub-property `gem:exclusivelyCoversProcedure` (§2j) further narrows by claiming closure: the union of its objects is the complete coverage scope. |
| `gem:exclusivelyCoversProcedure` | `gem:coversProcedure` | `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` | `gem:HCPCSprocedure` | A sub-property of `gem:coversProcedure` carrying the additional closed-list claim: the union of objects for a given subject (a policy or an anchored coding scope) is the COMPLETE set of procedures covered by that subject; any HCPCS code not in the union is implicitly excluded. The dual-domain declaration leaves room for a future pattern in which an anchor-scope's anchor is an ICD list and its closed-list scope is over HCPCS — the inverse of the present Article pattern; no current instances of the inverted pattern are extracted. The common usage is policy-level. See §2j. |
| `gem:excludesProcedure` | `gem:refersToHCPCSprocedure` | `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` | `gem:HCPCSprocedure` | References this procedure/item as non-covered / denied / excluded. Used at policy level for policy-wide exclusions, and at the anchor-scope level for per-anchor procedure exclusions (e.g., the A52519 `a7047CodingRule` pattern excluding E0485 and E0486 when A7047 is used; the domain extension to `gem:AnchoredCodingScope` was added in S60). See §2j. |
| `gem:requiresProcedure` | `gem:refersToHCPCSprocedure` | `gem:CMSpolicy` | `gem:HCPCSprocedure` | References this procedure/item as **required** for coverage / medical necessity (e.g., a test that must be performed before another service is covered). A third polarity-bearing sub-property of `gem:refersToHCPCSprocedure`, distinct from "covered" because the procedure is itself a precondition, not the covered service. Defined in the ontology; not yet used by any extracted policy. |

**Polarity-assignment rule — binary (two tiers)** (also stated in `SKILL.md` under Polarity rule 4):

1. **Tier 1 — denial stated** ("not covered" / "does not support medical necessity" / "denied" / "excluded" / equivalent for this code in heading, prose, or table title): use the `excludes…` predicate (`gem:excludesCondition` / `gem:excludesProcedure`).
2. **Tier 2 — covered or silent (the default)** — anything that is not a denial: explicit coverage, an explicit disclaimer of polarity ("the appearance of a code in this section does not necessarily indicate coverage"), or no stated polarity: use the `covers…` predicate (`gem:coversCondition` / `gem:coversProcedure`). Neutral is not modeled separately; the manifest marks a silence-based assignment as Tier 2 (covered/silent) so the user sees the inferred polarity.

The polarity-neutral parents (`gem:refersToICDdiagnosis`, `gem:refersToHCPCSprocedure`) are **never asserted directly** by new extraction under this rule (established Session 19, superseding the prior three-tier scheme that routed explicit disclaimers to the neutral parent). They remain in the schema as parents reached by entailment. Legacy L33797 triples under the old scheme are the only remaining direct uses and await a backfill pass.

The closed-list sub-properties `gem:exclusivelyCoversCondition` / `gem:exclusivelyCoversProcedure` (§2j) are refinements of Tier 2 covers — same polarity, with the additional claim that the listed set is exhaustive for the subject (a policy or a Group). Use them when the policy makes the closure explicit (e.g., a 'DO NOT Support Medical Necessity' section that lists no specific codes but declares the complement excluded, or a Group Paragraph that anchors a finite ICD list to a finite HCPCS list). Otherwise use plain `gem:coversCondition` / `gem:coversProcedure`.

A polarity-bearing link entails the neutral parent triple (sub-property semantics), so the neutral predicate is never asserted alongside a polarity-bearing one. A single code may legitimately carry **two distinct polarity-bearing predicates** when a policy uses it in two different ways (e.g., a code described as "required" in one context and "non-covered" in another), but should never carry the bare neutral predicate.

### 2d. Modifier reference property

| URI | Domain | Range | prefLabel |
|-----|--------|-------|-----------|
| `gem:refersToHCPCSmodifier` | `gem:CMSpolicy` | `gem:HCPCSmodifier` | "Refers to HCPCS Modifier" |

Modifiers are billing instructions, not covered/non-covered items, so a single polarity-neutral predicate is used — there is no covered/non-covered pair for modifiers.

### 2e. Provider credential class and vocabulary

| URI | Kind | prefLabel |
|-----|------|-----------|
| `gem:ProviderCredential` | class | "Provider Credential" |
| `gem:requiresProviderCredential` | object property, `gem:CMSpolicy` → `gem:ProviderCredential` | "Requires Provider Credential" |
| `gem:delegatesCoverageTo` | object property, `gem:PolicyRule` → `gem:ProviderCredential` | "Delegates Coverage To" |

`gem:delegatesCoverageTo` (S167, `deferred_proposals[90]`) marks **contractor (MAC) discretion** at the rule level: the rule delegates its coverage determination to a Medicare contractor authority rather than stating a national covered/non-covered disposition. Its *presence* on a rule is the discretion marker; its object is the delegatee, reusing an existing `gem:ProviderCredential` — `gemi:credentialMedicareAdministrativeContractor` (delegation to the MAC as a whole) or `gemi:credentialMedicalStaff` (delegation to the MAC medical staff). It records **to whom** the determination is delegated and is deliberately orthogonal to the deferred `gem:CoverageDecision` disposition value `gem:mac_discretion` (`deferred_proposals[72]` Phase 2), which records **what** the disposition is — the two coexist without duplication. It does not assert that the delegatee furnishes the service. As of the S168 `deferred_proposals[90]` complete-sweep, 20 rules across 12 policies carry it — the S167 set (NCD 200.2, 180.2, 240.2.2, 260.1, 280.7, 280.14) plus the seven swept in at S168 (NCD 20.29, 240.2, 270.1, 280.16, 280.1, 50.1, all → `gemi:credentialMedicareAdministrativeContractor`); the graph is the source of truth for which rules do.

A **controlled vocabulary** of credential individuals (in the `gemi:` namespace), grown as policies introduce new concepts. The individual roster is **not enumerated here — the graph is the single source of truth** (as it is for clinical concepts §2f, qualification groups §2h, and benefit categories §2i). Query `GEM_policy_instances.ttl` for subjects typed `a gem:ProviderCredential`; each carries a `gem:prefLabel` (the source phrasing, verbatim), a `gem:description` (license basis / governing text / minting session), and a `dc:source` naming the introducing policy. As of S130 the graph holds **74** credential individuals. Distinct source phrasings are **catalogued as separate individuals, never consolidated by the extractor** — synonymy is an SME assertion (e.g. `gemi:credentialAuthorizedPractitioner` and `gemi:credentialOtherQualifiedPractitioner` are catalogued separately because the §210.2 source text does not alias the two phrasings).

`gemi:credentialTreatingPractitioner` and `gemi:credentialTreatingClinician` are deliberately **kept distinct**, not consolidated. In the Medicare Claims Processing Manual, "treating practitioner" is a term of art for **non-physician** providers (nurse practitioners, clinical nurse specialists, physician assistants). "Treating clinician" is the broader CMS term for **anyone qualified in clinical practice** — M.D., D.O., nurse practitioner, or other allied health professional. The clinician concept is a superset of the practitioner concept; merging them would wrongly assert that a policy requiring a "treating clinician" requires a non-physician. Term identity is by meaning, not by surface similarity.

Capture only credentials the policy **affirmatively requires** of a service or test performer. A "DME supplier" is *not* modeled as a credential — across the oxygen policies it appears only in disqualifying or restrictive contexts (a supplier may not perform qualifying tests, etc.), never as a credential the policy requires. The DME-supplier disqualification is logged as a deferred proposal, not modeled.

### 2f. Clinical concept class and reference property

| URI | Kind | prefLabel |
|-----|------|-----------|
| `gem:ClinicalConcept` | class, `rdfs:subClassOf skos:Concept` | "Clinical Concept" |
| `gem:refersToClinicalConcept` | object property, `gem:CMSpolicy` → `gem:ClinicalConcept` | "Refers to Clinical Concept" |

A flat controlled vocabulary of clinical, physiological, diagnostic, therapeutic, and equipment concepts relevant to the policy's domain (for home oxygen: conditions, findings, measurements, tests, therapies, equipment). Concept individuals are in the `gemi:` namespace. **One individual per concept, reused across policies; one `gem:refersToClinicalConcept` link per policy in which the concept appears.** The link records presence only — it does not assert polarity or evaluate how the concept is mentioned. Concept-to-concept hierarchy (`skos:broader`/`skos:narrower`) and synonym consolidation are deliberately deferred to a later human-reviewed taxonomy pass; `gem:ClinicalConcept` is a single flat class. See the "Clinical Concepts" section of `SKILL.md` for scope (Option B) and modeling rules.

### 2g. Policy-metadata datatype properties

Domain `gem:CMSpolicy` on all seven.

| URI | Range | Holds |
|-----|-------|-------|
| `gem:publicationNumber` | `xsd:string` | CMS Manual publication number (e.g. "100-3"). NCD field; LCDs/Articles leave it unset. |
| `gem:manualSectionNumber` | `xsd:string` | CMS Manual section number (e.g. "240.2"). NCD field. Single-valued and always the **current** version's section — see `gem:priorManualSectionNumber`. |
| `gem:priorManualSectionNumber` | `xsd:string` | A manual coordinate — publication **plus** section — the policy was published under in an earlier version and no longer appears under, written as the superseded rendition prints it, publication first: `"Pub. 6 §35-98"`. **Repeatable (0..N)**, unordered. Exists because CMS renumbers: the Coverage Issues Manual (Pub. 6) was converted into the NCD Manual (Pub. 100-03), and sections were renumbered within a publication too, so one policy document (one NCDId) can carry several coordinates over its life — and a citation written against an old coordinate must still resolve to the policy holding that content today. Carries **no date and no version linkage**; `gem:publicationNumber` + `gem:manualSectionNumber` remain the single-valued current-version facts. Absence means no renumbering is *recorded*, not that none occurred — the history is only visible when every version rendition was supplied at extraction. Introduced S152 at NCD 270.1 (Pub. 6 §35-98 → Pub. 6 §35-102 → Pub. 100-3 §270.1); a deliberately partial answer to `deferred_proposals[98]`, which first-class version individuals would subsume. |
| `gem:policyVersion` | `xsd:string` | Version/revision label of the current iteration, recorded verbatim (NCD "2", LCD "R11", Article "R17"). Scheme is not validated. |
| `gem:policyEffectiveDate` | `xsd:date` | Date the current version took legal effect as a coverage determination. Distinct in meaning from any claim-side date. |
| `gem:policyImplementationDate` | `xsd:date` | Date contractors were directed to reflect the policy in claims processing. Distinct from the effective date. |
| `gem:policyPageCount` | `xsd:integer` | Page count of the source document at the time of extraction, taken from the PDF rendering that served as the authoritative source. Operational metric for triage; not semantically tied to coverage decisions. |

### 2h. Qualification group class and reference property

| Term | Kind | Label |
| :--- | :--- | :--- |
| `gem:QualificationGroup` | class | "Qualification Group" |
| `gem:refersToQualificationGroup` | object property, `gem:CMSpolicy` → `gem:QualificationGroup` | "Refers to Qualification Group" |

A flat controlled vocabulary of the named patient-qualification tiers (Group I, Group II, …) that policies define. Group individuals are in the `gemi:` namespace, **one shared individual per named group, reused across policies** — one `gem:refersToQualificationGroup` link per policy that names the group. The link records presence of the named tier only; it does **not** assert that policies sharing a group name define the tier identically, and the criteria that define a group are **not** bundled onto the group individual — they remain independent `gem:ClinicalConcept` links on the policy. Group individuals are minted only for groups actually named by a processed policy. Promoted from a deferred proposal at the session-2 review.

### 2i. Benefit category class and reference property

| Term | Kind | Label |
| :--- | :--- | :--- |
| `gem:BenefitCategory` | class, `rdfs:subClassOf skos:Concept` | "Benefit Category" |
| `gem:refersToBenefitCategory` | object property, `gem:CMSpolicy` → `gem:BenefitCategory` | "Refers to Benefit Category" |

A flat controlled vocabulary of the named Medicare benefit categories under which items and services may fall (e.g. "Durable Medical Equipment", "Ambulance Services", "Diagnostic Laboratory Tests"). Category individuals are in the `gemi:` namespace, **one shared individual per named category, reused across policies** — one `gem:refersToBenefitCategory` link per policy that names the category. The link records presence of the named category in the policy's scope only; it does not assert coverage polarity for items within the category, and the policy's coverage rules for items in a category are not bundled onto the category individual. Categories are minted only when actually named by a processed policy. The vocabulary is the categories CMS names in its policies, not an exhaustive Medicare benefit taxonomy. Introduced by NCD 310.1, which enumerates 72 categories whose routine costs are eligible for clinical-trial coverage.

### 2j. Anchored Coding Scope class family and per-scope relationships

An **anchored coding scope** (`gem:AnchoredCodingScope`, abstract) is a structural rule-organization unit inside a CMS Policy that anchors to one or more claim-line codes via the `gem:appliesWhenCode` predicate family (with sub-properties `gem:appliesWhenProcedure`, `gem:appliesWhenModifier`, and `gem:appliesWhenCondition` for HCPCS procedures, HCPCS modifiers, and ICD-10 diagnoses respectively) and scopes a set of coverage, medical-necessity, or coding-correctness assertions to claims carrying the anchor's codes. Two concrete subclasses, distinguished by their source pattern in the policy document:

- **`gem:PolicyGroup`** — the documented anchor-scope variant; a CMS-published Group from a policy's Coding Information section (typically pairing a HCPCS-anchor list with a closed list of supporting ICD-10 codes, or, in the Group 1A pattern, a list of ICDs explicitly excluded for those HCPCS).
- **`gem:PolicyCodingRule`** — the prose-derived anchor-scope variant; the extractor's reification of a Coding Guidelines (or comparable prose) statement expressing a coding-correctness boundary scoped to a HCPCS anchor.

The umbrella predicate `gem:hasAnchoredCodingScope` links a policy to either subclass; sub-properties `gem:hasPolicyGroup` and `gem:hasPolicyCodingRule` narrow by subclass.

| URI | Kind | Domain | Range | prefLabel |
|-----|------|--------|-------|-----------|
| `gem:AnchoredCodingScope` | class (abstract) | — | — | "Anchored Coding Scope" |
| `gem:PolicyGroup` | class (subclass of `gem:AnchoredCodingScope`) | — | — | "Policy Group" |
| `gem:PolicyCodingRule` | class (subclass of `gem:AnchoredCodingScope`) | — | — | "Policy Coding Rule" |
| `gem:hasAnchoredCodingScope` | object property | `gem:CMSpolicy` | `gem:AnchoredCodingScope` | "Has Anchored Coding Scope" |
| `gem:hasPolicyGroup` | object property (sub-property of `gem:hasAnchoredCodingScope`) | `gem:CMSpolicy` | `gem:PolicyGroup` | "Has Policy Group" |
| `gem:hasPolicyCodingRule` | object property (sub-property of `gem:hasAnchoredCodingScope`) | `gem:CMSpolicy` | `gem:PolicyCodingRule` | "Has Policy Coding Rule" |
| `gem:appliesWhenCode` | object property (umbrella) | `gem:AnchoredCodingScope` | — (sub-properties carry kind-specific ranges) | "Applies When Code" |
| `gem:appliesWhenCondition` | object property (sub-property of `gem:appliesWhenCode`) | `gem:AnchoredCodingScope` | `gem:ICDdiagnosis` | "Applies When Condition" |
| `gem:appliesWhenModifier` | object property (sub-property of `gem:appliesWhenCode`) | `gem:AnchoredCodingScope` | `gem:HCPCSmodifier` | "Applies When Modifier" |
| `gem:appliesWhenProcedure` | object property (sub-property of `gem:appliesWhenCode`) | `gem:AnchoredCodingScope` | `gem:HCPCSprocedure` | "Applies When Procedure" |

**Predicates available on either subclass.** The S60 schema reorganization extended the domains of `gem:exclusivelyCoversCondition`, `gem:exclusivelyCoversProcedure`, `gem:excludesCondition`, and `gem:excludesProcedure` to the union `(gem:CMSpolicy, gem:AnchoredCodingScope)` — joined at S197 by `gem:referencesPolicy` and the three setting-polarity predicates (`gem:coversInHealthcareSetting`, `gem:exclusivelyCoversInHealthcareSetting`, `gem:excludesHealthcareSetting`), which were declared on the union from the start — making all four polarity-bearing predicates available on both `gem:PolicyGroup` and `gem:PolicyCodingRule` instances (as well as at policy level). (`gem:ruleDescription` was likewise on this union at S60, but its domain was later changed: extended to a three-way union including `gem:PolicyRule` at S67, then **narrowed to `gem:PolicyRule` exclusively at S86** — so rule strings no longer attach to anchor-scope or policy subjects; they live on `gem:PolicyRule` individuals reached via `gem:hasPolicyRule`. See §2l.) See §2c.

#### Anchor predicate family

The `gem:appliesWhenCode` predicate family is the property-side counterpart to the `gem:AnchoredCodingScope` class family. It expresses the conditional-applicability relationship between a scope and the claim-line codes whose presence triggers the scope's rules. The family consists of an umbrella property and three sub-properties partitioned by code kind:

- **`gem:appliesWhenCode`** — umbrella property; no `rdfs:range` declared (sub-properties carry kind-specific ranges); used for cross-cutting queries via RDFS sub-property entailment.
- **`gem:appliesWhenProcedure`** — sub-property; range `gem:HCPCSprocedure`. The most common anchor pattern in CMS Articles: a Coding Information Group Paragraph reading "For HCPCS codes X, Y, Z:" pairs the listed HCPCS procedures with the Group's ICD-10 list.
- **`gem:appliesWhenModifier`** — sub-property; range `gem:HCPCSmodifier`. First instantiated by A52514's Group 1 (paragraph "For all claims submitted with the N3 modifier"), which pairs the N3 modifier with the Group's ICD-10 exclusion list.
- **`gem:appliesWhenCondition`** — sub-property; range `gem:ICDdiagnosis`. Anticipated for the "mutually exclusive conditions" pattern in CMS policies (where one ICD-10 diagnosis on a claim triggers a constraint on other ICDs); first corpus instance pending.

**Same-kind vs cross-kind anchor semantics.** Within a single anchor predicate, multiple values are interpreted **disjunctively** — a claim need only carry ONE of the listed codes of that kind to match. Across anchor predicates of different kinds on the same scope, the multiple anchors are interpreted **conjunctively** — the claim must satisfy at least one assertion in EACH anchor kind present. Example: a scope with `gem:appliesWhenProcedure hcpcs:A1234, hcpcs:A1235` and `gem:appliesWhenModifier hcpcs:KX` matches a claim carrying (A1234 OR A1235) AND KX.

**Policy-level materialization asymmetry.** Of the three anchor kinds, only the procedure anchor (`gem:appliesWhenProcedure`) gets a policy-level materialization rule: a HCPCS procedure named in a Group's anchor is *also* asserted at policy level via `gem:coversProcedure` on the enclosing CMS Policy (the "prerequisite procedures of a documented Group are themselves within the policy's coverage scope" rule). Modifier anchors do not get this materialization — modifiers are billing instructions on claim lines rather than separately covered or excluded items, and the policy's references to modifiers are captured at policy level via the polarity-neutral `gem:refersToHCPCSmodifier`. Diagnosis anchors (`gem:appliesWhenCondition`) likewise do not get an analogous materialization; the policy-level diagnosis references are captured via the polarity-bearing `gem:coversCondition` / `gem:excludesCondition` predicates as appropriate, separately from the per-scope anchor role.

#### Policy Groups

**Minting rule.** Create a `gem:PolicyGroup` instance when EITHER (a) the policy lists one or more prerequisite HCPCS procedures that constrain the application of its rules, OR (b) the policy contains more than one parallel rule-set within its Coding Information section. A policy that has neither does not need Policy Groups, and its `gem:exclusivelyCoversCondition` and `gem:exclusivelyCoversProcedure` triples (where they apply) are asserted directly on the policy individual.

**Matching algorithm** (downstream from this graph, when a claim is being matched to a Group-structured policy):

1. For each Policy Group of the policy, check whether any of the claim's HCPCS codes appears in the Group's `gem:appliesWhenProcedure` set.
2. If a match exists, evaluate the claim's ICD-10 codes against the Group's `gem:exclusivelyCoversCondition` list. Any ICD-10 code in the claim that is NOT in the list is grounds for denial within that Group's scope. Where the Group also carries `gem:excludesCondition` triples (the Group 1A pattern), an explicit denial for any listed ICD additionally applies.
3. The exclusion of "all ICDs not in the listed set" is implicit in the closed-list semantic and queryable via SPARQL `FILTER NOT EXISTS`; it is not materialized as `gem:excludesCondition` triples (except in the Group 1A pattern, where the source itself denies specific ICDs).

**Source-fidelity principle.** Within Group-structured policies, the source asserts ICD-10 codes only inside Group Codes lists — never at policy level. The graph mirrors that: no policy-level `gem:coversCondition` triples are materialized for the ICDs that appear only in Groups. A query for "does policy P reference ICD X anywhere?" requires a 2-hop traversal through `gem:hasPolicyGroup` to reach the per-Group assertions. The HCPCS side is treated asymmetrically: a HCPCS code in a Group's `gem:appliesWhenProcedure` set is ALSO materialized as a policy-level `gem:coversProcedure` triple on the enclosing CMS Policy, because the Group Paragraph's naming of the HCPCS *is* a policy-level coverage assertion at the policy/Group structural junction. The source makes policy-level HCPCS claims (in Group Paragraphs and in the Article Text's prose discussion of specific codes) but does not make policy-level ICD claims for Group-structured policies — the asymmetric materialization rule reflects that.

**Closed-list semantic.** The closed-list rule is carried by the two sub-properties `gem:exclusivelyCoversCondition` and `gem:exclusivelyCoversProcedure` (§2c). On a Policy Group, the union of `gem:exclusivelyCoversCondition` objects constitutes the COMPLETE set of conditions covered by the Group within the scope of the Group's prerequisite HCPCS; any ICD-10 code not in the union is implicitly excluded. The same property used directly at policy level (for policies without Groups) carries the analogous policy-wide closure.

**Worked example — A52466 (Nebulizers Policy Article).**

- A52466 carries 16 Policy Group instances, `gemi:a52466_group1` through `gemi:a52466_group16`.
- Each Group's `gem:appliesWhenProcedure` set lists the HCPCS codes named in its "For HCPCS codes X, Y, Z:" Paragraph — for example, `gemi:a52466_group1 gem:appliesWhenProcedure hcpcs:A4619, hcpcs:E0565, hcpcs:E0572`.
- Each Group's `gem:exclusivelyCoversCondition` set is the list of ICD-10 codes published under that Group's "Group N Codes" — 64 codes for Group 1, 201 for Group 2, … 13 for Group 16; 1,342 announced total across the 16 Groups (213 unique, since the same ICD commonly appears in multiple Groups when it qualifies for multiple HCPCS contexts).
- A52466's "DO NOT Support Medical Necessity" section is *not* modeled as a Policy Group, because A52466's DNS content is all policy-wide blanket denial — not the per-anchor pattern that yields a Group. The 35 universally-denied HCPCS named there become 35 `gem:excludesProcedure` triples on `gemi:a52466`; the per-Group ICD complement is implicit in each Support Group's closed-list semantic; and the "silence for all other HCPCS" rule is the graph's open-world default.
- The HCPCS anchor codes of each Group appear BOTH as `gem:appliesWhenProcedure` on their Group AND as `gem:coversProcedure` on `gemi:a52466` (the "prerequisite procedures are covered" inferential rule, materialized at extraction).

**Worked example — A52519 Group 1A (negative-polarity Group).**

- A52519 carries two Policy Group instances: `gemi:a52519_group1` (the Support Group, anchored to HCPCS A4605, A4624, listing the closed ICD set via `gem:exclusivelyCoversCondition`) and `gemi:a52519_group1a` (the per-anchor diagnostic exclusion drawn from A52519's DNS section).
- `gemi:a52519_group1a` carries `gem:appliesWhenProcedure hcpcs:A7002, hcpcs:A7047, hcpcs:E0600` and `gem:excludesCondition icd10:G47.33` — encoding the policy's "Group 1A: For A7002, A7047, E0600, G47.33 does not support medical necessity" statement.
- The negative-polarity capability on `gem:PolicyGroup` is provided by the S60 domain extension of `gem:excludesCondition` to `union(gem:CMSpolicy, gem:AnchoredCodingScope)`. A separate `DenialGroup` sibling class was considered and not adopted because the umbrella + domain-extension path preserves single-class instance modeling at the same query semantics.

**Worked example — A52514 Group 1 (modifier-anchored Group).**

- A52514 carries one Policy Group, `gemi:a52514_group1`, drawn from the policy's Coding Information / ICD-10-CM Codes that DO NOT Support Medical Necessity section, Group 1 (5 Codes).
- Unlike A52466 and A52519 (both procedure-anchored), this Group is anchored on a HCPCS Level II modifier: `gemi:a52514_group1 gem:appliesWhenModifier hcpcs:N3`. The N3 modifier is appended to oxygen-equipment claim lines when the supplier asserts that all Group III LCD criteria (normoxemic, non-respiratory) have been met.
- The Group excludes 5 ICDs all encoding hypoxemic conditions: `gem:excludesCondition` for `icd10:J96.01`, `icd10:J96.11`, `icd10:J96.21`, `icd10:J96.91`, and `icd10:R09.02`. The source paragraph "For all claims submitted with the N3 modifier" pairs them with N3 because the N3 assertion (normoxemia, Group III) is incompatible with these hypoxemic diagnoses.
- A Medicare claim line carrying the N3 modifier together with any of these five ICDs is a reason for denial within this Group's scope. The five ICDs do NOT, however, exclude coverage on claims that do not carry N3 (a Group I or II beneficiary may legitimately bear one of these diagnoses); the scoping is essential, and pre-S70 unconditional policy-level `gem:excludesCondition` triples (now migrated into this Group) misrepresented the policy.
- First corpus instance of a modifier-anchored Coding Information Group; motivated the S70 codification of the `gem:appliesWhenCode` anchor predicate family.

#### Policy Coding Rules

**Minting rule.** Create a `gem:PolicyCodingRule` instance when policy prose (typically in a Coding Guidelines or analogous section) names a HCPCS anchor and asserts a coding-correctness boundary on that anchor — i.e., when the source says something equivalent to "for [HCPCS X], you may not also bill [HCPCS Y]" or "[HCPCS X] is correctly coded only when [condition on other codes]." A policy-wide boundary that is not anchored to a specific HCPCS is asserted at policy level using ordinary predicates and does not yield a Policy Coding Rule.

**URI minting.** Single-anchor form (the only pattern observed so far): `gemi:<policyLocalName>_<anchorCode>CodingRule`. Example: `gemi:a52519_a7047CodingRule`. Multi-anchor Policy Coding Rules have not yet been encountered; the URI form for that case will be resolved as a borderline at first occurrence. See §5 for the URI-minting table entry.

**Triple-writing pattern.** Per rule:

1. `<policy> gem:hasPolicyCodingRule <rule>` (umbrella `gem:hasAnchoredCodingScope` reached by entailment via the sub-property declaration).
2. `<rule> gem:appliesWhenProcedure <hcpcs>` for the anchor HCPCS.
3. Polarity-appropriate boundary assertions on the rule: `gem:excludesProcedure` / `gem:exclusivelyCoversProcedure` for HCPCS boundaries; `gem:excludesCondition` / `gem:exclusivelyCoversCondition` for ICD boundaries.
4. The anchor HCPCS is also asserted at policy level via `gem:coversProcedure` (the prerequisite-HCPCS-are-covered materialization rule), unless excluded elsewhere by the policy.
5. Optional `gem:ruleDescription` annotation carrying the verbatim or near-verbatim source prose.

**Worked example — A52519 a7047CodingRule.**

- `gemi:a52519_a7047CodingRule` carries `gem:appliesWhenProcedure hcpcs:A7047`, `gem:excludesProcedure hcpcs:E0485`, and `gem:excludesProcedure hcpcs:E0486` — encoding the policy's Coding Guidelines statement that when A7047 is used, codes E0485 and E0486 may not also be billed.
- This rule originates from A52519's Coding Guidelines (prose), not from a CMS-numbered Group structure — hence `gem:PolicyCodingRule` rather than `gem:PolicyGroup`.

---

### 2k. Workflow-state schema (next-planned-step + isInEffect)

Introduced 2026-06-08 (Session 45). Every `gem:CMSpolicy` instance — whether a fully-extracted policy or a stub — carries two orthogonal workflow-state assertions.

**Class and named individuals:**

| URI | Kind | Parent | prefLabel | Meaning |
|-----|------|--------|-----------|---------|
| `gem:NextPlannedStep` | class | `skos:Concept` | "Next Planned Step" | Controlled-vocabulary class for the named workflow states. |
| `gem:planPromote` | individual | `gem:NextPlannedStep` | "Promote" | Stub queued for advancement to full extraction. Default for newly-minted stubs. |
| `gem:planNone` | individual | `gem:NextPlannedStep` | "None" | No further work is intended on the document. States intent only; no other meaning may be inferred. User-set. |
| `gem:planDone` | individual | `gem:NextPlannedStep` | "Done" | Fully extracted via normal two-turn workflow. |
| `gem:planRevisit` | individual | `gem:NextPlannedStep` | "Revisit" | Queued for re-examination and verification regardless of past completeness. User-set. |

**Properties:**

| URI | Kind | Domain | Range | Meaning |
|-----|------|--------|-------|---------|
| `gem:nextPlannedStep` | object property | `gem:CMSpolicy` | `gem:NextPlannedStep` | The next planned work step for this policy. |
| `gem:isInEffect` | datatype property | `gem:CMSpolicy` | `xsd:boolean` | Whether the document is still carried by its publisher (true) or GEM knows the publisher removed it (false). |

**Default assignment by category** (Action 6c rule, Session 45):

| Category | `nextPlannedStep` default | `isInEffect` default |
|----------|--------------------------|----------------------|
| Fully extracted (worklist status=processed) | `gem:planDone` | `true` |
| NCA (`gem:NCAdocument`) | `gem:planPromote` (always, even when superseded) | `true` |
| `_DELETED` URI suffix | `gem:planNone` | `false` |
| Other stub (default) | `gem:planPromote` | `true` |

There is exactly **one** road to `isInEffect=false`: GEM knows the publisher removed the document. The Session 45 row *"Other stub, `is_current=false` → `gem:planNone` / `false`"* is **deleted** (Session 159). It was the rule that put `false` on 31 transmittals, 4 NCAs and 2 change requests whose only offence was delivering or analysing a version that a later version superseded. `gem:planNone` survives on those documents unchanged — no further work is intended on them, which is all that value ever claimed.

The two properties are orthogonal, and so is the third (§2k-bis). A superseded NCA carries `gem:planPromote` (future extraction in scope) and `gem:isInEffect=true` (CMS still publishes it). A document deleted from its manual carries `gem:planNone` and `gem:isInEffect=false`. A fully-extracted current policy carries `gem:planDone` and `gem:isInEffect=true`. `gemi:tn78CIM` is `gem:planNone`, `gem:isInEffect=true` and `gem:sourceUnobtainable`, and none of the three follows from the others.

---

#### What `gem:isInEffect` means

*The written definition owed since Session 148 (§3 B5) and carried as an unowned scrap through eleven handoffs. Settled by Tom, Session 159, and it closes `deferred_proposals[97]`.*

**`true`** — the document is still carried by its publisher as an operative document. **`false`** — GEM has *knowledge* that the publisher removed it: a manual section deleted from the manual it was published in, or a published document withdrawn. **Absence of knowledge is not removal**, so a stub GEM has never read is `true` by default. The property is asserted on all **327** `gem:CMSpolicy` individuals and is `false` on **six**.

Three things it does **not** record.

- **Retirement in place.** A section that survives its own coverage determination — retitled RETIRED, left in the manual, its live text stating that no NCD is appropriate and that the MACs decide — is still in the manual. `gemi:ncd180.2` and `gemi:ncd240.2.2` are `true`, and they are `true` **because** they are retired in place, not despite it. `gemi:ncd280.13` was retired **and removed**, incorporated into NCD 160.27, and is `false` — under this definition it is *deleted*, not retired. That is why the NCD count is **51 active / 0 stubs / 2 retired / 6 deleted**, and why both earlier counts (Session 150's, Session 158's) were wrong.
- **Rescission or supersession.** A rescinded transmittal, a superseded delivery and a superseded NCA all remain published, and each still governs or explains claims dated before the change. `gemi:tn2402CP` is rescinded by TN 2476 and is `true`. A fact about the version a document delivered belongs to **that version**, not to the deliverer: `gemi:tn48NCD` revises twenty policies, its text is still current for some and superseded for others, and one boolean cannot hold twenty answers.
- **Version currentness.** Whether an individual describes the version presently in force is a different question on a different subject. It is not asked here, and it is not answerable until version individuals exist — `deferred_proposals[98]`, which is where `gem:isCurrent` will land.

**And it does not answer whether a policy applies to a claim.** Applicability is a relation between a *policy version* and a *date of service*, and this property carries neither.

- An `isInEffect=false` document may still govern claims dated before its removal. `gemi:ncd280.13` governs a 2010 TENS claim still in litigation.
- An `isInEffect=true` document's live text may be the wrong text for an older claim. `gemi:ncd180.2` carries exactly one rule — *"Effective January 1, 2022 … no national coverage determination is appropriate … MACs decide"* — and a 2021 enteral-nutrition claim is governed by V1's substantive criteria, which are **not in the graph** (see that policy's B2 in `gem_rule_categories.md`). A consumer filtering on `isInEffect=true` gets a confidently wrong answer rather than a missing one.

That axis is `deferred_proposals[98]`'s and is not this property's.

**History.** Introduced 2026-06-08 (Session 45) as a rename of the worklist's `is_current` field, and **the rename is where the defect entered**: it moved a *version*-scoped fact onto a *policy* subject and swapped a currentness name for one asserting legal force. Currentness is a fact about *now* and can be a boolean; legal force is a fact about a *date of service* and cannot. Redefined 2026-07-17 (Session 159) to the publication-status question alone — which the corpus had been answering correctly all along on every document-class individual. All 103 document-class values were already right; the 37 corrections were on the classes the Session 45 rule never fit.

---

### 2k-bis. Source-availability schema (`gem:sourceAvailability`)

Introduced 2026-07-17 (Session 156). A **Source Availability** records the obtainability of a policy document's own source rendition — a fact about GEM's *access to the artifact*, not about the document's coverage disposition. It is the third axis alongside §2k's two, and it is orthogonal to both: `gemi:tn78CIM` is **still published** (`gem:isInEffect true`), has **no further work intended** (`gem:planNone`), and is **unobtainable**, and none of the three facts follows from the others.

**Class and named individuals:**

| URI | Kind | Parent | prefLabel | Meaning |
|-----|------|--------|-----------|---------|
| `gem:SourceAvailability` | class | `skos:Concept` | "Source Availability" | Controlled-vocabulary class for the named obtainability values. |
| `gem:sourceUnobtainable` | individual | `gem:SourceAvailability` | "Unobtainable" | The source rendition does not exist in any fetchable form and none is expected. User-set. Established case: the pre-2000 Coverage Issues Manual transmittals, which were paper-only and were never digitized (CMS's public transmittal archive begins at 2000). |

**Property:**

| URI | Kind | Domain | Range | Meaning |
|-----|------|--------|-------|---------|
| `gem:sourceAvailability` | object property | `gem:CMSpolicy` | `gem:SourceAvailability` | The obtainability of this document's source rendition. At most one value; **absent by default**. |

**The vocabulary is deliberately one-member, and the absence of the property is the point.** There is no `sourceAvailable` and no `sourcePending`. A document carries `dc:source` (a rendition exists and is recorded), or `gem:sourceUnobtainable` with no `dc:source` (checked; no rendition exists), or **neither** — which asserts nothing and means *nobody has checked*. That third state is what makes the unverified set **derivable from the graph rather than maintained as a roster**: a CIM transmittal with neither fact is undetermined by construction, and each one that resolves — either way — leaves the set by itself. `gem_audit.py`'s `source_availability_unverified` check (INFO tier; a work queue, not drift) reports exactly that derivation. Adding an affirmative "available" member would break the property, because it would make silence ambiguous again.

**Relationship to `gem:planNone`.** The two travel together but say different things. `gem:planNone` says *no further work is intended*; `gem:sourceUnobtainable` says *why* — no further work is **possible**. §2k's default table reaches `gem:planNone` by only one road (`_DELETED`); an unobtainable document is a second, and every other use is user-set. The reason lives here rather than being read out of prose. This split is the point of the property: it is what kept `gem:nextPlannedStep` from acquiring the second job `gem:isInEffect` acquired — and Session 159 removed that second job at the source, resolving `deferred_proposals[97]` and narrowing `gem:planNone` to a statement of intent and nothing else (Tom, S159).

| Category | `nextPlannedStep` | `isInEffect` | `sourceAvailability` |
|----------|-------------------|--------------|----------------------|
| Rendition exists (recorded in `dc:source`) | per §2k | per §2k | *(absent)* |
| Rendition exists but URL not yet backfilled | per §2k | per §2k | *(absent)* |
| Checked; no rendition exists and none expected | `gem:planNone` | **unchanged** — publication status is orthogonal | `gem:sourceUnobtainable` |
| Not yet checked | per §2k | per §2k | *(absent)* |

Note rows 1, 2 and 4 are indistinguishable on this property alone — that is intended. Rows 1–2 are separated by `dc:source`; rows 2 and 4 are separated only for CIM-era documents, where the `source_availability_unverified` check treats "no `dc:source`, no `gem:sourceAvailability`" as row 4. For post-2003 transmittals the rendition is published by construction, so a missing URL is row 2 (a backfill item), never row 4.

---

### 2l. Policy Rule class and verbatim-content relationship

A **Policy Rule** (`gem:PolicyRule`) is a first-class rule entity that carries the verbatim text of a single rule extracted from a CMS coverage policy — one self-contained criterion, requirement, or constraint. It is the post-migration home for what were formerly `gem:ruleDescription` strings attached directly to a CMS Policy (or an Anchored Coding Scope): the multi-phase migration tracked in `deferred_proposals[72]` has minted a distinct `gem:PolicyRule` instance per rule (391 individuals as of S85), with the string carried via `gem:ruleDescription` on the PolicyRule subject and the policy / anchor-scope subject linking to it via `gem:hasPolicyRule`.

**Disambiguation from `gem:PolicyCodingRule`.** Despite the name proximity, the two classes operate at orthogonal ontological layers and have no subclass relation:

- `gem:PolicyCodingRule` (S60) — a structural anchor-scope subclass (under `gem:AnchoredCodingScope`) for code-to-code coding-correctness constraints derived from policy prose. *Where* a rule applies, structurally.
- `gem:PolicyRule` (S67) — a content unit that holds the verbatim text of a rule. *What* the rule says.

The two may co-occur within a policy without subclass relation. The S67 introduction scoped `gem:hasPolicyRule` to `gem:CMSpolicy` subjects only; S83 (the Phase-4 launch) extended its domain to `(gem:CMSpolicy ∪ gem:AnchoredCodingScope)`, so anchor-scope subjects — including `gem:PolicyCodingRule` — now attach `gem:PolicyRule` individuals via `gem:hasPolicyRule`. A future schema cycle may still introduce a *closer, more direct* relationship between the two classes, beyond this generic attachment.

| URI | Kind | Domain | Range | prefLabel |
|-----|------|--------|-------|-----------|
| `gem:PolicyRule` | class | — | — | "Policy Rule" |
| `gem:hasPolicyRule` | object property | `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` | `gem:PolicyRule` | "Has Policy Rule" |

**Domain of `gem:ruleDescription`.** The S67 introduction extended `gem:ruleDescription`'s domain to the three-way union `(gem:CMSpolicy, gem:AnchoredCodingScope, gem:PolicyRule)`, allowing the verbatim-text property to carry from any of the three subject types during the migration window. The S86 Phase-4 closeout reached the end state: the domain was **narrowed to `gem:PolicyRule` exclusively**, so `gem:ruleDescription` now lives only on `gem:PolicyRule` subjects (enforced by `rdfs:domain`, by `gem:PolicyRuleShape`, and by the audit's `check_ruledescription_domain_conformance`).

**Multi-phase rollout (per `deferred_proposals[72]`).**

1. **Phase 1 (S67, complete):** Codify `gem:PolicyRule` class, `gem:hasPolicyRule` predicate, extend `gem:ruleDescription` domain. *Schema substrate only — no instance migration yet.*
2. **Phase 2 (pending):** Codify the structured-decomposition schema (qualifying-condition trees, atomic predicates, coverage-outcome decomposition). The seven open design decisions in `gem_structured_rule_guide.md` are largely settled (six of seven resolved at S68); what remains pending is codifying the decomposition schema itself, deferred until the claim-data substrate is better understood.
3. **Phase 3 (complete, S85):** Migrated `gem:ruleDescription` triples attached to `gem:CMSpolicy` subjects — minted a `gem:PolicyRule` URI per rule string, moved the string from the policy to the new PolicyRule, and asserted `<policy> gem:hasPolicyRule <newRule>` to preserve the policy-to-rule relationship.
4. **Phase 4 (complete, S83–S85; schema closeout S86):** Migrated `gem:ruleDescription` triples attached to `gem:AnchoredCodingScope` subjects (PolicyGroup, PolicyCodingRule) — the open question is resolved: those rules **do** migrate to PolicyRule subjects, attached via the S83 union-domain extension of `gem:hasPolicyRule`. The S86 closeout then narrowed `gem:ruleDescription`'s domain to `gem:PolicyRule` exclusively, completing the migration at both instance and schema level.

**Structured-decomposition schema deferred.** The full ζ-schema sketched in `gem_structured_rule_guide.md` (qualifying-condition trees of `gem:LogicalExpression` subclasses, `gem:NumericPredicate` / `gem:ConditionalPredicate` leaves, `gem:CoverageOutcome` family, controlled-vocabulary `gem:Comparator` / `gem:MeasurementContext` / etc.) remains pending Phase 2 design refinement. Phase 1 codifies only the rule-entity substrate.

---

### 2m. Coverage Qualifier hierarchy

A **Coverage Qualifier** (`gem:CoverageQualifier`) is an abstract parent class for the two kinds of condition that qualify the scope of an otherwise-positive coverage decision: `gem:CoverageRestriction` (narrows what is covered) and `gem:CoverageExclusion` (carves out a sub-case that is not covered). The hierarchy is the structured-form representation of the qualifiers that today appear inside verbatim `gem:ruleDescription` strings — for example, NCD 240.2 Group I sleep bullet's *"coverage is provided only for use of oxygen during sleep, and then only one type of unit will be covered. Portable oxygen, therefore, would not be covered in this situation."* decomposes into two `gem:CoverageRestriction` individuals (the use-case "during sleep only" and the count "one unit only") plus one `gem:CoverageExclusion` (the portable-oxygen carve-out), all attached to a shared `gem:CoverageOutcome`.

The hierarchy follows the **S60 abstract-umbrella precedent** established for `gem:AnchoredCodingScope` over `gem:PolicyGroup` + `gem:PolicyCodingRule`: an abstract parent class with two concrete subclasses, and an umbrella predicate (`gem:hasCoverageQualifier`) with two sub-properties (`gem:hasCoverageRestriction`, `gem:hasCoverageExclusion`) so cross-cutting queries over qualifier-of-any-kind work via RDFS inference without UNIONing over the sub-properties.

**Companion class: Coverage Outcome.** A `gem:CoverageOutcome` is the THEN-clause of a structured Policy Rule — the coverage decision and any qualifiers (restrictions and exclusions) that apply when the rule's qualifying conditions are met. Outcomes are first-class individuals so that one outcome may be referenced by multiple `gem:PolicyRule` instances when source prose names a single outcome for multiple qualifying scenarios (the *"In either of these cases ..."* framing). Codified header-only at S69 Phase 3a: substantive properties (`gem:decision` and the `gem:CoverageDecision` controlled vocabulary) remain pending claim-data substrate understanding per the Deferment Posture in `gem_structured_rule_guide.md`.

**Restriction Type controlled vocabulary.** A `gem:CoverageRestriction` carries a `gem:restrictionType` tag (range `gem:RestrictionType`) naming the dimension along which the restriction narrows coverage. Initial vocabulary: `gem:restrictionType_useCase` (narrows the clinical context — *"only during sleep"*), `gem:restrictionType_count` (narrows cardinality — *"only one unit"*), `gem:restrictionType_duration` (narrows a time span — *"limited to 90 days"*), `gem:restrictionType_frequency` (narrows how often — *"no more than once per twelve months"*). Vocabulary is extended as new policies surface additional restriction shapes; the parallel `gem:RuleType` controlled vocab (Phase 3 sub-cycle (b)) tags a different dimension (the kind of *rule*, not the kind of *restriction*) but uses the same pattern.

**Schema additions codified at S69 Phase 3a (work item #72).**

| URI | Kind | Parent / Sub-property of | Domain | Range | prefLabel |
|-----|------|--------------------------|--------|-------|-----------|
| `gem:CoverageOutcome` | class | — | — | — | "Coverage Outcome" |
| `gem:CoverageQualifier` | class (abstract) | — | — | — | "Coverage Qualifier" |
| `gem:CoverageRestriction` | class | `gem:CoverageQualifier` | — | — | "Coverage Restriction" |
| `gem:CoverageExclusion` | class | `gem:CoverageQualifier` | — | — | "Coverage Exclusion" |
| `gem:RestrictionType` | class (controlled vocab) | `skos:Concept` | — | — | "Restriction Type" |
| `gem:hasCoverageQualifier` | object property (umbrella) | — | `gem:CoverageOutcome` | `gem:CoverageQualifier` | "Has Coverage Qualifier" |
| `gem:hasCoverageRestriction` | object property | sub-property of `gem:hasCoverageQualifier` | `gem:CoverageOutcome` | `gem:CoverageRestriction` | "Has Coverage Restriction" |
| `gem:hasCoverageExclusion` | object property | sub-property of `gem:hasCoverageQualifier` | `gem:CoverageOutcome` | `gem:CoverageExclusion` | "Has Coverage Exclusion" |
| `gem:restrictionType` | object property | — | `gem:CoverageRestriction` | `gem:RestrictionType` | "Restriction Type" |
| `gem:restrictionConcept` | object property | — | `gem:CoverageRestriction` | `gem:ClinicalConcept` | "Restriction Concept" |
| `gem:excludedConcept` | object property | — | `gem:CoverageExclusion` | `gem:ClinicalConcept` | "Excluded Concept" |
| `gem:restrictionDescription` | datatype property | — | `gem:CoverageRestriction` | `xsd:string` | "Restriction Description" |
| `gem:exclusionDescription` | datatype property | — | `gem:CoverageExclusion` | `xsd:string` | "Exclusion Description" |
| `gem:restrictionType_useCase` | named individual | `gem:RestrictionType` | — | — | "Use Case" |
| `gem:restrictionType_count` | named individual | `gem:RestrictionType` | — | — | "Count" |
| `gem:restrictionType_duration` | named individual | `gem:RestrictionType` | — | — | "Duration" |
| `gem:restrictionType_frequency` | named individual | `gem:RestrictionType` | — | — | "Frequency" |

**Disambiguation: `gem:restrictionType_frequency` vs `gem:ruleType_frequency`.** The two value individuals share the local-name component `frequency` but tag different things:

- `gem:restrictionType_frequency` — names a kind of **restriction**: a `gem:CoverageRestriction` that narrows how often a covered item may be claimed.
- `gem:ruleType_frequency` (codified at Phase 3 sub-cycle (b)) — names a kind of **rule**: a `gem:PolicyRule` whose subject matter is frequency criteria.

The predicate context (`gem:restrictionType` vs `gem:ruleType`) disambiguates without ambiguity; the parallel naming is intentional, exposing a recognizable `<Host>Type` pattern across controlled-vocabulary classifications.

**Properties intentionally deferred at S69 Phase 3a.**

- `gem:restrictionValue` — a typed numeric value naming the count, duration, or frequency a restriction narrows to. Marked "(mixed datatype, optional)" in `gem_structured_rule_guide.md`. Deferred pending claim-data substrate understanding (the right `rdfs:range` choice depends on how multi-shape numeric values are expressed across the corpus of restrictions). In the interim, the value lives within `gem:restrictionDescription`.
- `gem:CoverageOutcome` substantive properties — `gem:decision` (object → `gem:CoverageDecision`) and the `gem:CoverageDecision` controlled vocabulary (`gem:covered`, `gem:notCovered`, possibly `gem:macDiscretion`). Out of S69 Phase 3a scope; expected in a later Phase 3 sub-cycle once the structured-decomposition use cases are tested against real policy decompositions.

**Cross-references.** See `gem_structured_rule_guide.md` §Schema Model for the full design (qualifying-condition tree, atomic predicates, comparator vocabulary), §Deferment Posture for the rationale on which design questions are deferred until the Medicare Claim data substrate is better understood, and §Worked Decomposition for the NCD 240.2 Group I sleep-bullet worked example. Phase 3 of the multi-phase migration tracked in `deferred_proposals[72]` decomposes into three sub-cycles: (a) CoverageQualifier hierarchy (S69, codified — this section); (b+c) RuleDomain / RuleType vocabularies and their value individuals (S69, codified — see §2n); instance promotion (minting `gem:PolicyRule` individuals from `gem:ruleDescription` strings and attaching `gem:ruleDomain` / `gem:ruleType` triples) was completed across S83–S85 (Phase 3 for CMSpolicy-scope rules, Phase 4 for anchor-scope rules), with the S86 closeout narrowing the `gem:ruleDescription` domain to `gem:PolicyRule`. The structured-decomposition deferred-property follow-ups remain pending.

---

### 2n. Rule categorization (RuleDomain, RuleType)

The **RuleDomain** and **RuleType** vocabularies tag a `gem:PolicyRule` along two independent classification axes. **Rule Domain** (`gem:ruleDomain`) names *what clinical activity within a policy a rule applies to* — useful when one policy spans multiple activities (e.g., NCD 210.10 covers both STI laboratory screening and High Intensity Behavioral Counseling, and rules may apply to one leg, the other, or both). **Rule Type** (`gem:ruleType`) names *what kind of evaluator criterion a rule expresses* — coverage scope, eligibility, frequency, setting, credentialed actor, and so on. Each axis is independently queryable; the two axes are not flavors of a common concept.

**Peer classes, no umbrella.** Resolved at S68 (Decision 6): `gem:RuleDomain` and `gem:RuleType` are peer controlled-vocabulary classes with no abstract `gem:RuleCategory` parent. The two classifications are independent and downstream consumers query per-axis (a rule's domain answers "which activity?", and its type answers "what kind of criterion?") rather than polymorphically over a common umbrella. This diverges intentionally from the umbrella pattern used for `gem:CoverageQualifier` (§2m) and `gem:AnchoredCodingScope` — those umbrellas exist because the two subclasses share a structural role on the same parent. RuleDomain and RuleType do not share a structural role; they are orthogonal axes.

**Semantic property naming.** Property names are semantic (`gem:ruleDomain`, `gem:ruleType`), not positional (no `gem:ruleAxis1` / `gem:ruleAxis2`). Future additional axes are additive — e.g., a prospective `gem:ruleScope` or `gem:ruleJurisdiction` would attach without requiring positional-slot renumbering of the existing axes.

**Contractor discretion is an object link, not a categorization axis (S167).** The prospective `gem:ruleJurisdiction` note above anticipated a *value-classification* axis. When contractor (MAC) discretion was implemented (`deferred_proposals[90]`), it was modeled instead as the object predicate `gem:delegatesCoverageTo` → a `gem:ProviderCredential` delegatee (§2e), not as a `gem:RuleType`/`gem:RuleDomain`-style controlled-vocabulary axis. Reason: the concept records *to whom* a coverage determination is delegated (an actor already in the graph), which is naturally an object link, and the corpus names no specific MAC/jurisdiction to enumerate as vocabulary values — only the whole-MAC-vs-MAC-medical-staff delegatee distinction, which the object already captures. A named-jurisdiction axis therefore has nothing to bind and was not built.

**Value individuals — full-mirror naming.** The value individuals on each axis carry the property name as their URI prefix: `gem:ruleDomain_<value>` and `gem:ruleType_<value>`. This is the same convention used by `gem:NextPlannedStep` (S45) and `gem:RestrictionType` (S69 Phase 3a).

**Cardinality.** Both properties are 0..n on a `gem:PolicyRule`. A rule may carry no domain tag at all (acceptable: single-domain policies don't always need an explicit domain tag, since the policy itself names the domain). A rule may carry multiple type tags when its content spans multiple criterion categories (e.g., a rule defining both who may perform a service and what setting is required carries both `gem:ruleType_credentialedActor` and `gem:ruleType_settingDefinition`).

**Schema additions codified at S69 Phase 3 sub-cycle (b+c) (work item #72).**

| URI | Kind | Parent | Domain | Range | prefLabel |
|-----|------|--------|--------|-------|-----------|
| `gem:RuleDomain` | class (controlled vocab) | `skos:Concept` | — | — | "Rule Domain" |
| `gem:RuleType` | class (controlled vocab) | `skos:Concept` | — | — | "Rule Type" |
| `gem:ruleDomain` | object property | — | `gem:PolicyRule` | `gem:RuleDomain` | "Rule Domain" |
| `gem:ruleType` | object property | — | `gem:PolicyRule` | `gem:RuleType` | "Rule Type" |

**`gem:RuleDomain` value individuals (3).**

| URI | prefLabel | Tag for |
|-----|-----------|---------|
| `gem:ruleDomain_screening` | "Screening" | Rule applies to laboratory screening services only (e.g., NCD 210.10's STI laboratory screening leg). |
| `gem:ruleDomain_hibc` | "HIBC" | Rule applies to High Intensity Behavioral Counseling services only (e.g., NCD 210.10's HIBC leg). |
| `gem:ruleDomain_crossCutting` | "Cross-Cutting" | Rule applies to both/either service within a multi-domain policy. |

**`gem:RuleType` value individuals (19).**

| URI | prefLabel | Tag for |
|-----|-----------|---------|
| `gem:ruleType_coverageScope` | "Coverage Scope" | What is covered, at what level. |
| `gem:ruleType_eligibility` | "Eligibility" | Who/when is eligible. |
| `gem:ruleType_frequency` | "Frequency" | How often / repeat-screening intervals. |
| `gem:ruleType_settingDefinition` | "Setting Definition" | What setting is required (positive definition + exclusions). |
| `gem:ruleType_credentialedActor` | "Credentialed Actor" | Who can order/perform/provide. |
| `gem:ruleType_serviceDefinition` | "Service Definition" | Defines a service itself. |
| `gem:ruleType_serviceStandard` | "Service Standard" | Technical standards (FDA, CLIA, etc.). |
| `gem:ruleType_riskFactor` | "Risk Factor" | Enumerates risk factors. |
| `gem:ruleType_riskDetermination` | "Risk Determination" | Who/how determines risk. |
| `gem:ruleType_documentation` | "Documentation" | Documentation requirements. |
| `gem:ruleType_nonCoverage` | "Non-Coverage" | What is NOT covered. |
| `gem:ruleType_costSharing` | "Cost Sharing" | Patient cost obligations. |
| `gem:ruleType_concurrentServices` | "Concurrent Services" | What services can be billed on the same date / together. |
| `gem:ruleType_statutoryFraming` | "Statutory Framing" | Scope-defining reference to statute. |
| `gem:ruleType_studyDesign` | "Study Design" | Content, structure, or analytical plan a study must follow. |
| `gem:ruleType_studyQuality` | "Study Quality" | Methodological-integrity standards a study must meet. |
| `gem:ruleType_outcomeMeasure` | "Outcome Measure" | How a study measures or characterizes an outcome. |
| `gem:ruleType_procedural` | "Procedural" | Program-administrative process distinct from claim-eligibility rules. |
| `gem:ruleType_definition` | "Definition" | Generic catch-all for definitional rules not covered by the more-specific type categories. |

**Disambiguation: `gem:ruleType_frequency` vs `gem:restrictionType_frequency`.** The two share the local-name component `frequency` but tag different things along different axes:

- `gem:ruleType_frequency` — names a kind of **rule** (`gem:PolicyRule`): the rule's subject matter is frequency criteria. Carried on a rule via `gem:ruleType`.
- `gem:restrictionType_frequency` — names a kind of **restriction** (`gem:CoverageRestriction`): the restriction narrows how often a covered item may be claimed. Carried on a restriction via `gem:restrictionType`.

The predicate context (`gem:ruleType` vs `gem:restrictionType`) disambiguates without ambiguity. The parallel naming is intentional: both follow the `<Host>Type_<value>` controlled-vocab pattern.

**MD-file role transition (in effect — hybrid model).** The `gem_rule_categories.md` per-policy assignment tables were the intake source for which rules carry which domain and type values; that categorization is now promoted to the graph — all 391 `gem:PolicyRule` individuals carry `gem:ruleType` triples (and `gem:ruleDomain` where applicable), attached during instance promotion (S83–S85). Under the hybrid source-of-truth model in effect: the assignment tables remain the **Plan-turn authoring surface** where a new policy's rules are first categorized, but once a rule is minted as a `gem:PolicyRule` individual the **graph is authoritative** for it, and that policy's table rows become provenance/historical record. Going forward the MD file focuses on vocabulary definitions, evolution history, and Plan-turn intake; per-rule categorization, once in the graph, is read from the graph (the audit enforces this: every `gem:PolicyRule` must carry ≥1 `gem:ruleType`). This transition is distinct from the S69 sub-cycle (b+c) vocabulary codification.

**Cross-references.** See `gem_structured_rule_guide.md` §`gem:RuleDomain` and §`gem:RuleType` for the per-value vocabulary and design rationale; §6 of the same document for the categorization-axes resolution paragraph (S68 Decision 6); `gem_rule_categories.md` for the canonical per-policy assignment tables and the values' evolution history.

### 2o. Code Group class family

| term | kind | prefLabel |
| `gem:CodeGroup` | class, `rdfs:subClassOf skos:Concept` | "Code Group" |
| `gem:identifiesClinicalConcept` | object property, `gem:CodeGroup` -> `gem:ClinicalConcept` | "Identifies Clinical Concept" |
| `gem:codeGroupOwner` | annotation property, `rdfs:subPropertyOf dcterms:rightsHolder`, `gem:CodeGroup` -> `xsd:string` | "Code Group Owner" |
| `gem:memberCodePattern` | datatype property, `gem:CodeGroup` -> `xsd:string` (regex matched against code IRIs) | "Member Code Pattern" |
| `gem:refersToCodeGroup` | object property, `gem:CMSpolicy` -> `gem:CodeGroup` (materialized policy->group link) | "Refers to Code Group" |
| `gem:CodeGroupShape` | SHACL node shape, `sh:targetClass gem:CodeGroup` | "CodeGroup structural shape" |

A **Code Group** is a named, reusable, cross-policy set of billing codes (HCPCS Level II, CPT Level I, ICD-10-CM) that generalizes a collection of codes under one queryable term, so a query can name the group instead of listing code strings. Group individuals are in the `gemi:` namespace and live in **`GEM_code_group_instances.ttl`** — a separate canonical file added at S103, parsed into the audit/validation graph but **not** part of the `GEM_policy_instances.ttl` triple count. Introduced 2026-06-30 (Session 103); first instance `gemi:codeGroupRAD` (Respiratory Assist Devices, HCPCS E0470-E0472, identifying `gemi:conceptRespiratoryAssistDevice`, owner "CMS", `dc:source gemi:ncd240.9`).

**Membership — two forms, used singly or together.**
- *Enumerated curated core:* `skos:narrower` to each member code IRI. Used for arbitrary sets with no code-prefix pattern (e.g. RADs = E0470-E0472, or an ad-hoc analysis set). This is the project's first committed use of `skos:narrower`.
- *Pattern groups:* `gem:memberCodePattern` — a single regular-expression string matched against code IRIs — for prefix-defined structural groups such as the HCPCS Level II letter categories, so the node stays a handful of triples instead of enumerating thousands. Declared 2026-06-30 (Session 104) as an `owl:DatatypeProperty` (domain `gem:CodeGroup`, range `xsd:string`); the same session minted all 17 HCPCS Level II letter categories (A, B, C, E, G, H, J, K, L, M, P, Q, R, S, T, U, V) as pattern-only groups (`gemi:codeGroupHCPCS…`, owner "CMS", no `dc:source`, no concept link), each carrying one anchored full-IRI regex over the HCPCS namespace. A group may carry both a curated core and a pattern.

**Concept link.** `gem:identifiesClinicalConcept` records that a group represents / is identified by a clinical concept (0..N; a group may identify none). It is semantically identical to `gem:refersToClinicalConcept` (presence only, no coverage polarity); it is held as a distinct predicate solely to physically separate group->concept links from policy->concept links, so each population can be queried independently.

**Owner.** `gem:codeGroupOwner` names the responsible party as a string literal; `rdfs:subPropertyOf dcterms:rightsHolder`. Note: `rightsHolder` is a DC **Terms** property, so a `dcterms:` prefix (`http://purl.org/dc/terms/`) was added to the ontology at S103 — it is **not** in DC Elements 1.1. CMS-policy-derived groups carry `"CMS"`.

**Overlap & contrast.** Groups may overlap (a code may belong to several groups); no disjointness is asserted. Contrast `gem:PolicyGroup` (policy-specific, not shared across policies) and `gem:ICDgrouping` (ranges within the ICD code system's own hierarchy).

**Deferred (S103):** HCPCS modifiers and ICD code-pair groupings are not yet admitted as members. **Resolved (S104):** the direct policy->CodeGroup predicate (`gem:refersToCodeGroup`) and the automated policy->group linking pass are implemented — see *Policy-to-group linking* below; `deferred_proposals[88]` is `complete`.

#### Reference SPARQL (kept for later use)

*Motivating query — policies that refer to clinical concepts identified by a group:*
```
PREFIX gem:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/>
PREFIX gemi: <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/>
SELECT DISTINCT ?policy WHERE {
  gemi:codeGroupRAD gem:identifiesClinicalConcept ?concept .
  ?policy           gem:refersToClinicalConcept   ?concept .
}
```

*Member resolution — curated core + pattern (now that `gem:memberCodePattern` is declared, resolves both enumerated `skos:narrower` members and pattern-defined members):*
```
PREFIX gem:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/>
PREFIX gemi: <http://www.cms.hhs.gov/ontology/2026/07/GEM/instances/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT DISTINCT ?code WHERE {
  VALUES ?codeGroup { gemi:codeGroupRAD }
  { ?codeGroup skos:narrower ?code . }
  UNION
  {
    ?codeGroup gem:memberCodePattern ?pattern .
    ?code a ?codeType .
    FILTER( ?codeType IN ( gem:HCPCSprocedure, gem:CPTprocedure, gem:ICDdiagnosis ) )
    FILTER( REGEX( STR(?code), ?pattern ) )
  }
}
```

*Materialize pattern membership into the triplestore (CONSTRUCT; mirrors `gem_hcpcs_conversion.rq` — writes `skos:narrower` into the working graph, never into a canonical file):*
```
PREFIX gem:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
CONSTRUCT { ?codeGroup skos:narrower ?code . }
WHERE {
  ?codeGroup a gem:CodeGroup ; gem:memberCodePattern ?pattern .
  ?code a ?codeType .
  FILTER( ?codeType IN ( gem:HCPCSprocedure, gem:CPTprocedure, gem:ICDdiagnosis ) )
  FILTER( REGEX( STR(?code), ?pattern ) )
}
```

**Policy-to-group linking (`gem:refersToCodeGroup`).** Declared S104: an `owl:ObjectProperty`, `gem:CMSpolicy` -> `gem:CodeGroup`, 0..N, validated on `gem:CMSpolicyShape` (`sh:class gem:CodeGroup`, `sh:nodeKind sh:IRI`). A policy links to a group iff the policy references at least one HCPCS code that is a `skos:narrower` member of the group **or** matches its `gem:memberCodePattern`; the link is presence-only and polarity-agnostic (a code reached via `gem:coversProcedure` and one via `gem:excludesProcedure` both establish it), mirroring `gem:refersToClinicalConcept`. Because groups overlap (a curated group is a subset of its enclosing HCPCS letter category), one referenced code can produce several links. These links are a **derived, materialized** fact: recomputed by an idempotent linking pass and stored in `GEM_policy_instances.ttl` inside a single block delimited by an explicit marker pair — `# === BEGIN MATERIALIZED gem:refersToCodeGroup LINKS ===` and `# === END MATERIALIZED gem:refersToCodeGroup LINKS ===`. The block is the span **between** the two markers and holds nothing but link lines; it does **not** extend to EOF — hand-authored content sits both above the BEGIN marker and below the END marker, and the pass never touches it. The pass strips from the BEGIN marker through the END marker inclusive, recomputes from current policy code references intersected with current group membership, and re-emits the marker pair with the fresh links between them; it is re-run at session close whenever any policy's codes or any group's membership change (the three triggers). Two `gem_audit.py` checks guard it. `codegroup_link_drift` recomputes the expected set and flags YELLOW on any missing or obsolete link, so stored links cannot silently rot; `codegroup_block_extent` (S145) enforces the boundary — exactly one marker of each kind, in order, nothing but link lines inside the span, and no link statement outside it. (The marker pair replaced an extends-to-EOF claim at S145. That claim was false from S131, when 49 hand-authored transmittal/CR stubs were written below the links and so inside the span the documented strip-to-EOF procedure would have deleted; a second copy of the claim, on a banner orphaned ~1,100 lines up the file by successive policy insertions, swept in 11 policy sections as well. `codegroup_link_drift` guards the links' content against the graph and never reads the file's text, which is why the extent went unguarded from the block's introduction at S104 until S145.) S104 backfill: 45 links across 18 policies. S108 (2026-07-01) minted the first two non-letter-category code groups: `gemi:codeGroupDiabetes` (the project's first ICD-10-CM code group — a `gem:memberCodePattern` over `ICD10CM/E11`, type 2 diabetes mellitus) and `gemi:codeGroupOxygenEquipment` (the first range-defined pattern group — two HCPCS patterns spanning `E0400`–`E0493` and `E1300`–`E1499`). The oxygen-equipment group extended the materialized set to **56 links across 18 policies**; the diabetes group is ICD-10, so it contributes no materialized links (the `codegroup_link_drift` check is HCPCS-only).

*Recompute the policy->group links — the linking pass expressed as a CONSTRUCT (the reference implementation writes the result into the materialized block in `GEM_policy_instances.ttl`; it matches the HCPCS IRI shape directly, equivalent to the `?code a gem:HCPCSprocedure` typing that holds in the triplestore):*
```
PREFIX gem:  <http://www.cms.hhs.gov/ontology/2026/07/GEM/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
CONSTRUCT { ?policy gem:refersToCodeGroup ?codeGroup . }
WHERE {
  ?policy a ?ptype .
  FILTER( ?ptype IN ( gem:CMSpolicy, gem:NCDpolicy, gem:LCDpolicy,
                      gem:ArticlePolicy, gem:TransmittalPolicy,
                      gem:ProgramMemorandumPolicy ) )
  ?policy    ?refPred ?code .
  ?code      a gem:HCPCSprocedure .
  ?codeGroup a gem:CodeGroup .
  { ?codeGroup skos:narrower ?code . }
  UNION
  { ?codeGroup gem:memberCodePattern ?pattern .
    FILTER( REGEX( STR(?code), ?pattern ) ) }
}
```

---

### 2p. Healthcare setting class, hierarchy, and reference properties

| URI | Kind | prefLabel |
|-----|------|-----------|
| `gem:HealthcareSetting` | class, `rdfs:subClassOf skos:Concept` | "Healthcare Setting" |
| `gem:refersToHealthcareSetting` | object property, `gem:CMSpolicy` → `gem:HealthcareSetting` | "Refers to Healthcare Setting" |
| `gem:coversInHealthcareSetting` | object property, `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` → `gem:HealthcareSetting`; sub-property of `gem:refersToHealthcareSetting` | "Covers In Healthcare Setting" |
| `gem:exclusivelyCoversInHealthcareSetting` | object property, `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` → `gem:HealthcareSetting`; sub-property of `gem:coversInHealthcareSetting` | "Exclusively Covers In Healthcare Setting" |
| `gem:excludesHealthcareSetting` | object property, `gem:CMSpolicy` ∪ `gem:AnchoredCodingScope` → `gem:HealthcareSetting`; sub-property of `gem:refersToHealthcareSetting` | "Excludes Healthcare Setting" |
| `gem:excludedHealthcareSetting` | object property, `gem:CoverageExclusion` → `gem:HealthcareSetting` | "Excluded Healthcare Setting" |

A **Healthcare Setting** is the place of care — the physical or administrative site at which an item or service is furnished — as named in a policy's text (home, physician's office, outpatient hospital, clinic). Setting individuals are in the `gemi:` namespace, in `GEM_policy_instances.ttl`'s HEALTHCARE SETTING INDIVIDUALS section. **One individual per setting, reused across policies; one link per policy in which the setting appears.**

**Setting polarity (S197).** Coverage polarity is carried on the same binary rule as ICD-10 and HCPCS codes, and its subject is normally the `gem:PolicyRule` that makes the statement (domain `union(CMSpolicy, AnchoredCodingScope, PolicyRule)`). The policy's own `gem:refersToHealthcareSetting` presence link is independent and stays. The reason settings take polarity while `gem:refersToClinicalConcept` does not is claim-matchability: a claim carries a place of service (`gem:placeServiceCode`) and carries no clinical concept, so settings belong to the code model. Three sub-properties of `gem:refersToHealthcareSetting`:

| URI | Super-property | Tier | Meaning |
|-----|----------------|------|---------|
| `gem:refersToHealthcareSetting` | — (the neutral parent) | — | Presence: the setting appears in the policy's text. **Asserted directly on the policy**, and not generally reached by entailment from the polarity family below, whose subject is normally a `gem:PolicyRule` — a rule's statement is contained in its policy, not propagated to it. Where a polarity link carries a policy subject, entailment supplies this parent as normal. |
| `gem:coversInHealthcareSetting` | `gem:refersToHealthcareSetting` | 2 | The service is covered in this setting, or the setting is named with no denial attached to it. The default. |
| `gem:exclusivelyCoversInHealthcareSetting` | `gem:coversInHealthcareSetting` | 2 (closed list) | The named settings are the entire permitted set; the complement is excluded and is not materialized. Canonical shape: TN 2476's instruction to pay G0445 *only when* the place of service is Physician's Office, Outpatient Hospital, Independent Clinic, or State or local public health clinic. |
| `gem:excludesHealthcareSetting` | `gem:refersToHealthcareSetting` | 1 | The service is denied or excluded in this setting. Canonical shape: NCD 160.7.1's carve-out of electrical nerve stimulation furnished by a physician in the office, by a physical therapist, or by an outpatient clinic under §1862(a)(1). |

The denial must attach to the **place**. A negative sentence that merely names a setting does not make it excluded — NCD 280.8 denies home use of the air-fluidized bed under a list of circumstances, but the home is the covered locus there and the exclusion is conditional, so it stays Tier 2.

`gem:excludedHealthcareSetting` is **not** this mechanism and remains unused: it hangs off `gem:CoverageExclusion` in the deferred structured coverage-outcome layer of `deferred_proposals[72]`, whose attachment predicates have domain `gem:CoverageOutcome` and zero individuals, so nothing reaches a policy through it. The two predicates differ by one word and one is live; check the domain before asserting either.

**Hierarchy (work item [95], S152).** Setting-to-setting hierarchy is `skos:broader` **among the individuals** — e.g. `gemi:settingIndependentClinic skos:broader gemi:settingClinic`; `gemi:settingOutpatientHospital skos:broader gemi:settingHospital`. There are **no** granularity subclasses: the S117 `gem:ClinicSetting` subclass was retired at S152 (a class-per-setting duplicates each singleton at two levels, and `gem:refersToHealthcareSetting`'s range requires individuals). To retrieve a setting family, follow `skos:broader` inbound from the parent individual. This contrasts with `gem:ClinicalConcept`, which remains flat (its hierarchy pass is deferred); the settings rule is the precedent for that future work.

**Labels and URIs.** `gem:prefLabel` is the bare place phrase — qualifier-first, no parentheses, never the word "setting" ("clinic", "outpatient hospital", "physician's office", "anywhere"). The URI is `setting` + UpperCamelCase(prefLabel), punctuation dropped (`gemi:settingPhysiciansOffice`). See §5's naming table. `gemi:settingAnywhere` is the reserved member for affirmative "performable anywhere" statements only — never attached on policy silence about setting.

**Renames (S152):** `settingClinicUnspecified` → `settingClinic`; `settingUnspecified` → `settingAnywhere`; `settingPhysicianOffice` → `settingPhysiciansOffice`.

## 3. HCPCS Modeling

The BioPortal UMLS HCPCS ontology (`HCPCS.ttl`, version `2025aa`) has been **integrated into GEM**. HCPCS procedure/item codes and modifiers — originally `owl:Class` definitions in the BioPortal source — were converted to **individuals** of new GEM classes, mirroring the earlier ICD-10 conversion (see §6).

**Established HCPCS classes** (in `GEM_ontology.ttl`):

| Class | Members |
|-------|---------|
| `gem:HCPCScode` | Superclass of all real HCPCS codes (procedure/item codes and modifiers). |
| `gem:HCPCSprocedure` | HCPCS procedure / item codes — five-character local names, e.g. `hcpcs:E1390`. |
| `gem:HCPCSmodifier` | HCPCS modifiers — two-character local names, e.g. `hcpcs:KX`. |

Each carries a SHACL node shape (`gem:HCPCSprocedureShape`, `gem:HCPCSmodifierShape`, `gem:HCPCScodeShape`) validating the IRI pattern.

**Consequences for extraction:**
- HCPCS references link to `hcpcs:` IRIs that are now **typed individuals** of `gem:HCPCSprocedure` / `gem:HCPCSmodifier` — parallel to how ICD-10 codes are individuals of `gem:ICDdiagnosis`.
- IRI local names are clean — **no dot** (unlike ICD-10): `hcpcs:E1390`, `hcpcs:A4575`, `hcpcs:KX`, `hcpcs:N1`.
- Because the modifier/procedure distinction is now an explicit `rdf:type`, **SHACL enforces it**: `gem:refersToHCPCSmodifier` has range `gem:HCPCSmodifier` and `gem:refersToHCPCSprocedure` (and its sub-properties `gem:coversProcedure`, `gem:excludesProcedure`, `gem:requiresProcedure`) have range `gem:HCPCSprocedure`, so a modifier predicate pointing at a procedure code, or vice versa, is a validation error. This is a real guarantee, not skill-level discipline.
- The skill still relies on the **policy's own labeling** to decide whether a code is used as a procedure/item or a modifier (policies have an explicit "MODIFIERS" coding subsection); the SHACL range check then confirms the chosen predicate matches the code's type.

---

## 4. GEM Conventions (match exactly)

Derived from `GEM_ontology.ttl`. Every new term and every instance must follow these.

**Annotations — required on every new term and individual:**
- `gem:prefLabel` — human-readable name.
- `gem:description` — explanation. For classes/properties, define scope/meaning. For instances, describe the entity.
- `gem:memberOfOntology gem:gemOntology` — always; **second-to-last** predicate.

**Properties also require:** `rdfs:domain` and `rdfs:range`.
**Classes also require:** `rdfs:subClassOf` (except top-level).
**Classes may also carry:** `gem:isaPrimaryClass true` — an optional flag marking the class as one of the ontology's primary / heavily-used classes. Asserted only when `true`; never asserted with value `false` on non-primary classes.

**Predicate ordering within a definition** (omit any that don't apply; full version with worked rationale in `gem_turtle_style_guide.md`):
1. `rdf:type` (`a`)
2. `rdfs:subClassOf` / `rdfs:subPropertyOf` (if applicable)
3. naming — `gem:identifier`, `gem:prefLabel`, `skos:altLabel`
4. descriptive annotations — `gem:shortDescription` (if present), `gem:description`, then any `gem:llm*` enrichment annotations (alphabetical)
5. structural metadata — `rdfs:domain`, `rdfs:range` (properties); `gem:isaPrimaryClass` (classes, only when `true`)
6. domain data-properties (instances) — dates, identifiers, etc.
7. relationship / object properties — `gem:referencesPolicy`, `gem:refersTo…`, etc.
8. `gem:memberOfOntology` (second-to-last)
9. `dc:source` (last), where used

**Naming:**
- Classes: `gem:UpperCamelCase` (e.g., `gem:ProviderCredential`).
- Properties: `gem:lowerCamelCase` (e.g., `gem:referencesPolicy`).
- Instances: `gemi:lowerCamelCase` in the instance namespace — all instance local names are camelCase, with no underscores (exception: anchored coding scope instances — `gem:PolicyGroup` and `gem:PolicyCodingRule` — use an underscore as a structural separator between the parent-policy local name and the scope-identifier portion; see §2j and §5). Initialisms stay uppercase mid-name (`conceptPO2`, `conceptPPulmonaleOnEKG`). Policy-URI style: `gemi:ncd240.2`, `gemi:lcd33797`, `gemi:a52514` — a period is preserved only where the real-world identifier has one (NCD manual-section numbers, mirroring the ICD-10 dot convention); LCD and Article IDs carry no period. Credential individuals: `gemi:credential…`. Clinical concepts: `gemi:concept…` (e.g. `gemi:conceptHomeOxygen`). Qualification groups: `gemi:groupI`, `gemi:groupII`, etc.
- Parenthetical handling in URIs: include the parenthetical only when it matches the qualifier pattern (first character lowercase a–z, content limited to lowercase letters, spaces, commas, and hyphens); drop otherwise (acronym, eponym, marker patterns). The `gem:prefLabel` always retains the parenthetical verbatim. See SKILL.md §GEM Mapping for the decision rule and worked examples.
- External codes: keep the source IRI exactly — `icd10:J96.11` (dot preserved), `hcpcs:E1390` (no dot).

**Term identity by meaning, not format:** when deciding whether a candidate term is genuinely new, judge it by what it *means*, not by whether an existing name happens to match its datatype or shape. Two `xsd:date` properties are not the same property if they denote different things (e.g. a policy's effective date is not a claim service-line date).

**Formatting:**
- `GEM_ontology.ttl` and `GEM_policy_instances.ttl`: CRLF line endings — **every** line ends `\r\n`, with **zero lone-LF** endings; **spaces only** for indentation — no tabs. A lone-LF ending parses as valid Turtle but violates the format rule and has slipped in before (a 22-line regression was found and repaired); the Turn-2 validation explicitly counts lone-LF endings and the file must end with `.\r\n`.
- Every TTL definition terminates with `.` — never a dangling `;`.
- Comment headers (`#`) delimit sections.
- Companion skill files (`SKILL.md`, `worklist_schema.md`, this file) are Markdown and use LF line endings.

**Annotation labels:** GEM uses `gem:prefLabel` and `gem:description`, **not** `rdfs:label`/`rdfs:comment` — for GEM-namespace terms and `gemi:` individuals. The one exception in practice: cited related documents that are *not* GEM-modeled policies (NCAs, Transmittals, draft LCDs) are minted as `owl:NamedIndividual` and carry `rdfs:label`/`rdfs:comment`, since they are reference pointers rather than first-class GEM entities.

**Optional enrichment annotations** (defined in `GEM_ontology.ttl`, never required, listed in §1a): `gem:shortDescription`, `gem:llmDetailedDefinition`, `gem:llmCardinalityNote`, `gem:llmEnumeratedValues`, `gem:llmInverseNote`, `gem:llmScopingNote`, `gem:llmTraversalHint`. Add to a new term only if it genuinely benefits from the extra context. When `gem:shortDescription` and `gem:description` both appear on a term, place `gem:shortDescription` **before** `gem:description`. See `gem_turtle_style_guide.md` ("Optional Schema-Term Enrichment") for per-annotation guidance.

---

## 5. Instance Namespace and Stubs

Policy instances and minted individuals live in `GEM_policy_instances.ttl` under the `gemi:` namespace. Schema terms never appear in the instances file; instance data never appears in `GEM_ontology.ttl`.

A **cited-policy stub** is a minimal `gemi:` individual created so a `gem:referencesPolicy` triple has an object before the cited policy is processed. A stub carries identifier, label, and source URL; it is **populated in place** (description rewritten, extracted triples added) when its own extraction pass runs — never re-created as a duplicate. Every minted policy document is typed to a `gem:CMSpolicy` subclass — NCDs/LCDs/Articles, and equally NCAs (`gem:NCAdocument`), Transmittals (`gem:TransmittalPolicy`) and Program Memoranda (`gem:ProgramMemorandumPolicy`). The untyped-`owl:NamedIndividual` pointer form was retired at S41 (Tom: *"a transmittal is a policy document which should be realized from the full document, not just a reference"*) and its last trace generalized away by the S131 mint-every-referenced-policy rule; no untyped policy pointers remain in the graph. Draft LCDs have no instances — `gemi:dl<id>` is a reserved scheme.

### Instance URI naming schemes

Every minted `gemi:` individual follows a fixed scheme. The general rule (§4) is camelCase with no underscores; the schemes below are the established patterns for each kind of individual. A period is preserved only where the real-world identifier has one.

| Kind | Scheme | Examples |
|------|--------|----------|
| NCD policy / stub | `gemi:ncd<section>` — manual-section number, periods preserved | `gemi:ncd240.2`, `gemi:ncd240.4.1`, `gemi:ncd310.1` |
| LCD policy / stub | `gemi:lcd<id>` — LCD numeric id, no period | `gemi:lcd33797`, `gemi:lcd33718` |
| Article policy / stub | `gemi:a<id>` — Article numeric id, no period | `gemi:a52514`, `gemi:a52466` |
| Transmittal | `gemi:tn<NN><MANUAL>` — transmittal number + the manual token (**mandatory**; see §5.2) | `gemi:tn96NCD`, `gemi:tn961CP`, `gemi:tn144CIM`, `gemi:tn1194OTN` |
| National Coverage Analysis (NCA/CAL) | `gemi:cag<id>` — CAG number, **hyphen removed**, trailing revision letters kept **with their source casing** (`N`/`R`, uppercase as CMS writes them). Equivalently: the local name is `cag` + the individual's own `gem:identifier` minus `CAG-` — which is what the `nca_uri_derivation` audit check enforces. | `gemi:cag00296N`, `gemi:cag00296R2`, `gemi:cag00465N` |
| Draft LCD | `gemi:dl<id>` — `DL` identifier, no period | *reserved; no instances in the graph* |
| Credential | `gemi:credential<Name>` | `gemi:credentialTreatingPractitioner` |
| Clinical concept | `gemi:concept<Name>` | `gemi:conceptHomeOxygen`, `gemi:conceptPO2` |
| Qualification group | `gemi:group<RomanNumeral>` | `gemi:groupI`, `gemi:groupII` |
| Healthcare setting | `gemi:setting<Place>` — `setting` + UpperCamelCase(prefLabel), punctuation dropped; prefLabel is the bare place phrase (qualifier-first, no parentheses, never the word "setting"); hierarchy via `skos:broader` among individuals (§2p) | `gemi:settingHome`, `gemi:settingClinic`, `gemi:settingPhysiciansOffice`, `gemi:settingAnywhere` |
| Policy Group | `gemi:<policyLocalName>_group<N>` — policy local-name + underscore + Group number per source | `gemi:a52466_group1`, `gemi:a52466_group16`, `gemi:a52510_group1` |
| Policy Coding Rule | `gemi:<policyLocalName>_<anchorCode>CodingRule` — policy local-name + underscore + lowercase HCPCS anchor + `CodingRule` suffix (single-anchor form; multi-anchor TBD at first occurrence) | `gemi:a52519_a7047CodingRule` |

**Deleted-section variant:** any NCD/LCD/Article URI may be suffixed with `_DELETED` (e.g. `gemi:ncd270.1.1_DELETED`) when the policy was deleted by a transmittal. The suffix is the second documented exception to §4's "no underscores" rule (alongside Policy Groups and Policy Coding Rules — both subclasses of `gem:AnchoredCodingScope`). See §5.3 for the rationale and worked examples.

The transmittal `<MANUAL>` token names the CMS manual the transmittal belongs to, and pairs one-to-one with the individual's `gem:publicationNumber` (§5.2's table). The `rdfs:label` states the manual in words ("TN 96 (NCD)", "TN 961 (Medicare Claims Processing)"). The CAG hyphen is dropped because `gemi:` local names are camelCase with no punctuation except the NCD section period.

Policy Group URIs and Policy Coding Rule URIs — the two subclasses of `gem:AnchoredCodingScope` — are the first documented exception to the §4 "no underscores" rule for instance local names. An anchored coding scope is policy-specific — its identity is *parent-policy + scope-identifier*, not a stand-alone concept — and the underscore is a structural separator that distinguishes the policy-local-name portion from the scope-identifier portion. The general camelCase convention would produce ambiguous URIs for policies whose local name itself contains digits (e.g., `gemi:a52466group1` is harder to read and unparseable into its parts; `gemi:ncd240.2group1` is worse; `gemi:a52519a7047CodingRule` similarly cannot be cleanly split). The underscore is therefore deliberate. The second documented exception is the `_DELETED` suffix on deleted-section stubs — see §5.3.

### URI uniqueness and the manual-token rule

The general URI-uniqueness rule for any minted `gemi:` individual: a bare URI is used when the real-world identifier is *itself* unique; a disambiguating token is added when it is not. The token is then part of identity, not decoration.

**Transmittals never satisfy the antecedent.** A transmittal number is unique only *within* one CMS manual — the CIM (HCFA Pub. 6) ran 1–169 to early 2003; Pub. 100-03 and Pub. 100-04 each restart at 1 and run past 13,000. A bare `gemi:tn<NN>` therefore asserts a uniqueness that does not exist, and the manual token is **mandatory** on every `gem:TransmittalPolicy` URI.

The collision is real, not hypothetical: **TN 78 is two documents.** The graph's `gemi:tn78CIM` is the Coverage Issues Manual's Transmittal 78 (1995, TENS, cited by NCD 160.7); Pub. 100-03's own Transmittal 78 is an unrelated document (5 Dec 2007, CR 5834, Pulmonary Rehabilitation Services, adding §240.8) — verified by fetch at S148. Until S148 the corpus held the first at a bare `gemi:tn78` carrying the second's rendition URL. That defect is what this rule exists to prevent. The corpus holds no colliding *pair* today, so the token is pre-emptive — and S148 is the evidence that pre-emption is warranted.

**Manual tokens and their publication numbers.** The token and `gem:publicationNumber` are one fact recorded twice; the audit's `transmittal_manual_token` check enforces the biconditional, so neither can drift from the other silently.

| token | manual | `gem:publicationNumber` | extent |
|-------|--------|-------------------------|--------|
| `CIM` | Coverage Issues Manual (HCFA Pub. 6) | `"6"` | TN 1–169, through early 2003 |
| `BP` | Medicare Benefit Policy Manual (Pub. 100-02) | `"100-02"` | 2003 onward |
| `NCD` | NCD Manual (Pub. 100-03) | `"100-03"` | 2003 onward |
| `CP` | Medicare Claims Processing Manual (Pub. 100-04) | `"100-04"` | 2003 onward |
| `OTN` | One-Time Notification (Pub. 100-20) | `"100-20"` | 2003 onward |
| `MHM` | Medicare Hospital Manual (HCFA Pub. 10) | `"10"` | predecessor claims manual, through early 2003 |
| `MIM` | Medicare Intermediary Manual (HCFA Pub. 13) | `"13"` | predecessor claims manual, through early 2003 |
| `MCM` | Medicare Carriers Manual (HCFA Pub. 14) | `"14"` | predecessor claims manual, through early 2003 |
| `HHA` | Home Health Agency Manual (HCFA Pub. 11) | `"11"` | predecessor program manual, through early 2003 |

A new token is introduced only for a genuinely new CMS manual, and enters this table with its publication number in the same edit.

**The era gate — a disqualifier that outranks every source below.** Pub. 100-03, 100-04 and 100-20 did not exist before 2003, and the CIM ended at TN 169 in early 2003. Therefore a transmittal dated before 2003 **cannot** carry `NCD`/`CP`/`OTN`, and one numbered above 169 **cannot** carry `CIM`. (Boundary corrected 167→168 at S177, then 168→169 at S247: TN 169's rendition R169CIM.pdf — the 04/2003 crystallization-boundary transmittal that removed the age limitation on stem-cell-transplantation coverage for multiple myeloma, NCD 110.23 — was supplied by Tom, so the CIM reached TN 169 and just into 2003; the number half of the gate is authoritative, the date half is advisory.)

The gate **disqualifies; it does not assign.** A pre-2003 *coverage* transmittal is CIM, but a pre-2003 *claims* transmittal belongs to the predecessor Carriers/Intermediary manuals rather than the CIM — so a positive CIM assignment still needs corroboration (a verified rendition, the MCD's Coverage Transmittal Link, or a fit in the CIM's monotonic dated series). The predecessor claims manuals now carry their own tokens — `MHM` (Medicare Hospital Manual, HCFA Pub. 10), `MIM` (Medicare Intermediary Manual, HCFA Pub. 13), and `MCM` (Medicare Carriers Manual, HCFA Pub. 14), introduced S234 at NCD 230.9, plus `HHA` (Home Health Agency Manual, HCFA Pub. 11), introduced S243 at NCD 40.1 — so a pre-2003 *claims* or predecessor-program transmittal named under a specific predecessor manual takes that manual's token rather than being disqualified into a bare URI. Every transmittal defect the corpus has produced was found by this gate and shares one shape — **right number, wrong manual**: `tn78` (a 1995 document described as Pub. 100-03), `tn144` (2001, described as a "Pub. 100-3 NCD Coverage Issuance Manual" that does not exist, with a URL resolving to Pub. 100-04 TN 144 of 2004), and `tn36` (05/1989 described as Pub. 100-03, while moving text out of CIM §60-9).

**Token-source priority — highest available source wins:**
1. **A verified rendition filename.** CMS's own machine identifier in the filename — `…r11263CP.pdf` → `CP`, `…R13374NCD.pdf` → `NCD`, `…R144CIM.pdf` → `CIM` — outranks everything else, **provided the rendition is verified**: supplied by the user, fetched, or read from the MCD's per-version *Coverage Transmittal Link*. A filename **constructed by analogy is not evidence** and does not enter this list at all — `tn78`'s `r78ncd.pdf` was exactly that, and it named a real but different document.
2. **The document's own stated manual**, when no verified rendition filename exists.
3. **The citing context** — the section heading a document is cited under — is a **last resort only**.

The `tn13374` episode is the worked example of why (1) outranks (3): the source filename `R13374NCD.pdf` correctly said `NCD`, but the transmittal was cited under a section heading literally titled "Claims Processing Instructions", and reading the token off that heading (priority 3) produced the wrong `CP`. The filename was right; the heading-derived label was wrong. The correction restored `gemi:tn13374NCD`.

**When no source determines the manual,** the URI is minted bare and the state is *declared*, never silent: the individual carries **no** `gem:publicationNumber`, its `gem:description` says **"Manual undetermined"**, and it joins the reference-stub backlog until resolved — the same posture as "Source URL pending". **A bare transmittal URI means *unresolved*, never *fine*.** The audit reads an *undeclared* bare URI as a finding. This is the rule's load-bearing clause: the pre-S149 wording ("a bare URI is used when the identifier is already unique") made bare the resting state, and 61 of the corpus's 85 transmittals accumulated there, each one unremarkable at mint. The graph holds zero bare transmittal URIs as of S149.

**When sources conflict,** the priority order resolves the URI, **and** the conflict is recorded in the individual's `gem:description` so the resolution is auditable.

### 5.3 The `_DELETED` URI suffix — preserving the standard URI for identifier reuse

When a transmittal deletes a coverage policy (NCD/LCD/Article section) entirely, the deleted policy is minted as a stub with the URI form `gemi:ncd<section>_DELETED` (analogously for LCDs and Articles). The standard URI `gemi:ncd<section>` is **deliberately left unreserved** so it remains available for any future case where CMS reuses the same section identifier for a different policy.

**Why this matters — the §20.8.3 motivation.** CMS does reuse section identifiers across policy lifetimes. NCD §20.8.3 was deleted by TN 48 (effective 2006-06-19); the same identifier was later reused by CMS for an unrelated 2013 policy. If the deleted §20.8.3 policy occupied `gemi:ncd20.8.3`, the later 2013 policy would have nowhere clean to land — either we'd silently overwrite (losing the deleted-policy stub) or use a contrived alternative URI (breaking the standard pattern). The `_DELETED` suffix avoids both problems: the deleted policy lives at `gemi:ncd20.8.3_DELETED`, and the standard URI `gemi:ncd20.8.3` is available when (and if) the 2013 policy is extracted.

**The underscore is the second documented exception to §4's "no underscores" rule** — alongside Policy Group and Policy Coding Rule URIs (see §5.1). It is a structural separator distinguishing the section-identifier portion from the `_DELETED` marker; the camelCase form (`gemi:ncd20.8.3DELETED`) would not parse cleanly.

**Five `_DELETED` stubs in the graph (as of S41), all minted during TN 48 formalization:**
- `gemi:ncd20.8.3_DELETED` — Policy originally at §20.8.3, deleted by TN 48. The standard URI `gemi:ncd20.8.3` stays unreserved (identifier-reuse case).
- `gemi:ncd150.4_DELETED` — Policy originally at §150.4, deleted by TN 48. (Duplicate bare mint consolidated into this stub at S146 — see below.)
- `gemi:ncd160.3_DELETED` — Policy originally at §160.3, deleted by TN 48. (Duplicate bare mint consolidated into this stub at S146 — see below.)
- `gemi:ncd160.11_DELETED` — Policy originally at §160.11, deleted by TN 48.
- `gemi:ncd270.1.1_DELETED` — Policy originally at §270.1.1, deleted by TN 48 with content "promulgated in section 270.1" per TN 48 prose.

The **conservative cross-reference principle** for `gem:referencesPolicy` links from `_DELETED` stubs lives in SKILL.md §Transmittals. Summary: only assert `gem:referencesPolicy` from a `_DELETED` stub to a surviving section if the transmittal's prose explicitly grounds the link. Currently asserted in the graph: `gemi:ncd270.1.1_DELETED gem:referencesPolicy gemi:ncd270.1` (1 triple total).

**The S114–S146 breach — the reservation consumed by the one policy it was not for.** The convention above says the bare URI stays free for a *different* future policy at the same identifier. Twice it was instead taken by the *same* policy as its retiree, and the breach stood undetected for 32 sessions.

NCD 160.13 (`Supplies Used in the Delivery of TENS and NMES`) is **Version 1, effective 1988-07-14**. Its cross-references name §150.4 and §160.3 — both of which TN 48 deleted in 2006, and both of which already existed in the graph as `gemi:ncd150.4_DELETED` and `gemi:ncd160.3_DELETED`. At **S114**, NCD 160.13's promotion minted those cross-references as fresh bare stubs at `gemi:ncd150.4` and `gemi:ncd160.3`, so each real-world document was asserted as two entities and each reservation was spent. At **S146** both bare stubs were deleted (8 + 7 triples), NCD 160.13's two `gem:referencesPolicy` links were retargeted to the retirees, and each bare stub's substantive finding was folded into its retiree's `gem:description` (−15 triples net). Both foldings paid off: §150.4's crosswalk finding (CIM 35-77 → NCD §160.12, NCDId=175) upgraded that retiree's §160.12 note from inference to external citation, and §160.3's trial-period finding corroborated its retiree's §160.7.1 note. Neither became a graph link — the conservative cross-reference principle governs regardless of how good the evidence gets, because it is TN 48's grounding that the rule asks for.

**Why nothing caught it.** The URI-collision pre-flight's forward audit asks whether the proposed URI is already taken. `gemi:ncd150.4` was **not** taken — that is the convention working exactly as designed. A pre-flight built to detect occupied URIs cannot detect a *reservation* being consumed, because a reservation looks identical to free space. `SKILL.md`'s pre-flight rule gained a **third direction** at S146 (retiree audit: check `gemi:<x>` against `gemi:<x>_DELETED` too), and `gem_audit.py` gained `deleted_twin_collision` (YELLOW, no autofix) as the after-the-fact guard.

**No automatic discriminator, deliberately.** A bare/`_DELETED` pair is either a duplicate mint or a genuine CMS identifier reuse, and the tempting automatic tell — label similarity — is the wrong one: it would have missed `gemi:ncd160.3`, the case that motivated the check. That bare stub's prefLabel was `Transcutaneous Electrical Nerve Stimulation (TENS) for Chronic Intractable Pain`, reconstructed from citing context and flagged unconfirmed at S114; its retiree's TN-48-grounded title is `Assessing Patients Suitability for Electrical Nerve Stimulation`. A similarity test reads that pair as two different policies — i.e. as legitimate reuse — and passes it. The check reports the pair and a human reads it.

**Known consequence — the first genuine reuse will need an allowlist.** When CMS's 2013 reuse of §20.8.3 is extracted, `gemi:ncd20.8.3` and `gemi:ncd20.8.3_DELETED` will both legitimately exist and `deleted_twin_collision` will fire YELLOW permanently, breaking the fully-GREEN bootstrap invariant. That is understood and accepted: there are **zero** such instances today (all five `_DELETED` stubs are lone retirees after S146), and building a suppression mechanism for a hypothetical shape is the failure mode this project already has a name for. Add the allowlist at the first real instance, not before.

(Convention established 2026-06-05, Session 41, during TN 48 formalization. Breach recorded and guarded 2026-07-15, Session 146.)

---

## 6. HCPCS Class-to-Instance Conversion — Done

The HCPCS class-to-instance conversion described as an open question in earlier versions of this file **has been carried out**. For the record:

ICD-10-CM codes — originally `owl:Class` definitions in the BioPortal source — were earlier converted to individuals of `gem:ICDdiagnosis`, with `gem:ICDgrouping` / `gem:ICDconcept` classes and the `gem:ICDdiagnosisShape` SHACL shape. The HCPCS ontology had the same shape of problem: codes and modifiers were `owl:Class` definitions distinguished only by `rdfs:subClassOf` lineage (modifiers descend from `hcpcs:MTHU000318`, the "HCPCS Modifiers" root; procedure/item codes descend from administrative `Level 1`–`Level 5` range groupings).

The conversion typed HCPCS codes and modifiers as individuals of `gem:HCPCScode` / `gem:HCPCSprocedure` / `gem:HCPCSmodifier` (see §3), via a SPARQL `INSERT` script (`gem_hcpcs_conversion.rq`) keyed off `MTHU000318` lineage and namespace scoping. Option (b) was chosen — real codes and modifiers are typed; the administrative `Level`-range groupings and the `rdfs:subClassOf` hierarchy are not carried over, since HCPCS hierarchy navigation is not needed for claim relevance. The modifier-vs-procedure distinction is now an explicit `rdf:type`, which the SHACL shapes enforce. HCPCS references are therefore links to typed `hcpcs:` individuals, exactly parallel to ICD-10.

---

## 7. Standing Schema Notes

### 7.1 Reasoning profile (platform assumption)

**GEM targets an OWL reasoner, not RDFS** (Tom, S148). The schema is authored in OWL and depends on entailments outside RDFS:

| construct | uses | RDFS? | notes |
|---|---|---|---|
| `rdfs:subClassOf`, `rdfs:subPropertyOf`, `rdfs:domain`, `rdfs:range` | many | yes | hold under any profile |
| `owl:inverseOf` | 4 pairs | **no** | `revisesPolicy`/`revisedByPolicy`, `transmitsChangeRequest`/`changeRequestTransmittedBy`. The never-assert-the-inverse convention (`SKILL.md` §Linking direction) rests on this. |
| `owl:unionOf` | 7 | **no** | domain/range unions |
| `owl:TransitiveProperty` | via SKOS | **no** | `skos:broaderTransitive` / `skos:narrowerTransitive` |

**SKOS semantics are the platform's responsibility.** A `@prefix skos:` declaration is lexical only — it binds a name and contributes no axioms. Neither GraphDB nor Stardog follows `owl:imports` automatically, and neither ships SKOS axioms with its rulesets. The graph database platform is expected to supply the reasoner and the standards-based vocabulary GEM authors against (Tom, S148); GEM does not localize foreign axioms.

**Authoring rule.** Assert only the direction the query writer starts from; the reasoner supplies the inverse and the transitive closure.

- `skos:broader` — asserted where the query writer knows the narrow term and asks for its parent (`cpt.ttl`: CPT code → heading).
- `skos:narrower` — asserted where the query writer knows the container and asks for its members (`GEM_code_group_instances.ttl`: code group → members).
- `skos:broaderTransitive` / `skos:narrowerTransitive` — **never authored.** They are entailed. Assert one only to state an ancestor link without claiming a direct parent; GEM has had no such case.
- Never assert both directions of the same pair. `cpt.ttl` currently does (18 `skos:broader` + the same 18 inverted as `skos:narrower`), an artifact of RDFS-era defensive authoring — see the worklist's cpt.ttl cleanup item.

No outstanding standing schema to-do. The earlier `gem:hasDiagnosis` / `gem:hasICDdiagnosis` inconsistency in `GEM_ontology.ttl` has been **resolved** by the user (the `gem:BaseServiceLineShape` `sh:path` and descriptions consistently use `gem:hasICDdiagnosis`).

New schema-extension candidates discovered during extraction are logged in the worklist's `deferred_proposals` list and reviewed at the checkpoint; when the user approves one, record the resulting term in §2 of this file and move it from the worklist to the established set.
