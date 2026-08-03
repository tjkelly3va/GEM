# Plan-Turn Extraction Manifest Format

This is the companion file for `SKILL.md §Extraction Manifest Format`. It documents the full structured JSON schema produced during a policy's Plan turn. Consult both this file and the parent SKILL.md section at every Plan-turn manifest construction.

## Purpose

The manifest is a self-contained, machine-readable summary of everything extracted from a single policy. It is the artifact the user reviews and approves at the Plan turn; the Generate turn consumes it without re-reading the policy text. Generate via Python (it will often exceed `file_create` limits).

## Schema

```json
{
  "metadata": {
    "policy_identifier": "NCD 240.2",
    "policy_uri": "gemi:ncd240.2",
    "document_type": "NCD",
    "title": "Home Use of Oxygen",
    "version": "2",
    "policy_effective_date": "2021-09-27",
    "source_url": "https://www.cms.gov/medicare-coverage-database/view/ncd.aspx?NCDId=169",
    "reading_status": "complete",
    "extraction_date": "2026-05-22"
  },

  "proposed_schema_terms": [
    {
      "uri": "gem:SomeNewTerm",
      "term_kind": "class",
      "parent": "gem:CMSpolicy",
      "label": "Some New Term",
      "description": "...",
      "rationale": "Why no existing term fits — by meaning, not format."
    }
  ],

  "icd10_references": [
    {
      "code": "J96.11",
      "iri": "icd10:J96.11",
      "context_type": "table",
      "polarity": "non_covered",
      "governing_text": "ICD-10-CM Codes that DO NOT Support Medical Necessity — For all claims submitted with the N3 modifier.",
      "location": "Coding Information, Group 1"
    }
  ],

  "hcpcs_references": [
    {
      "code": "E1390",
      "iri": "hcpcs:E1390",
      "context_type": "table",
      "polarity": "neutral",
      "governing_text": "CPT/HCPCS Codes, Group 1. Group 1 Paragraph: 'The appearance of a code in this section does not necessarily indicate coverage.'",
      "location": "Coding Information, Group 1"
    }
  ],

  "modifier_references": [
    {
      "modifier": "KX",
      "iri": "hcpcs:KX",
      "context_type": "table",
      "governing_text": "...",
      "location": "Coding Information, HCPCS MODIFIERS"
    }
  ],

  "provider_credentials": [
    {
      "concept": "treating practitioner",
      "uri": "gemi:credentialTreatingPractitioner",
      "status": "reuse",
      "governing_text": "... ordered and evaluated by the treating practitioner."
    }
  ],

  "benefit_categories": [
    {
      "concept": "Durable Medical Equipment",
      "uri": "gemi:benefitCategoryDurableMedicalEquipment",
      "status": "reuse",
      "governing_text": "... covered under the Durable Medical Equipment benefit category."
    }
  ],

  "policy_references": [
    {
      "identifier": "L33797",
      "uri": "gemi:lcd33797",
      "reference_type": "LCD",
      "source_url": "https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?lcdid=33797",
      "governing_text": "..."
    },
    {
      "identifier": "TN 48",
      "uri": "gemi:tn48NCD",
      "reference_type": "Transmittal",
      "source_url": "https://www.cms.gov/Regulations-and-Guidance/Guidance/Transmittals/downloads/R48NCD.pdf",
      "governing_text": "Listed as current Transmittal Information in NCD 210.1.",
      "change_propagation_observation": {
        "affected_policies": ["NCD 210.1"],
        "status": "reflected",
        "basis": "NCD 210.1 current text shows Z12.5 in Group 1, matching TN 48's claimed addition.",
        "note": "Observation made during NCD 210.1's Plan turn; TN 48 not yet extracted at this time."
      }
    }
  ],

  "clinical_concepts": [
    {
      "label": "hypoxemia",
      "governing_text": "... when the patient exhibits hypoxemia as defined below.",
      "location": "B. Nationally Covered Indications, opening"
    }
  ],

  "rules": [
    {
      "id": "R1",
      "text": "Verbatim source text of the rule as a self-contained string.",
      "pdf_location": "Section name, paragraph/sentence reference",
      "pattern": "1 | 2 | 3 | 4 | 5 (per NCD 210.10 first-use conventions)",
      "rule_types": ["coverage-scope", "eligibility", "..."],
      "domain": "optional; only used for multi-domain policies",
      "verbatim_note": "Optional: notes on source typos, OCR corrections, sic-marked text"
    }
  ],

  "deferred_proposals": [
    {
      "concept_group": "Clinical qualification thresholds",
      "example": "An arterial PO2 at or below 55 mm Hg ...",
      "note": "Numeric coverage criteria. Logged for post-checkpoint review."
    }
  ],

  "verification": {
    "counts": {"icd10": 0, "hcpcs": 0, "modifiers": 0, "credentials": 0,
               "policy_references": 0, "clinical_concepts": 0, "rules": 0,
               "deferred_proposals": 0, "proposed_schema_terms": 0},
    "uncertainties": [],
    "self_check": {
      "every_table_code_extracted": true,
      "every_prose_code_extracted": true,
      "revision_history_excluded_from_links": true,
      "polarity_recorded_for_every_code": true,
      "document_complete_no_gates": true,
      "reading_complete": true
    }
  }
}
```

