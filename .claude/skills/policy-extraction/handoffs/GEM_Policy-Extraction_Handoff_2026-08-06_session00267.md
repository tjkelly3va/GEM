# GEM Policy-Extraction Handoff — Session 267 (2026-08-06)

## §1 — Canonical files (post-close state)

Hashes are md5 over the frozen output set; **M** marks a file changed this session. The canonical set is **15 files**.

| File | md5 | size | S267 |
| :--- | :--- | :--- | :--- |
| `GEM_ontology.ttl` | `5a77000e27e2ce03d6e2e0596e716934` | 340257 |  |
| `GEM_policy_instances.ttl` | `bc338f62e862f9e68ff2472aac45b2d0` | 6074368 | **M** |
| `GEM_code_group_instances.ttl` | `10a70c01175dcf714a4bd8307bd07eeb` | 25942 |  |
| `cpt.ttl` | `351aa816b978ec63a6800feb50bfb5c4` | 35223 |  |
| `SKILL.md` | `9956f49f098c6eff3e07c865e0ce50af` | 285703 | **M** |
| `gem_reference.md` | `bd2a8164afcf31ccfeda5dc242fd6f63` | 121808 | **M** |
| `gem_rule_categories.md` | `6a8f4d8eb9a7494662b89c392224990f` | 1520278 | **M** |
| `gem_edit_log.md` | `8b953004aa94f6fceaf5ce910d3e433f` | 162511 | **M** |
| `gem_structured_rule_guide.md` | `5dc562fdf25cdd7a492969be2b82fee5` | 60817 |  |
| `gem_turtle_style_guide.md` | `0c82c21cb54232de2c731fb1dcfce117` | 26524 |  |
| `manifest_format.md` | `24d134579244454795e39b2be1ce80d3` | 26227 |  |
| `policy_worklist.json` | `a6bfebb3c0c685b0e5553ef8c4ba1db3` | 322732 | **M** |
| `gem_llm_annotations.json` | `ae89620445889e7137e2bdc5ba4cd669` | 7213 |  |
| `worklist_schema.md` | `2519964abbdba260c621a6a5e9f8318b` | 16521 |  |
| `gem_audit.py` | `05029d1e6a1e328c72d8499bfd9b4733` | 339782 | **M** |

## §2 — Work completed in S267

**One promotion, and the audit's own era-gate ceiling raised twice.** NCD 220.6 is the umbrella §220.6 section — the parent the whole 220.6.x family was carved out of, extracted last, after six of its subsections. It is a promotion rather than a fresh mint, and the first extraction in the corpus to straddle the Coverage Issues Manual → Pub. 100-03 crystallization **inside its own version set**. That produced a RED on the audit's `CIM_MAX_TN` ceiling, which the source overruled; Tom then located three more CIM renditions and, for the first time, searched for the next one and did not find it. No schema change (`GEM_ontology.ttl` byte-identical).

**Graph movement:** `policies_processed` **181 → 182**. Instances triples **54,331 → 54,687** (+356). Workflow `planDone` **181 → 182**, `planPromote` **763 → 791**, `planNone` **16 → 17**. NCD census **Active 141** (unchanged), Stubs **6** (unchanged — `ncd220.6` leaves for Retired, `ncd220.12` arrives), Retired **18 → 19**, Deleted 5, Unknown 0, **Total 170 → 171**. Clinical concepts **2,998 → 2,999**; policy rules **1,995 → 1,998**; provider credentials **138** and healthcare settings **26** both unchanged. `referencesPolicy` **1254 → 1295**, `revisesPolicy` **283 → 296**, `revisedByPolicy` **0** (invariant), `referencesChangeRequest` **142 → 151**. INFO: `source_availability_unverified` **49 → 51** (the two new CIM stubs with neither `dc:source` nor `sourceAvailability`), `policy_effective_date_v1` **24** unchanged.

**`sources/` gained 7 PDFs** — the seven NCD 220.6 renditions, all supplied by Tom.

### (a) The extraction

| Policy | Rules | Concepts | Refs / new stubs | Δ |
| :--- | ---: | :--- | :--- | ---: |
| **NCD 220.6** Positron Emission Tomography (PET) Scans - RETIRED | 3 | 1 mint | 41 + 9 CRs / 30 | +356 |

