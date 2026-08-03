# policy_worklist.json — Schema and Maintenance Rules

The worklist is a persistent JSON file that accumulates across every policy processed. It is the project's memory of work discovered but not yet done. It holds **two active lists** — `related_policies` and `deferred_proposals`. A third list, `uncoded_clinical_concepts`, has been **retired** (see below); it is documented here only because worklists created before the retirement still carry its entries as a historical record.

Generate and update it via Python, never by hand-editing in a response.

---

## Top-Level Structure

```json
{
  "metadata": {
    "created": "2026-05-22",
    "last_updated": "2026-05-22",
    "policies_processed": 0,
    "checkpoint_cadence": 20
  },
  "related_policies": [],
  "uncoded_clinical_concepts": [],
  "deferred_proposals": []
}
```

The `uncoded_clinical_concepts` array is retained in the structure so that pre-retirement worklists remain valid, but **no new entries are added to it**. A worklist created after the retirement may carry an empty array and a `metadata.uncoded_clinical_concepts_status` string recording the retirement. The fix-uri rule below also applies: instance URIs use the `gemi:` namespace (e.g. `gemi:lcd33797`), not a bare `:` prefix.

`metadata.checkpoint_cadence` is the *recurring* review interval, not a target: a value of `20` means "review at every 20 policies processed," not "review once when `policies_processed` reaches 20." The recurring cadence was confirmed at the Session 40 checkpoint (when `policies_processed` was 21); the field was renamed from `checkpoint_at` at that time to make the semantics unambiguous.

---

## List 1 — `related_policies`

Policies discovered as references that may need their own extraction pass.

```json
{
  "identifier": "L33797",
  "uri": "gemi:lcd33797",
  "reference_type": "LCD",
  "status": "pending",
  "source_url": "https://www.cms.gov/medicare-coverage-database/view/lcd.aspx?lcdid=33797",
  "discovered_in": ["NCD 240.2"],
  "is_current": true,
  "note": ""
}
```