## Notes

- The manifest is generated via Python because policy size frequently exceeds `file_create` limits.
- There is no `gated_or_unconfirmed_sections` field. A gate halts the work before a manifest is produced (see SKILL.md "The Gate Hard-Stop Rule"); a manifest therefore only ever describes a complete document.
- The `verification.counts` values must be derived via `len(list)` against the manifest's own lists in the builder, never hardcoded as literals (see SKILL.md `manifest count drift` failure mode).
- **`change_propagation_observation`** is an optional field on `policy_references` entries, populated only when `reference_type == "Transmittal"`. It records the observation step required by §Transmittals in SKILL.md — whether the transmittal's claimed change has been folded into the current text of each affected policy. The field is structured as `{affected_policies: [<policy_identifier>...], status: "reflected" | "not_reflected" | "unverifiable" | "n/a", basis: "<free-text>", note: "<free-text>"}`. The `status` value is one of a closed list: `reflected` (affected policy's current text shows the change), `not_reflected` (current text does NOT show the change — the case where the transmittal carries operative-but-unmigrated guidance), `unverifiable` (verification not readily possible at this point), or `n/a` (citing policy is not one of the transmittal's affected policies). For multi-affected-policy transmittals, `status` and `basis` may be a per-policy dict when needed (typically only at the transmittal's own Plan turn). The observation does NOT gate extraction; it is a best-effort finding. At Generate, the observation is persisted in two places: appended as natural-language prose to the transmittal stub's `gem:workflowDescription` in `GEM_policy_instances.ttl`, and appended to the transmittal's worklist `note` field. No dedicated ontology property is minted for the observation — it reuses the existing `gem:workflowDescription` predicate. (Field introduced 2026-06-06, Session 42, per the §Transmittals methodology shift codified at S41–S42. **Persistence pointer moved `gem:description` → `gem:workflowDescription` at S166**, resolving `deferred_proposals[100]`'s fifth scope call; existing in-`gem:description` observations are migrated in that proposal's corpus sweep.)
- **`benefit_categories`** (introduced 2026-06-08, Session 45) is a manifest section listing the Medicare benefit categories the policy names explicitly in its text (e.g., "Durable Medical Equipment", "Diagnostic Laboratory Tests", "Physicians' Services"). Each entry carries `concept`, `uri` (under the `gemi:benefitCategory<Name>` URI pattern, lowercase-first), `status` (mint/reuse), and `governing_text` — the same shape as `provider_credentials`. At Generate, each entry yields a `gemi:<policy> gem:refersToBenefitCategory gemi:benefitCategory<Name>` triple. Reuse the controlled vocabulary across policies. Promoted to standard taxonomy at S45 (was previously per-policy, ad-hoc); see `SKILL.md` §Extraction Taxonomy.
- **`rules`** (introduced 2026-06-10, Session 48; documented here 2026-06-11, Session 49) is the manifest section holding evaluator-criterion rules captured as `gem:ruleDescription` strings on the policy. Each entry carries `id` (an `Rn` identifier scoped to the policy), `text` (strict-verbatim source string — the Patterns 1–5 conventions established at NCD 210.10's first use govern wording and decomposition choices), `pdf_location` (where the rule lives in the source), `pattern` (which of Patterns 1–5 was applied), `rule_types` (the axis-2 categorization values from `gem_rule_categories.md`), an optional `domain` (axis-1, used only for multi-domain policies per the register's single-domain convention), and an optional `verbatim_note` (source typos, sic-marked text, OCR corrections, or other source-fidelity flags). At Generate, each entry yields one `gemi:<policy> gem:ruleDescription "..."` triple. The same Generate turn typically also appends a categorized table to `gem_rule_categories.md` per the `rule_categorization_plan` field (see Reprocessing Manifests section below for that field; first-extraction manifests may carry it too).
- Provenance: this file was extracted from SKILL.md in Session 37 pass 7.5 as part of the size-mitigation work. The schema itself is unchanged from its prior SKILL.md form.

