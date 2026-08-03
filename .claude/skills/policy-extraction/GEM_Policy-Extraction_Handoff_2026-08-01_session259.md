# GEM Policy-Extraction Handoff — Session 259 (2026-08-01)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S259 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `646723062e55e457473f0f6e7a3cbd97` | 5575270 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `aee1d032d9b9175300fc4dc2964a9d09` | 272551 | **M** |
| `gem_reference.md` | `4ddd97d8b96dec2b4aff8e0318376c46` | 120152 |  |
| `gem_rule_categories.md` | `26b9e8184ed210db35d81c023bd91a83` | 1367326 | **M** |
| `gem_edit_log.md` | `8e7b26c10bc37a63d146cf986ba12785` | 87487 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `1983054a2c8a5601ed9cbaa2c624b74f` | 24849 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `6354d9e3b70868d259ca9e2f19167fed` | 322762 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `3f012027bb2d328e229042ed2e89b5d9` | 16002 |  |
| `gem_audit.py` | `88e760727453c69683eaf055cc2c36ef` | 306797 |  |

## §2 — Work completed in S259

**Extracted NCD 20.24 (Displacement Cardiography; ncdid=262)** — a fresh, single-version CIM-era diagnostic-test NCD (2 pp.), minted direct to the graph (never worklisted). Two-turn: Plan manifest with three borderlines (B1–B3), all Tom-confirmed at the lean, then Generate. Text-layer PDF, ungated, complete.

- **Version / dates.** Version 1, effective **1988-10-12**, posted directly in the Tracking Information block (a normal single-version NCD, **not** a longstanding-NCD Other-Versions-column read). V1 in hand → **not** a `policy_effective_date_v1` [107] candidate; INFO stays **24**. No implementation date stated. Pub. 100-3, section 20.24, pageCount 2. Benefit category: Diagnostic Tests (other) (reuse).
- **Rules (4; B1).** r1 `serviceDefinition` (Item/Service Description, captured whole — no HCPCS code carries the service identity, the NCD 110.22 R1 / 230.12 r1 shape); r2 `coverageScope` (cardiokymography covered for services on/after 10/12/1988); r3 `coverageScope`+`eligibility` (cardiokymography covered only as an adjunct to ECG stress testing + the male/female clinical indications, folded verbatim into the single Pattern-3 sentence); r4 `nonCoverage` (photokymography excluded). 5 `gem:ruleType` triples; no new axis-2 vocabulary. The r2/r3 split (vs one folded Pattern-3 rule → 3) is B1.
- **Concepts (8 links; 6 mints, 2 reuse).** Mints: `conceptDisplacementCardiography` (umbrella test), `conceptCardiokymography` (covered), `conceptPhotokymography` (non-covered, still linked — presence, not polarity), `conceptElectrocardiographicStressTesting`, `conceptAtypicalAnginaPectoris` (male indication), `conceptNonischemicChestPain` (male indication). Reuse: `conceptCoronaryArteryDisease`; and `conceptAngina` (**B2**) — the female indication. `gemi:conceptAngina` (prefLabel *"angina"*, minted S196 at NCD 190.15) already existed, so it is **reused on exact-prefLabel match**, not duplicate-minted. The Plan-turn reuse-search for it was malformed and missed it; the duplicate mint was caught by the audit's `uri_collision` check pre-close and corrected to a reuse (see §3 B2, and the process note in §4 item 31).
- **Codes / credentials / settings.** 0 ICD-10/HCPCS/CPT/modifier codes, 0 code group (no coding section), 0 provider credentials (no ordering/performing actor named), 0 healthcare settings. 1 benefit category, reuse.
- **References (1 mint).** TN 33 → `gemi:tn33CIM` (**B3**). Named in the Transmittal Information field and the 09/1988 Revision History entry describing the change it made — it established the cardiokymography coverage that is the current V1 content. **Era gate:** a coverage transmittal dated 09/1988 predates Pub. 100-03/100-04/100-20, so CIM (HCFA Pub. 6), overriding the page's Publication Number 100-3; corroborated by the CIM's monotonic dated series (`tn29CIM` 07/1988, `tn34CIM` 04/1989, `tn36CIM` 05/1989). Takes `gem:revisesPolicy gemi:ncd20.24` (S151 transmittal-edge rule); the policy asserts the reciprocal citing-side `gem:referencesPolicy`. No CR (predates the CR system). Source URL pending (pre-2000 CIM; archive begins 2000); `gem:sourceAvailability` not asserted → `source_availability_unverified` INFO **41 → 42**. Empirical counts: `revisesPolicy` **238 → 239**, `revisedByPolicy` **0**, `referencesPolicy` **1108 → 1109**.
- **Registry.** `policies_processed` **158 → 159**; TTL `# Policies processed:` header list, the `# --- planDone / isInEffect=True ---` list (**158 → 159**), and the `# --- planPromote / isInEffect=True ---` list (**705 → 706**) updated. `### NCD 20.24` section added to `gem_rule_categories.md`; S259 entry appended to `gem_edit_log.md`. `policy_worklist.json` metadata `policies_processed` 158 → 159, `last_updated` 2026-08-01 (S259) (no new worklist entries — the single reference is minted direct to the graph as a stub). `dc:source` = Tom's supplied `?ncdid=262&ncdver=1`. SKILL.md empirical sentence → as of S259, 239/0/1109 (Fix-A close autofix).
- **NCD census.** Active, extracted **126 → 127**; Total **143 → 144** (Stubs 2, Retired 10, Deleted 5, Unknown 0 unchanged).