Seven-version **retirement-in-place** NCD, V7 effective and implemented 2023-04-10. `policyEffectiveDate` and `policyImplementationDate` both **2002-10-01**, V1's per S192; `KNOWN_V1_DATES` row added per S260 D8. `gem:priorManualSectionNumber` **`Pub. 6 §50-36`** — V1 is published in the Coverage Issues Manual. 1 benefit category (reuse), 1 credential (reuse, via R2's `delegatesCoverageTo`), **14 inbound `revisesPolicy`**. 0 codes, 0 code groups, 0 settings.

**Promotion means relocation.** `gemi:ncd220.6` was a `planPromote` stub minted at S264 inside NCD 220.6.15's `POLICY STUBS` sub-section; it moved to its own top-level section, per the `ncd220.5` (S251) / `ncd280.8` (S156) practice. **This is the step whose omission is §4 item 52** — doing it here did not touch item 52, which remains about `a55426`.

### (b) 20,000 words of source, zero retained rules (§3 D1)

V1–V5 carried the full PET coverage scheme: V2's sixteen numbered sections (allowable scanner types, per-cancer coverage for lung, esophageal, colorectal, lymphoma, melanoma, head and neck, thyroid and breast, cardiac perfusion with Rb-82 and N-13 ammonia, and the soft-tissue-sarcoma and dementia noncoverage determinations), V3's coverage-with-evidence-development tables, V5's MAC-discretion preamble. **V6 states in its own text that CMS removed the umbrella NCD**, so this is a documented removal and S151 retention does not fire; the S152 corollary takes the concepts with the rules. A seven-version, 22,000-word policy therefore mints **one** clinical concept. What survives survives in the 220.6.x subsections — which is what the live body's third sentence says.

### (c) The era gate fires six times in one policy, twice inside one revision history (§3 D2)

| number | this policy | the graph held | outcome |
| :--- | :--- | :--- | :--- |
| TN 76 | 05/1995 CIM | `tn76NCD` (2007, NCD 220.5) | mint `tn76CIM` |
| TN 106 | **02/1999 CIM** | `tn106NCD` (2009) | mint `tn106CIM` |
| TN 106 | **09/2009 Pub. 100-03** | `tn106NCD` | reuse |
| TN 113 / 136 / 147 | 1999–2001 CIM | `tn136NCD` (2011) | mint `tn113CIM`, `tn136CIM`, `tn147CIM` |
| TN 156 | 08/2013, `R156NCD.pdf` | `tn156CIM` (2002) | mint `tn156NCD` |
| TN 171 | 06/2003, **`R171CIM.pdf`** | `tn171NCD` (2014) | mint `tn171CIM` |

**Transmittal 106 appears twice in one Revision History as two different documents.** Both are cited, both are linked, to distinct individuals. TN 171's collision is settled by the source itself: V2 publishes `R171CIM.pdf` against `tn171NCD`'s `R171NCD.pdf`.

**`tn156CIM` was reused, not duplicated (§3 D3).** Same manual, same number, same month as NCD 160.23's TN 156 — and a transmittal number is unique *within* a manual, so the era gate does not license a split inside one. The differing change request (CR 2138 here, CR 2153 there) is one omnibus CIM transmittal read from two sections' revision histories, recorded as an observation rather than resolved by minting a second individual.

### (d) `CIM_MAX_TN` raised twice, 169 → 171 → 174 (§3 D4)

`transmittal_manual_token` fired **RED** on `gemi:tn171CIM` against the recorded CIM extent of 169. The source overruled the guard: NCD 220.6 **Version 2's own Coverage Transmittal Link publishes `R171CIM.pdf`**, Tom supplied the same URL, and the entry carries effective and implementation dates of 10/01/2003 — the CIM ran a quarter past "early 2003". Ceiling raised to **171**.

Tom then located **R172CIM, R173CIM and R174CIM**, and **searched for R175CIM without finding it**. Ceiling raised to **174**.

The second raise differs in kind from all four before it. 167, 168 (S177), 169 (S247) and 171 were each pushed up *from below* by whichever single rendition happened to be needed that session; **174 is the first ceiling bounded from above**, because someone asked where the manual stops rather than only where it had been seen to reach. That makes it a better number without making it a documented terminus — a negative search is weaker than a rendition, and a `R175CIM` surfacing would move it again.

**TN 172–174 are deliberately not minted.** No policy in the corpus cites them, and S131 mints what is *referenced*, not what is known to exist.