## Reprocessing Manifests

When a previously-extracted policy is reprocessed under a broadened methodology — applying methodology changes that didn't exist at the policy's first extraction — the manifest is structured as a **delta against the existing graph state**, not as a full re-extraction. The same JSON shape applies, with the additions below.

The delta-over-baseline shape is intentional: the Generate turn touches only what's changing. Existing graph content (codes, credentials, concept links, references, and the policy block's banner and description) is preserved unchanged unless the manifest's `reprocessing_delta.modified` block explicitly says otherwise.

### Metadata additions

- `metadata.reprocessing: true` — boolean flag distinguishing a reprocessing manifest from a first-extraction manifest. Absent or `false` for first extractions.
- `metadata.original_extraction: "YYYY-MM-DD (Session N)"` — when the policy was first extracted, so the methodology gaps to apply can be scoped.
- `metadata.reprocessing_scope: "<free text>"` — short prose summary of which methodology changes the reprocessing applies (e.g., "S48 broadened methodology: capture rule-description strings; verify clinical-concept completeness; banner-discipline check").
- `metadata.source_pdf: "<absolute path>"` — local path to the user-supplied canonical PDF. For reprocessing, the user-supplied PDF is the source of truth, preferred over the MCD HTML view (which carries CMS-wide boilerplate the canonical PDF does not — e.g., the "Reasons for Denial" disclaimer that appears identically on many NCD pages but is not part of the canonical document). The standard `metadata.source_url` field still holds the canonical CMS URL alongside.

### `reprocessing_delta`

A top-level dict summarizing what's preserved vs. what's added vs. what's being modified:

```json
"reprocessing_delta": {
  "preserved_unchanged": {
    "icd10_references": 0,
    "hcpcs_references": 1,
    "hcpcs_modifiers": 0,
    "provider_credentials": 2,
    "benefit_categories": 1,
    "policy_references": 4,
    "clinical_concepts": 34,
    "policy_metadata_triples": "all preserved"
  },
  "added": {
    "rule_descriptions": 16,
    "clinical_concepts": 1
  },
  "modified": {
    "description": false,
    "banner": "pending borderline B5"
  }
}
```

Counts come from the existing graph block at Plan time; the Generate turn verifies that preserved counts are unchanged after the edit (no existing triples accidentally affected).

### `existing_codes_and_actors`

Summarizes preserved entities with `status: "reuse"` markers. Each category mirrors its full-manifest shape but lightweight when the full details are already in the graph:

```json
"existing_codes_and_actors": {
  "hcpcs_references": [
    {"code": "E0652", "iri": "hcpcs:E0652", "polarity": "covered",
     "status": "reuse", "governing_text": "...", "location": "..."}
  ],
  "provider_credentials": [
    {"uri": "gemi:credentialPhysician", "status": "reuse"},
    {"uri": "gemi:credentialTreatingPhysician", "status": "reuse"}
  ],
  "benefit_categories": [
    {"uri": "gemi:benefitCategoryDurableMedicalEquipment", "status": "reuse"}
  ],
  "policy_references": [
    {"identifier": "TN 151", "uri": "gemi:tn151CIM",
     "reference_type": "Transmittal", "status": "reuse"}
  ]
}
```

The full-manifest top-level sections (`hcpcs_references`, `provider_credentials`, etc.) are NOT populated in a reprocessing manifest — they're rolled into `existing_codes_and_actors` instead. This avoids ambiguity about whether a top-level array entry is a new mint or a preserved entity.

### `clinical_concepts_added` (replaces `clinical_concepts`)