Post-close audit on the S259 set (this handoff in place): **all checks GREEN — 0 RED, 0 YELLOW.** Two INFO (`source_availability_unverified` **42**; `policy_effective_date_v1` **24**). No ontology / SHACL / audit-script / `cpt.ttl` / `gem_llm_annotations.json` change.

## §3 — Decisions (S259)

All three are NCD 20.24 borderlines, Tom-confirmed at Claude's lean:

- **B1 — 4 rules (r2/r3 split).** Section A's two sentences kept as separate rules — r2 the date-of-service coverage boundary, r3 the adjunct-use + clinical-indication gate — rather than folded into one Pattern-3 rule (→ 3). Materially different assertions under the verbatim-capture posture (corollary #3). r3 folds the male/female indications verbatim (a completed sentence, not a δ-atomizable gate).
- **B2 — `conceptAngina` (concept with prefLabel "angina").** Confirmed as a concept with prefLabel *"angina"*, not a reuse of `conceptAnginaPectoris` (which drops *"pectoris"*). Realized at Generate as a **reuse** of the existing `gemi:conceptAngina` (S196, NCD 190.15) on exact-prefLabel match — more aligned with the confirmed decision than a fresh mint. Not split into typical/atypical individuals; the *"either typical or atypical"* scope stays verbatim in r3.
- **B3 — `gemi:tn33CIM`, revises + references.** Era gate makes TN 33 (09/1988) a CIM coverage transmittal; corroborated by the CIM monotonic dated series. `gem:revisesPolicy gemi:ncd20.24` (transmittal-edge rule) + citing-side `gem:referencesPolicy`. `planPromote`/`isInEffect true`; no CR; source URL pending.

## §4 — Open items

Items carry from S258 unless noted.