`gem_reference.md` states the extent in four places (§5.2 prose, the manual-token table row, the era-gate rule, the ratchet history); all four were updated in the same edit as the code, so the number cannot drift between them. Self-test **115/115** after both raises.

## §3 — Decisions (S267)

- **D1 — a documented removal is read from the version that documents it, not from the size of what it removes.** V1–V5 are the most substantive versions in the family and produce zero rules, because V6 *reports* the removal. The temptation to retain scales with the volume of what is being dropped, and volume is not evidence. **Carry forward:** the retention test is the report, never the substance (S264 D1, confirmed at its largest scale yet).
- **D2 — the era gate is not a per-policy exception; a policy can straddle the crystallization internally.** Every prior era-gate collision was between the document in hand and a document elsewhere in the corpus. Here **one policy's own version set spans both manuals** (V1 is Pub. 6 §50-36, V2 onward Pub. 100-3 §220.6), so its cumulative revision history mixes eras and its transmittal numbers collide in both directions at once — including twice for the same number. `gem:priorManualSectionNumber` is what makes this legible in the graph.
- **D3 — a transmittal number is unique within its manual, so the era gate cannot split one manual (B1, Tom).** `tn76CIM`, `tn156CIM` and `tn156NCD` are three documents, all relevant here; `tn76NCD` is a fourth and is not. But the *existing* `tn156CIM` was reused rather than duplicated despite a differing CR and effective date, because same-manual + same-number + same-month is one document by construction. **The era gate disambiguates across manuals and eras; it says nothing inside one.**
- **D4 — a guard's empirical bound is a finding waiting to happen, and should say so in its own comment.** `CIM_MAX_TN` has been raised five times in ninety sessions, every time by a rendition arriving rather than by reasoning, and every time the guard fired correctly on a number it had not yet seen. The failure mode is treating the RED as a verdict on the *individual* rather than a question about the *ceiling*. Both `gem_audit.py` and `gem_reference.md` §5.2 now record the posture explicitly: **resolve a CIM-token RED only on a rendition, and read it as a question about the ceiling first.**
- **D5 — `sourceUnobtainable` is asserted on direction, never on a pattern (B1/B2, Tom).** `tn76CIM` carries it because Tom stated TN 76 is paper-only — which matches the term's own ontology definition verbatim. The S148/S149 archive line (CIM ≥126 has a rendition, ≤114 does not) independently predicted it, and **predicted correctly three for three** on the transmittals above the line, where Tom supplied URLs. It was still not used to assert anything: `tn106CIM` and `tn113CIM` sit below the line and stay `planPromote` with `dc:source` pending. Every one of the corpus's `sourceUnobtainable` assertions has come from Tom, and the two weakest say so in their own workflow notes.
- **D6 — a named deliverer that disclaims the change earns no revision edge (S169 sharpening, sharpest instance).** TN 11426 is named in all seven versions' Revision History and its entry reads *"This correction does not make any revisions to the companion Pub. 100-02 or Pub. 100-03; all revisions are associated with Pub. 100-04."* It takes `referencesPolicy` only. The other 14 coverage transmittals take `revisesPolicy`.
- **D7 — reference scope is the union across supplied renditions, and the dead versions are where the unique edges live (B5, Tom).** V7's Revision History is cumulative, so all 15 coverage transmittals and 9 CRs come from the live page either way. The union's whole yield is **12 edges recoverable only from superseded versions**: 6 Claims Processing transmittals and 1 Program Memorandum (**V7 dropped the Claims Processing Instructions section entirely**) and 5 NCAs V3 dropped. A cumulative revision history creates the impression that the live page carries everything; it does not carry what CMS *stopped listing*.

## §4 — Open items

Items 1–53 carry from S266 unless restated.