In a reprocessing manifest, the top-level `clinical_concepts` array is omitted; only the NEW concept individuals appear, in `clinical_concepts_added`. The pre-existing concept individuals are summarized in `reprocessing_delta.preserved_unchanged.clinical_concepts` (count only). Each entry has the same shape as a standard `clinical_concepts` entry plus `proposed_uri`, `status`, and optional borderline metadata:

```json
"clinical_concepts_added": [
  {
    "label": "congenital anomaly",
    "proposed_uri": "gemi:conceptCongenitalAnomaly",
    "status": "mint",
    "governing_text": "...",
    "location": "Lymphedema subsection, paragraph 1",
    "s43_normalization_note": "Source phrase is plural; singular-normalization applied per SKILL.md §Clinical Concepts."
  }
]
```

### `borderlines`

A top-level array of borderline decisions tracked through the conversational approval cycle. Per Core Principle #9, borderlines are surfaced one at a time in chat; this array is the structured record carrying both unresolved and resolved entries.

```json
"borderlines": [
  {
    "id": "B1",
    "topic": "<short topic name>",
    "status": "resolved | open",
    "decision": "<if resolved: what was decided and why>",
    "default": "<if open: what Claude will do absent direction>"
  }
]
```

The `borderlines` shape is also usable in first-extraction manifests; it was introduced in the reprocessing context but is not exclusive to it. NCD 210.10's nine borderlines at first-use (S48) predate this field; future first extractions should consider using it as the structured place for the borderlines the user resolves at approval.

### `rule_categorization_plan`

When the policy produces new `gem:ruleDescription` strings, the manifest carries a plan for the corresponding `gem_rule_categories.md` append:

```json
"rule_categorization_plan": {
  "target_file": "gem_rule_categories.md",
  "section_to_append": "### <Policy ID> — <Title>",
  "rule_count": 16,
  "domain_axis_note": "Single-domain policy; no domain column in the appended table.",
  "new_rule_type_values_added": [],
  "rule_types_used": ["coverage-scope", "credentialed-actor", "definition", "documentation", "eligibility", "service-definition", "service-standard"]
}
```

`new_rule_type_values_added` is empty when all rule-type categorizations use values already in the `gem_rule_categories.md` axis-2 vocabulary. A non-empty list signals that the vocabulary itself needs extension; those values must be added to the axis-2 list as part of the same Generate.

This field also belongs in a first-extraction manifest whenever the policy produces rule strings — it is not reprocessing-exclusive.

### `verification.preserved_counts`

Alongside the standard `verification.counts` (which tracks delta counts — entities being added), the reprocessing verification carries `preserved_counts` showing the pre-edit baseline of every category. Generate verifies that the post-edit preserved counts match the pre-edit ones (no existing triples accidentally affected).

```json
"verification": {
  "counts": {"rule_descriptions_added": 16, "clinical_concepts_added": 1, "...": "..."},
  "preserved_counts": {"icd10": 0, "hcpcs": 1, "credentials": 2, "clinical_concepts": 34, "...": "..."},
  "uncertainties": [...],
  "self_check": {...}
}
```

(Reprocessing-manifest format introduced 2026-06-11, Session 49, with NCD 280.6 as first-use.)

## Instance-Promotion Manifests

The instance-promotion manifest is the Plan-turn artifact used when migrating `gem:ruleDescription` triples on a `gem:CMSpolicy` individual to first-class `gem:PolicyRule` individuals — the Phase 3 / Phase 4 work tracked under `deferred_proposals[72]`. It is generated *before* any TTL edit, reviewed by the user, then drives the Generate turn that performs the migration.

Distinct from first-extraction and reprocessing manifests: this manifest does not introduce new codes, credentials, or clinical concepts. It restructures existing rule content. The pre-state's `gem:ruleDescription` count equals the post-state's `gem:PolicyRule` count; the migration is data-preserving by construction.

### Metadata additions

```json
"metadata": {
  "manifest_type": "instance_promotion",
  "policy_identifier": "NCD 210.10",
  "policy_uri": "gemi:ncd210.10",
  "migration_phase": "phase3",
  "preflight_verified": true,
  "session": "S73",
  "generated": "2026-06-21"
}
```