1. **Cadence checkpoint — next DUE at 160.** `policies_processed` is **159** (NCD 20.24 extracted this session). **One out** — the next extraction/promotion triggers it.
2. **LCD/Article V1-date research — 18 candidates (`[107]` remainder).** Unchanged: `a52467, a52492, a52494, a52495, a52510, a52514, a52517, a52519, a54969, a55426, a57115, a58075, lcd33612, lcd33718, lcd33797, lcd33800, lcd33923, lcd36524`. Blocked on Tom's renditions. `policy_effective_date_v1` INFO = **24** (NCD 20.24, being V1, did not add).
3. **CIM stub source availability — 42.** `tn33CIM` (S259) joins the queue; `tn159CIM` (S249) remains Source-pending. Both pre-2000 CIM, expected to stay Source-pending (CMS's public transmittal archive begins at 2000).
4. **Possible era-gate mistokens among pre-crystallization transmittals (S236); CIM ceiling 169 (S247).** Pending Tom.
5. **Referenced-document stubs from NCD 220.5 (S251).** Five. All `planPromote`.
6. **Referenced-document stubs from NCD 220.13 (S249).** Five. All `planPromote`.
7. **Referenced-document stubs from NCD 210.4 (S248).** Five. All `planPromote`.
8. **Referenced-document stubs from NCD 110.23 (S247).** Thirty-five. All `planPromote`.
9. **Referenced-document stubs from NCD 90.2 (S246).** Sixteen.
10. **Referenced-document stubs from NCD 20.33 (S245).** Twelve.
11. **NCD 20.14 stubs (S244) — RESOLVED.** No longer tracked.
12. **Referenced-document stubs from NCD 40.1 (S243).** `tn141CIM, cr1455, tn71CIM, tn13BP, tn1895MIM, tn305HHA`, six PMs — all `planPromote`.
13. **Referenced-document stubs from prior NCDs (S234–S259).** NCD 20.24 (S259, `tn33CIM`); NCD 110.4 (S237); NCD 190.3 (S235); NCD 230.9 (S234); NCD 250.5 (S242); NCD 260.6 (S241); NCD 250.4 (S239).
14. **`gem_reference.md` implementation-date clarification (S240) — deferred to migration end.** Pending Tom.
15. **Credential-URI consolidation candidates (S222).** Pending Tom.
16. **Setting-URI consolidation candidate (S238).** Pending Tom.
17. **`gemi:pub100_02_ch2` prefLabel likely carries Ch 6's title (S221); `pub100_04_ch32` title-free (S237).** Pending Tom.
18. **RESOLVED (S255) — global Edit log relocated** to `gem_edit_log.md`. No longer tracked.
19. **`# Extracted:` banner line vs the S46 banner-discipline rule (S237).** Sweep or bless. Pending Tom. (Recent section headers, incl. NCD 20.24 / 230.12 / 190.24 / 220.9, omit the `# Extracted:` line.)
20. **Reused-transmittal internal-edge retrofit (S242).** Deferred. Pending Tom.
21. **Prior promote-queue stubs (S214–S241).** Live NCD stubs remaining: `gemi:ncd20.4`, `gemi:ncd210.3`; plus retired-in-place `gemi:ncd280.13`.
22. **`[87]` transmittal-content validation (approved, unbuilt).** Parked. Pending Tom.
23. **The § (section-sign) verbatim rule undocumented in `gem_turtle_style_guide.md` (S241).** Pending Tom.
24. **KNOWN_V1_DATES / `[107]` recording for extracted NCDs (INFO nudge).** `policy_effective_date_v1` flags `gemi:ncd20.33, ncd90.2, ncd110.23, ncd210.4, ncd220.5, ncd230.11`. Standing: `ncd50.3` / `ncd220.1` KNOWN_V1_DATES additions. Pending Tom. (NCD 20.24's V1 date 1988-10-12 recorded on the individual; V1-current, not a candidate.)
25. **NCD census documentation doc (S244).** `claude/ncd-morning-count-rules.md` predates the S244 refinement; `_classify_ncd` is source of truth. Still cites a stale 2026-07-28 snapshot — current census is **Active 127 · Stubs 2 · Retired 10 · Deleted 5 · Unknown 0 · Total 144** — and the `07`-era Dropbox path. Regenerate only if Tom wants.
26. **Possible SKILL.md refinement — the cross-reference / pure-pointer NCD shape (S243/S254).** Pending Tom.
27. **Registered patterns (no methodology change).** Standing set unchanged. Includes the **07/2002 lab negotiated-rulemaking batch** shape and the **longstanding-NCD date rule**. NCD 20.24 adds a registered instance of the **code-less single-version CIM-era diagnostic NCD** whose V1-establishing transmittal is CIM-tokenized under the era gate and takes `revisesPolicy` (the `tn29CIM` / `tn40CIM` line): a coverage transmittal named in the current Transmittal Information field whose Revision History entry describes the change it made.
28. **Namespace is `…/2026/08/…`; audit auto-detects it (S255).** Informational.
29. **`gem_edit_log.md` S245-at-top ordering anomaly (S255).** Unchanged; S259 entry appended at EOF (correct tail). Reorder or leave — Tom's call.
30. **`register_section_coverage` message wording (S255).** Cosmetic only (check GREEN); tighten or leave — Tom's call.
31. **Plan-turn reuse-search hygiene (S259).** The B2 near-miss: a malformed prefLabel grep at Plan turn missed the existing `gemi:conceptAngina` and a duplicate was minted, caught pre-close by the audit's `uri_collision` check (the backstop worked; the concept resolved to a reuse before freeze). Candidate SKILL note — verify concept/credential reuse-candidate searches are well-formed (search the bare prefLabel and the bare URI, not a quoted composite), the `uri_collision` check being the safety net rather than the first line. Pending Tom's call on whether to promote a one-line rule into `SKILL.md` (§Clinical Concepts, reuse-vs-mint) or leave it as this note.

---

## §5 — Plan for S260

### §5.1 — Bootstrap (auto-authorized)

Run `python3 /mnt/user-data/uploads/gem_audit.py --files-dir /mnt/user-data/uploads/ --output-dir /mnt/user-data/outputs/ --autofix` immediately on the first prompt, without asking. `pip install rdflib --break-system-packages` if missing. The S260 uploaded set should match this handoff's §1 table byte-for-byte: expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **42**; `policy_effective_date_v1` **24**), plus the always-on **`[NCD CENSUS]`** block (Active 127 · Stubs 2 · Retired 10 · Deleted 5 · Unknown 0 · Total 144). Any RED is a halt; surface YELLOW for decision.

### §5.2 — First action

**Cadence checkpoint is due at 160 — one out**, so the next new extraction/promotion triggers it; plan to run the 20-policy checkpoint review (deferred proposals, SKILL.md/memory-edit curation, schema/worklist health, reference-stub backlog) at that point. No forced order otherwise: process the next policy (worklist related-policies or Tom-supplied); promote a `planPromote` stub through its own Plan/Generate cycle (items 5–13, 21, incl. the two live NCD stubs `gemi:ncd20.4`, `gemi:ncd210.3`); or advance a §4 item (e.g. item 31's SKILL note).

### §5.3 — Do not

- `policies_processed` is **159** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace — detection is deliberate (Option B, S255).
- Do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple — edit `_LLM_ANNOTATED_VOCAB_LOCALNAMES` when a vocab family is added.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