Field rules:
- `uri` — instance URI in the `gemi:` namespace. Extractable policy documents follow established patterns: `gemi:ncd<num>` (e.g. `gemi:ncd240.2`), `gemi:lcd<num>` (e.g. `gemi:lcd33797`), `gemi:a<num>` (e.g. `gemi:a52514`), `gemi:cag<id>` (e.g. `gemi:cag00313R`), `gemi:tn<num>` (e.g. `gemi:tn48NCD`), `gemi:cr<num>` (e.g. `gemi:cr8169`). For `reference_type: Other` Medicare Manual chapter references, the convention is `gemi:pub<pub#>_ch<chapter#>` (e.g. `gemi:pub100_02_ch13` for Medicare Benefit Policy Manual Ch 13, `gemi:pub100_04_ch20` for Medicare Claims Processing Manual Ch 20) — matching CMS's canonical Pub. 100-XX identification. Manual-chapter references are minted as `gem:CMSmanualChapter` graph stubs on first reference (S118, work item [69], reversing the prior no-stub direction); the minting Generate turn asks the user for the chapter's source URL. Like NCD/LCD/Article stubs, a Manual-chapter stub is removed from this worklist in the same Generate turn that mints it, and its extraction-pending state is tracked by `gem:nextPlannedStep` (`gem:planPromote` = awaiting extraction).
- `reference_type` — `NCD`, `LCD`, `Article`, `NCA`, `CAL`, `Transmittal`, `ProgramMemorandum`, `ChangeRequest`, or `Other`. NCD/LCD/Article are extractable policy documents; the others are recorded so the user can decide. **One exception:** a `Transmittal` that the transmittal-change rule has escalated (see "Transmittals That Introduce a Coverage-Policy Change" in `SKILL.md`) is also extractable — it keeps `reference_type: Transmittal`, is typed `gem:TransmittalPolicy` in the graph, and its `status` flips `pending → processed` when its extraction completes, exactly like an NCD/LCD/Article. `ProgramMemorandum` (added 2026-06-08, Session 45) is the pre-MAC predecessor of `Transmittal`; the same handling applies but the graph stub is typed `gem:ProgramMemorandumPolicy`. `ChangeRequest` (added 2026-06-26, Session 95) is the numbered CMS instruction work-item a transmittal delivers; when a transmittal being extracted delivers or cites a CR, the CR is minted directly as a `gem:ChangeRequest` stub in the graph (typed `gem:ChangeRequest`, `dc:source` = the delivering transmittal's IRI, linked via `gem:transmitsChangeRequest` or `gem:referencesChangeRequest`) rather than added here — so this `reference_type` is reserved for CRs *mentioned but not minted* (e.g. a CR named in narrative whose delivering transmittal is not yet known). **S131 update — mint-every-referenced-policy rule (see `SKILL.md` "Revision-history references"):** every `Transmittal` a policy references — header, claims-processing, or revision-history, and whether or not it introduces a coverage-policy change — is now minted directly as a `gem:TransmittalPolicy` stub (`gem:planPromote`) and linked via the citing policy's agnostic `gem:referencesPolicy`; the "escalated only when it introduces a change" gate above is superseded. Because the mint is direct-to-graph, such transmittals never land on this worklist. Their cited CRs are likewise minted directly (the S95 behavior). This `reference_type` value therefore now marks only transmittals *mentioned but not yet minted* (e.g. named in narrative whose identity isn't yet resolvable), paralleling the `ChangeRequest` reservation. **S191 update — the `ChangeRequest` reservation is likewise near-vacant.** Tom's S190 Q1 directed that a CR named in narrative with *no delivering transmittal* be minted directly as a `gem:ChangeRequest` stub (`planPromote`, Source-pending) and linked from the citing policy by `gem:referencesChangeRequest`, rather than held here — the same direct-to-graph treatment transmittals already had. The reservation therefore now covers only a CR whose **identifier** is not resolvable from the citing text, exactly paralleling the transmittal case above; a CR with a readable number is minted. The nine entries still carrying the pre-S191 wording (`NCD 90.2`, `NCD 210.3`, `NCD 20.33`, `CR 13278`, `CR 8197`, `CR 9087`, `CR 9631`, `CR 9861`, `CR 8206`) were minted and struck at S191, with the missing discoverer edges asserted on `gemi:ncd160.24` and `gemi:ncd270.1` so precondition (c) below was met before removal (the S152 `gemi:cr8109` precedent).
- `status` — `pending` (discovered, not processed), `processed` (extraction complete), or `deferred` (user chose to skip for now).
- `discovered_in` — list of policy identifiers that cited this one; append, never overwrite, when the same policy is cited again.
- `is_current` — `true` for the in-effect version, `false` for a historical/superseded version. **Historical versions go on this list with `is_current: false`; current policies are processed first.**
- **Dedup rule:** a policy identifier appears at most once. If already present, append to `discovered_in` and do not create a second entry.
- **§4f-surfaced entries:** an entry added under the reference-surfacing protocol (see SKILL.md "The 'reviewed, no action taken' outcome", item 5) carries the zero-outcome policy in its `discovered_in` even though no graph link to it exists from that policy — `discovered_in` records *where the reference came to the worklist's attention*, not the existence of a graph link. The entry's `note` field records the §4f provenance.
- **Status transitions and worklist scope:** `pending` → `processed` when its extraction completes. The worklist's scope is references **not yet minted as subjects in the graph**; once an entity is minted (even as a stub), the worklist entry is removed in the same Generate turn that performs the mint. The graph's `gem:nextPlannedStep` workflow-state property is the authoritative tracker of extraction-pending state for stubs (`gem:planPromote` = awaiting full extraction; `gem:planDone` = full extraction complete); the worklist does not duplicate this state. Categories that have no graph stub by convention — Change Requests and narrative-only references — remain on the worklist indefinitely as they have no graph entity to take over their tracking. (Medicare Manual chapters were formerly in this list; as of S118 / work item [69] they ARE minted as `gem:CMSmanualChapter` stubs and removed on mint.) Removal preconditions (carried over from S45 architecture revision): (a) the graph entity exists at the URI; (b) all worklist attributes are persisted in the graph — `source_url` as `dc:source`, content of `note` reflected in `gem:description` if material to identity; (c) for `discovered_in` provenance, all non-§4f discoverers have corresponding `gem:referencesPolicy` (or `gem:revisesPolicy`) triples in the graph. §4f-surfaced entries (those whose `discovered_in` contains a zero-outcome policy) stay on the worklist permanently — the §4f rule blocks the discoverer's outbound `gem:referencesPolicy`, so their provenance cannot fully migrate to the graph. **A worklist entry must NEVER be added in the same Generate turn that mints the entity as a stub in the graph — the mint goes directly to the graph; the worklist sees only the not-yet-minted backlog.** Never re-add an identifier already on the list or already in the graph. (Rule strict-form codified 2026-06-12, Session 50, after S50 observed 21-of-35 worklist entries were in-graph stubs.)

---

## Retired List — `uncoded_clinical_concepts`

**This list is retired.** It formerly held clinical concepts that appeared in policy prose with no code attached, awaiting human coding. Clinical concepts are now extracted directly into the graph as `gem:ClinicalConcept` individuals linked to the policy by `gem:refersToClinicalConcept` (see the "Clinical Concepts" section of `SKILL.md`); the set of those individuals and their links is itself the concept-review list, so a separate worklist list is no longer needed.

Retirement rules:
- **No new entries.** A Generate turn never appends to `uncoded_clinical_concepts`.
- **Existing entries are kept.** Worklists created before the retirement carry their `uncoded_clinical_concepts` entries unchanged — processed work is never deleted. They stand as a historical record.
- The retirement may be recorded in `metadata.uncoded_clinical_concepts_status`.
- The clinical concepts of any policy processed before the retirement (NCD 240.2, L33797) reach the graph only if that policy is re-processed for clinical concepts; until then their prose remains only in these historical entries.

---

## List 2 — `deferred_proposals`

Structured-data concept groups discovered in policies but intentionally **not modeled yet** (per first-policies scope discipline). Reviewed at the checkpoint.

```json
{
  "concept_group": "Clinical qualification thresholds",
  "first_seen_in": "NCD 240.2",
  "also_seen_in": ["L33797", "A52514"],
  "example": "An arterial PO2 at or below 55 mm Hg, or an arterial oxygen saturation at or below 88%, taken at rest.",
  "note": "Numeric coverage criteria (PO2, SpO2, hematocrit, LPM). Candidate for a future ClinicalThreshold concept group.",
  "status": "logged"
}
```

Field rules:
- `id` — **stable integer identifier**, the citation key every companion file uses (`deferred_proposals[NN]` in `SKILL.md`, `gem_rule_categories.md`, `gem_reference.md`, and handoffs). Added S161 (`deferred_proposals[101]`, option (a)) because the citation `[NN]` had been a hand-maintained pseudo-ID assumed to equal the array index, and the two had drifted (labels 0–95 equalled the index; a +1 offset entered when `[97]` was logged at S150, so labels 97+ are index+1 and label `[96]` is vacant). `id` pins each entry's citation label independent of its array position, so the array may be reordered freely and a write can key on `id` rather than on a neighbour's index. **Immutable once assigned.** A new entry takes the next-highest unused integer (never a reused or positional value). `gem_audit.py`'s `deferred_proposals_id` check enforces that every entry has a unique `id`, that every `status` (and `parts[].status`) is one of the seven valid values, and that every `deferred_proposals[NN]` cited in a companion file resolves to an entry.
- `concept_group` — short name for the kind of structured data (e.g., "Clinical qualification thresholds", "MAC jurisdictions", "Code-to-code coding constraints", "Qualification Groups I–IV").
- `first_seen_in` / `also_seen_in` — track recurrence; a group seen in 3+ policies is a strong candidate for promotion.
- `example` — one representative snippet.
- `status` — one value from two groups. **Build lifecycle** (the proposal will be / is being modeled), advancing `logged → approved → implemented → complete`: `logged` (discovered; pre-commitment — awaiting the decision on whether/how to model it), `approved` (committed and agreed in principle — in scope and intended for implementation; the specific modeling may still carry open design decisions; no extracted policy complies yet — the line separating `logged` from `approved` is *commitment*, not design finality), `implemented` (scaffolding exists and at least one — but not all — already-extracted policies have been transformed to comply), `complete` (all already-extracted policies / instance data comply and no backfill remains; new extractions comply by construction via standard extraction; reverts to `implemented` only if some extracted policy is later found non-compliant). **No-build outcomes** (terminal): `rejected` (out of scope), `resolved` (reviewed; in scope and the existing handling is already correct, so no schema change is needed -- distinct from `rejected` in that the pattern is in scope and the handling is right, not dismissed), `obsolete` (superseded / no longer relevant).
- `resolution` — *optional*, present only on `resolved` entries. A short note recording the date the resolution was made, the rationale, and any cross-reference to SKILL.md or other companion files where the confirming guidance lives. Resolved entries are retained as historical record (processed work is never deleted). Format: `Resolved YYYY-MM-DD, Session NN. <rationale>. <cross-reference>.`
- `parts` — *optional*. Used **only** when a single proposal bundles separable sub-solutions that are at genuinely different maturities; keep this rare. An array of `{ "name": <short label>, "status": <build-lifecycle value>, "note": <short note> }`. When `parts` is present, the entry's top-level `status` is the **roll-up** of its parts: `complete` iff every part is `complete`; otherwise `implemented` if any part has reached `implemented` or `complete`; otherwise `approved` if every part is at least `approved`; otherwise `logged`. The top-level value is stored (written), not computed at read time, and must be kept in sync with the parts whenever a part's status changes.
- **Dedup rule:** one entry per concept group. On re-encounter, append to `also_seen_in`; do not duplicate.

---

## Update Protocol (every Generate turn)

1. Load the existing worklist (or create the skeleton if first run).
2. For each newly discovered policy reference: if its identifier is new, add a `related_policies` entry with `status: pending`; if it exists, append to `discovered_in`.
3. Flip the just-processed policy's entry to `status: processed` (add the entry first if it was never listed).
4. Append or update `deferred_proposals`. **A newly appended entry is assigned the next-highest unused `id`** (an immutable integer citation key), never a positional or reused value; existing entries keep their `id`.
5. Update `metadata`: bump `policies_processed`, set `last_updated`.
6. Report the delta in the Verification Checkpoint: entries added, status changes.

Clinical concepts are **not** a worklist step — they are written to `GEM_policy_instances.ttl` as `gem:ClinicalConcept` individuals during the instances-generation step, not here.

The worklist is the single source of truth for what remains to be done. If a discovered reference is not written to the worklist, it is lost.