Field rules:
- `manifest_type` — fixed string `"instance_promotion"`, distinguishing this manifest from first-extraction and reprocessing manifests.
- `policy_identifier` / `policy_uri` — the policy whose rules are being promoted.
- `migration_phase` — `"phase3"` for `gem:CMSpolicy`-direct rules; `"phase4"` for `gem:AnchoredCodingScope`-attached rules (deferred per Decision 6 Part B).
- `preflight_verified` — boolean, set `true` only after the pre-flight URI collision audit confirms that none of the planned `gem:PolicyRule` URIs (`gemi:<policy>_r1`, `gemi:<policy>_r2`, ...) already exist in the graph.

### `migration_plan`

An array with one entry per rule being promoted. Entries are ordered by `source_order_index`. The array length must equal the policy's pre-migration `gem:ruleDescription` count.

```json
"migration_plan": [
  {
    "rn": 1,
    "source_order_index": 0,
    "new_uri": "gemi:ncd210.10_r1",
    "prefLabel": "NCD 210.10 R1",
    "domain": "screening",
    "rule_types": ["coverageScope", "eligibility"],
    "verbatim_preview": "Therefore, effective for claims with dates of service on or after..."
  },
  {
    "rn": 2,
    "source_order_index": 1,
    "new_uri": "gemi:ncd210.10_r2",
    "prefLabel": "NCD 210.10 R2",
    "domain": "screening",
    "rule_types": ["eligibility"],
    "verbatim_preview": "Screening for chlamydia and gonorrhea is covered when..."
  }
]
```

Field rules:
- `rn` — 1-indexed rule number. Per Decision 4, the `rn` value reflects source-document order: `r1` is the first rule encountered top-down in the policy.
- `source_order_index` — 0-indexed position in the source document (equals `rn - 1`). Carried redundantly so any downstream consumer can verify the ordering invariant by inspection.
- `new_uri` — the to-be-minted `gemi:` URI in the form `gemi:<policy-local-name>_r<n>`, per Decision 2.
- `prefLabel` — the `gem:prefLabel` literal in the form `"<policy identifier> R<n>"` (Decision 2 example: `"NCD 210.10 R1"`).
- `domain` — string value for `gem:ruleDomain` (e.g. `"screening"` → `gem:ruleDomain_screening`), or `null` if the policy is single-domain. Per Decision 6 Part B and the ontology's documented `gem:ruleDomain` semantics, single-domain policies legitimately omit this triple from every rule.
- `rule_types` — array of strings, each mapping to a `gem:RuleType` individual (e.g. `"coverageScope"` → `gem:ruleType_coverageScope`). Sourced from `gem_rule_categories.md`. Each rule carries at least one `gem:ruleType`; multiple are allowed when the rule's content spans multiple criterion categories.
- `verbatim_preview` — first ~80 characters of the `gem:ruleDescription` string, included for human review during the Plan turn. The full verbatim text is NOT carried in the manifest (the migration preserves it from the source graph; the preview only confirms the right rule is at the right position).

### `policy_edit_summary`

Describes the structural edit applied to the policy individual itself.

```json
"policy_edit_summary": {
  "predicate_slot": "after gem:isInEffect, before gem:memberOfOntology",
  "drop_count": 18,
  "add_count": 18,
  "drop_predicate": "gem:ruleDescription",
  "add_predicate": "gem:hasPolicyRule"
}
```

Field rules:
- `predicate_slot` — where the new `gem:hasPolicyRule` block sits in the policy individual's predicate ordering, per `gem_turtle_style_guide.md`'s canonical ordering rule.
- `drop_count` — number of `gem:ruleDescription` triples removed from the policy individual. Must equal `migration_plan.length`.
- `add_count` — number of `gem:hasPolicyRule` triples added to the policy individual. Must equal `drop_count` and `migration_plan.length`.

### `verification.counts`

```json
"verification": {
  "counts": {
    "pre_migration_ruleDescription_count": 18,
    "post_migration_ruleDescription_count": 0,
    "policyRule_individuals_minted": 18,
    "hasPolicyRule_triples_added": 18
  },
  ...
}
```

The four counts encode the migration's mass-conservation invariant:

```
pre_migration_ruleDescription_count
  == policyRule_individuals_minted
  == hasPolicyRule_triples_added
  == migration_plan.length
post_migration_ruleDescription_count == 0
```

### `verification.self_check`

Five audit-complementary attestations that the audit cannot verify on its own (each requires either pre-state comparison, source-document knowledge, or external-document judgment):