1. **Cadence checkpoint — next at 200.** `policies_processed` is **182**; 18 out. Not due. The item-52 agenda entry queued at S266 stands.
2. **LCD/Article V1-date research — 18 candidates.** `policy_effective_date_v1` INFO = **24**, unchanged.
3. **CIM stub source availability — 49 → 51.** `tn106CIM` and `tn113CIM` are the two additions; both sit **below** the S148/S149 archive line, so both are strong `sourceUnobtainable` candidates awaiting Tom's direction rather than inference (§3 D5). The three above the line arrived with URLs and never entered the queue.
4. **Era-gate mistokens — retrospective sweep still pending Tom.** S267 is the strongest argument yet for running it: six collisions in one policy, two of them for the same number.
5.–44. **Carry unchanged.**
45. **RE-MEASURED (S267).** `sources/` holds **340 PDFs, 267 NCD-named across 159 sections, 0 unparsed**, and **0 sections without a `planDone` individual**. Keep re-measuring; do not carry this answer forward. **Measure planDone from the graph, not the workflow-state text region.**
46. **`predicate_order` vs `predicate_ordering` name mismatch.** Still live.
47. **Stub `dc:source` convention is inconsistent.** S267 minted 30 stubs and split them four ways: `dc:source` from a Tom-supplied URL (`tn136CIM`, `tn147CIM`, `tn171CIM`), `dc:source` from a link the rendition publishes (`tn156NCD`), `sourceAvailability sourceUnobtainable` with no `dc:source` (`tn76CIM`), and neither (the remaining 25). The four-way split is the item's clearest instance to date.
48. **CLOSED (S264).**
49. **Carry, with the S265 caution.**
50. **CLOSED (S265).**
51. **CLOSED (S266).**
52. **DEFERRED to the 200-policy checkpoint (Tom, S266) — unchanged by S267.** NCD 220.6's promotion **relocated** its own individual, which is the practice item 52 says `a55426` did not follow; it neither fixes nor worsens the item. Of 72 `POLICY STUBS` banners, still exactly **one** has a `planDone` individual beneath it. **Prefer the wording fix over relocation; do not default to relocating.**
53. **NEW (S266) — no audit check covers banner presence.** Unchanged. S267's new section carries its banner correctly, by construction rather than by check.

54. **NEW (S267) — the `sources/` filename convention has a third form, and nothing reads it.** The seven NCD 220.6 renditions are named `NCD 220.6 v1.pdf` … `v7.pdf`. Census over the 267 NCD-named files: **166 dated** (`NCD X YYYY-MM-DD Effect.pdf`, multi-version), **94 undated** (single-version), **7 versioned** (this new form). The item-45 re-measure regex handles all three because it anchors only on `^NCD\s+<section>`, but **the S264 defect was exactly a filename regex that assumed one form**, and the memory note recording the convention describes only two. Either the note should be extended or the form normalized to dated; extending the note is cheaper and loses nothing.
55. **NEW (S267) — `gemi:ncd220.12` is minted with a bare-identifier `prefLabel`.** No rendition of NCD 220.6 gives the SPECT NCD's own title, and the cited policy is authoritative for its own identity (SKILL.md §Stub labeling), so inferring "Single Photon Emission Computed Tomography" from V2's colloquial cross-reference was declined. It resolves at its own extraction. Noted because a bare-identifier `prefLabel` on an NCD stub is unusual enough to look like an omission.

## §5 — Plan for S268

### §5.1 — Bootstrap (auto-authorized)

From the canonical directory, read the latest handoff in `handoffs/`, then run `python gem_audit.py --files-dir . --autofix` immediately, without asking. Expect a clean run with **no autofix write**, two INFO (`source_availability_unverified` **51**; `policy_effective_date_v1` **24**), plus **`[NCD CENSUS]`** (Active 141 · Stubs 6 · Retired 19 · Deleted 5 · Unknown 0 · Total 171). Any RED is a halt; surface YELLOW for decision.

**Mid-session `hash_verify` RED is normal.** The halt rule is about RED at **bootstrap**.

**The audit runs in ~18 seconds.** If it takes minutes, something is wrong — do not wait it out, and do not start a second run alongside the first.

### §5.2 — Standing priority: finish the NCDs (Tom, S260)

**Re-measure `sources/` against the graph before planning** (§4 item 45), with a regex that tolerates **all three** filename forms (§4 item 54), **printing the parsed-section and unparsed counts**, and reading planDone **from the graph**.

**The FDG PET family is now complete except `NCD 220.6.17`** — the section that replaced four of the siblings, cited by all of them, and the last high-value promote target in the family. `NCD 220.6.13` is the one sibling it did not replace.

Then the five stubs needing renditions from Tom:

| Policy | Note |
| :--- | :--- |
| **NCD 20.4** | Implantable Automatic Defibrillators (ICDs); CED with registry requirements; expect multi-version |
| **NCD 210.3** | Colorectal Cancer Screening Tests; extensive coding, long revision history; expect multi-version |
| **NCD 280.13** | TENS - RETIRED; counted under **Retired**, not **Stubs** |
| **NCD 80.7** | Cited by NCD 80.8 for excluded refractive procedures |
| **NCD 10.1** | Cited by NCD 80.8's bundling rule |

`NCD 220.12` (SPECT) is newly cited and newly stubbed — a candidate if Tom has the rendition (§4 item 55).

### §5.2a — After the NCDs

§4 items 53 and 54 are both small and both prevent a recurrence. Then 52 (at the checkpoint), 4, 37, 38, 40, 46, 47, 49. Items 35 and 36 also stand.

### §5.3 — Do not

- `policies_processed` is **182** — advance it only on a genuine new extraction/promotion.
- Do not re-hardcode the audit namespace; do not re-add the frozen `LLM_ANNOTATED_VOCAB_CLASSES` tuple; do not promote the PyYAML lazy import to module level; do not split `SKILL.md` without agreement.
- `owl:versionInfo`, the `# Produced:` header date, and Tom-supplied `dc:source` URLs remain untouched.
- **Do not lower `CIM_MAX_TN` (S267 D4).** 174 rests on renditions Tom located plus a negative search for 175. Raise it only on a rendition; treat a CIM-token RED as a question about the ceiling first and the individual second.
- **Do not mint a transmittal because it is known to exist (S267 D4).** TN 172–174 are deliberately absent; S131 mints what is *referenced*.
- **Do not assert `sourceAvailability` from the archive-line pattern (S267 D5).** Every such assertion in the corpus came from Tom. `tn106CIM` and `tn113CIM` are candidates, not conclusions.
- **Do not duplicate a transmittal across a differing CR or effective date within one manual (S267 D3).** Same manual + same number + same month is one document; record the divergence as an observation.
- **Do not read a cumulative revision history as the complete reference set (S267 D7).** V7 listed every transmittal and dropped an entire section plus five NCAs.
- **Do not retain removed content because there is a lot of it (S267 D1).** Check only whether the removal is reported.
- **Do not collapse `predicate_target_sort` to a single tier (S261).** V110/V111 guard both directions.
- **Do not re-introduce the literal-matching bug in `check_predicate_ordering` (S262 D7).** V112 pins it.
- **Do not restore the ambiguous block regex in `check_predicate_ordering` (S266 D4).** V115 pins it; the failure mode is a silent multi-minute hang.
- **Do not remove `block_terminator` as redundant with `predicate_order` (S266 D4).** Complementary by construction.
- **Do not treat a clean rdflib triple-count as sufficient verification of emitted bytes (S266 D5).** Valid Turtle can still be wrong Turtle.
- **Do not split a single source unit that says *covered under X / not covered under Y* (S262 D6), or that asserts two things about one subject (S265 D1).**
- **Do not treat the source's own lettering as the rule count (S266 D2).** Grammatical dependence keeps a condition whole; a modal shift breaks it apart.
- **Do not carry a transmittal's edges across from a sibling policy (S264 D2).**
- **Do not carry a family finding forward untested (S266 D1).**
- **Do not treat a same-stem reuse hit as identity (S265 D2).**
- **Do not assume a transmittal number identifies a document (S263 D2), in either direction (S264), or even within one policy's own version set (S267 D2).**
- **Do not trust an exact-prefLabel reuse search alone (S263 D5).** The forward URI pre-flight is the guarantee.
- **Do not conclude a text layer is damaged without re-extracting with `-enc UTF-8` (S262, S264 D5), and do not assume an apparent defect is tooling either (S263 D9).**
- **Do not chase an authoritative CMS NCD index to measure remaining work (item 41).**
- **Do not read the census `Stubs` count as the promote queue, and do not count graph facts with a regex over the TTL (item 43) — nor file structure (S266).** Use rdflib.
- **Do not carry forward a previous session's "`sources/` is fully extracted" answer (item 45), and do not assume the filename convention has only two forms (item 54).**
- **Do not reprocess any already-extracted NCD until every NCD is processed (Tom, S260).**
- **Do not delete anything from `sources/`, and do not delete the Dropbox originals** (Tom, S260).
- **Do not read other policy-PDF locations.** `Dropbox\Projects\HOO2pilot\policies` is the sanctioned source directory.
- **Push at session close, not before.** The remote is the only off-machine copy of `sources/`.