```json
"self_check": {
  "every_pre_migration_ruleDescription_migrated": true,
  "rn_numbering_matches_source_order_per_decision_4": true,
  "verbatim_ruleDescription_text_preserved_through_migration": true,
  "ruleType_assignments_sourced_from_gem_rule_categories_md": true,
  "prefLabel_format_per_decision_2_NCD_210_10_R1_style": true
}
```

Item rules:
- `every_pre_migration_ruleDescription_migrated` — every `gem:ruleDescription` triple that existed on the policy individual at pre-state has a corresponding `gem:PolicyRule` individual at post-state. Pre-state is sampled by Claude during the Plan turn; the audit only sees post-state.
- `rn_numbering_matches_source_order_per_decision_4` — `r1` corresponds to the first `gem:ruleDescription` encountered in the source TTL (top-down), `r2` to the second, etc. The audit doesn't read source TTL ordering.
- `verbatim_ruleDescription_text_preserved_through_migration` — the post-migration `gem:ruleDescription` string on each `gem:PolicyRule` is byte-identical to the pre-migration string on the policy. The audit doesn't have the pre-state to compare against.
- `ruleType_assignments_sourced_from_gem_rule_categories_md` — every `gem:ruleType` assignment on a `gem:PolicyRule` is drawn from the categorization table in `gem_rule_categories.md`, not invented at Generate time. The audit verifies presence but not categorization correctness.
- `prefLabel_format_per_decision_2_NCD_210_10_R1_style` — the `gem:prefLabel` literal exactly follows the Decision 2 format. The audit verifies presence but not the exact format.

### Worked example (3-rule synthetic policy)

```json
{
  "metadata": {
    "manifest_type": "instance_promotion",
    "policy_identifier": "EXAMPLE",
    "policy_uri": "gemi:example",
    "migration_phase": "phase3",
    "preflight_verified": true,
    "session": "S99",
    "generated": "2026-06-21"
  },
  "migration_plan": [
    {"rn": 1, "source_order_index": 0, "new_uri": "gemi:example_r1",
     "prefLabel": "EXAMPLE R1", "domain": null, "rule_types": ["coverageScope"],
     "verbatim_preview": "The service is covered when..."},
    {"rn": 2, "source_order_index": 1, "new_uri": "gemi:example_r2",
     "prefLabel": "EXAMPLE R2", "domain": null, "rule_types": ["frequency"],
     "verbatim_preview": "No more than one per calendar year..."},
    {"rn": 3, "source_order_index": 2, "new_uri": "gemi:example_r3",
     "prefLabel": "EXAMPLE R3", "domain": null, "rule_types": ["eligibility"],
     "verbatim_preview": "The beneficiary must have a documented..."}
  ],
  "policy_edit_summary": {
    "predicate_slot": "after gem:isInEffect, before gem:memberOfOntology",
    "drop_count": 3,
    "add_count": 3,
    "drop_predicate": "gem:ruleDescription",
    "add_predicate": "gem:hasPolicyRule"
  },
  "verification": {
    "counts": {
      "pre_migration_ruleDescription_count": 3,
      "post_migration_ruleDescription_count": 0,
      "policyRule_individuals_minted": 3,
      "hasPolicyRule_triples_added": 3
    },
    "self_check": {
      "every_pre_migration_ruleDescription_migrated": true,
      "rn_numbering_matches_source_order_per_decision_4": true,
      "verbatim_ruleDescription_text_preserved_through_migration": true,
      "ruleType_assignments_sourced_from_gem_rule_categories_md": true,
      "prefLabel_format_per_decision_2_NCD_210_10_R1_style": true
    }
  }
}
```

### Notes

- The manifest is generated via Python because larger policies (e.g. NCD 210.10 with 18 rules) may exceed `file_create` limits when the full plan is rendered.
- The manifest is a Plan-turn artifact only — reviewed and approved before any TTL edit. It is not a canonical file; it lives in `/home/claude/work/` or session scrollback.
- Post-Generate, the audit's Phase 3 check categories (three-state invariant, per-PolicyRule completeness, provenance reciprocity, controlled-vocab integrity) verify the structural correctness of the migration result; the manifest's `self_check` block records the attestation that the audit-blind aspects were honored.

(Instance-promotion-manifest format introduced 2026-06-20, Session 72 Cycle 0, in support of `deferred_proposals[72]` Phase 3 instance-promotion work.)
