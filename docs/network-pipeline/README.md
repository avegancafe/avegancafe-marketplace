# The J2 Network Pipeline — from Upload to "Your Network is Ready"

> A verbal description of everything that happens between a customer clicking **Create/Update
> Network** and receiving the completion email — with the customer-impacting milestones called out.
> This document drives the design of the interactive visualization in
> [`index.html`](./index.html).
>
> **How this was researched:** J2 GitHub code was not directly readable in the research session, so
> every claim below is sourced from primary non-code evidence — Slack engineering threads (many
> containing bot-generated code traces with `file:line` references), Linear issues, the Network
> Status PRD in Notion, the Network Status kickoff recording (Fathom), and Amplitude's event
> taxonomy. Confidence tags: **[HIGH]** multiply-sourced or primary-verified, **[MED]**
> single-sourced/partially corroborated, **[approx]** placement inferred. Snapshot date: 2026-07-22.

---

## 1. Thirty-second context

A health plan uploads a CSV of its in-network providers — "a network." J2 computes whether that
network meets regulatory access rules ("adequacy scores": the share of members within X
miles/minutes of each specialty, per county/zip), then populates the Postgres reporting tables that
the J2 UI reads. One upload triggers a *lot* of compute: geocode every provider, build a
provider×member drive-time matrix in BigQuery, run dbt scoring models, then publish results to the
app database. **[HIGH]**

The defining tension of the whole system — and the reason the milestone callouts matter — is that
**the machine's progress and the customer's visibility are almost completely decoupled.** Between
the "we're processing" email and the "network is ready" email, the customer sees *nothing* in the
app: on Create, no row appears in the network table until the run finishes; on Update, the old row
sits unchanged. There is no status column, no spinner, no toast (the Network Status project,
kicked off July 2026, exists precisely to close this gap). **[HIGH — Notion PRD; Fathom kickoff]**

## 2. Cast of characters

**Three Postgres records per run** **[HIGH]**
- `SelfServeTask` — the run's bookkeeping row: `created_at`, `completed_at`, `errored_at`,
  `completion_notified_at`, plus the observability-only stage machine (`current_stage` /
  `errored_stage`, PLA-175) and the resume marker (`attempt_stage`).
- `NetworkSnapshot` — a point-in-time capture of the network. New one per run. **The latest
  snapshot is the truth**; several steps re-derive "latest" at execution time — the root of most
  race-condition war stories.
- `NetworkChangeEvent` — "what changed," pinned to one snapshot.

**Two compute engines**
- **The heavy pipeline** — Celery task `run_self_serve_pipeline` on the `adequacy_pipeline` queue,
  running on a dedicated `j2-django-celery-pipeline-worker` GKE deployment. `acks_late=True` +
  `reject_on_worker_lost=True`: it re-runs only if a worker *dies* (e.g. a deploy), never on an
  app error. Since "the fold" (PR #2272, April 2026) the compute that used to live in the
  standalone pipeline-service runs inline here; the fold reached 100% of prod on 2026-06-23. **[HIGH]**
- **The completion ("score") chain** — a serial Celery chain the pipeline **fire-and-forgets**
  (`build_score_chain(...).apply_async(link_error=update_task_error)`) since "direct-enqueue"
  (PR #2600, May 2026). Nobody waits on it; the only safety net is the stale-task watchdog. Its
  steps hop across the `dbt`, `reporting`, and `default` queues. **[HIGH]**

**Storage** — uploaded files in GCS (`gs://j2-production/self_serve_provider_file_uploads/`); a
per-run BigQuery dataset named `adequacy_network_create_production_<tenant>_<user>_<net>_<ts>`;
results merged into tenant Postgres schemas. **[HIGH]**

## 3. The journey

### Phase 0 — Upload & synchronous intake (seconds)

The customer, in the **Networks page**, clicks **Create Network** (`CreateNetworkPage`) or opens an
existing network's **Update drawer** (`NetworkViewDrawer`). They provide: a network name, a service
area (county picker, filtered on create to counties that actually have members in the standard's
member file), the regulatory/custom **standard** to score against, and the **provider CSV** (per-
tenant loading template: NPI, address, specialty, INN/OON flag, etc.). **[HIGH]**

Synchronously, in the request:
1. **File validation** runs and the `ValidationResultsDialog` shows *fatals* vs *warnings* —
   unparseable CSV and missing required columns are hard rejects; softer rules (deactivated NPIs in
   NPPES, specialty grouping, service-area/member-file overlap) produce warnings plus a
   downloadable **troubleshooting file** (the upload's columns + a `Validation_Detail` column).
   ⭐ *This modal is the only instantaneous feedback in the entire flow.* **[HIGH]**
2. The file lands in GCS (`uploaded_*.csv` + `validated_*.csv`).
3. The three records are created (`SelfServeTask` type `createNetwork`/`updateNetwork` + snapshot +
   change event); stage = `queued`.
4. 📧 **Email #1 — kickoff** (*"we are processing your network"*) goes to the initiator only —
   teammates get nothing. Sent at button-press time, *not* when the queue picks the task up.
   Skipped for SFTP feeds and recipient-less tasks; all emails are prod-only (`SEND_EMAILS`). **[HIGH]**
5. `run_self_serve_pipeline` is enqueued on `adequacy_pipeline`; an internal "received request"
   notification posts to Slack. **[HIGH]**

**What the customer sees now: nothing.** On Create there is no row in the network table; on Update
the row is unchanged and the *old* snapshot keeps serving all pages/reports. **[HIGH — PRD]**

> Other entrances to the same pipeline (no customer emails): SFTP weekly batch feeds
> (`network_provider_feed_batch`, synthetic `sftp_bulk_upload` user), operator re-runs
> (`rerun_self_serve_tasks`), and the disruption module's create-network. **[HIGH]**

### Phase 1 — Queue wait (0 minutes → hours)

Runs wait for a slot on a small, fixed worker pool (no autoscaling in prod as of July 2026; bursts
of ~100 uploads from one tenant have queued behind alarms). Customers can't see queue position —
deliberately out of scope even in the Network Status project. **[HIGH]**

### Phase 2 — The heavy pipeline (~15–25 min floor; hours for big/cold-cache networks)

Progress is tracked by the PLA-175 stage machine — **12 stages, observability-only** (they emit to
the internal j-3po bot; customers never see them). In order: **[HIGH — stage list; [MED] BQ-job mapping]**

| # | Stage | What actually happens |
|---|-------|----------------------|
| 0 | `queued` | waiting for a worker slot |
| 1 | `prepare.start_attempt` | bookkeeping; fresh-attempt reset |
| 2 | `prepare.format_providers` | raw upload → `Formatted_Pipeline_Data` in BQ |
| 3 | `build.filter_inputs` | filter to service area / standard inputs |
| 4 | `build.assemble_universe` | build INN + OON provider universes; first dedup (`SELECT DISTINCT` over ~13 columns); **geocode provider addresses via Precisely** (cached by address hash) |
| 5 | `build.validate_universe` | produce `validation_results` (feeds the troubleshooting file) |
| 6 | `build.combine_providers` | second dedup to unique `provider_location_id` (NPI + geocoded address); combine INN + OON |
| 7 | `build.compute_distances` | **the expensive one**: the provider×member distance matrix ("PMD") — GraphHopper road routing for INN, precomputed global PMD for OON; members are census-sampled points from the standard's member file |
| 8 | `build.finalize_tables` | final BQ table assembly |
| 9 | `handoff.copy_pmd` | copy PMD out of the run dataset |
| 10 | `handoff.migrate_universe` | **BQ → Postgres** provider-universe migration (`in_network_provider_location` etc.). *The only resumable stage* — an `acks_late` redelivery resumes here instead of recomputing |
| 11 | `score` | set as the pipeline fire-and-forgets the score chain and reports itself done |

Under the hood the 12 coarse stages run as ~25 *serial* BigQuery jobs, which is why even a tiny
8-provider network takes ~15–25 minutes. Silent side-effect worth knowing: the two dedup passes can
legitimately shrink a customer's file by tens of thousands of rows with **zero feedback** ("dropping
providers" support tickets are usually this). **[HIGH]**

### Phase 3 — The handoff (the moment of decoupling)

At the end of the sync phase the pipeline enqueues the score chain and **the Celery task "succeeds"
while the run is unfinished** — from here on, nothing is watching except the watchdog. Provider
data now exists in the app database. **[HIGH]**

> ⭐ **MILESTONE A — the network quietly becomes visible/selectable.** Around this point (exact
> gate unconfirmed — placement **[approx]**) the network starts appearing in the network dropdown
> and its provider data is queryable, *before scores exist and before any email*. Kyle, at the
> Network Status kickoff: *"the network is selectable, but there are maybe no scores and they
> haven't gotten the email yet. And they're like, why can't I see some of the network but not all
> of it?"* Abby: *"the network is in the drop down. There is a period of time when there's no
> scores, then there are scores, and then there's still more reporting stuff."* **[HIGH that it
> happens before scores/email; approx where]**

### Phase 4 — The completion chain (queues: `dbt` → `default` → `reporting` → `default`)

The serial chain, in current post-PR-#2957 order: **[HIGH; Slack-notification position [MED]]**

1. `run_covered_members_dbt_pipeline` (dbt) — which members count as covered
2. `run_scores_dbt_pipeline` (dbt) — compute scores in BQ: per (county × zip × specialty ×
   metric) coverage fractions 0–1.0, metrics `DRIVE_TIME`, `DRIVE_DISTANCE`, `MINIMUM_COUNT`(±in
   zip/county), combined per the standard's AND/OR logic
3. `merge_zip_county_score_to_shared_schema` / `merge_servicing_provider_count…` (default) — push
   score rows into tenant Postgres
4. `run_reporting_dbt_pipeline` (dbt)
5. `populate_initial_reporting_data` (reporting queue; **6–14 min**, the serial bottleneck; shares
   its queue with exports/packets — the June 10 starvation) — rebuilds the app-facing tables
   (provider locations & specialties, member access, zip summaries, `NetworkZipCountyScore`), then
   sets ⭐ `snapshot.reporting_data_available_at` and triggers any pending PDFs
6. `populate_county_adequacy` / `populate_zip_adequacy` (default) — fill `CountySpecialtyAdequacy`
   / `ZipSpecialtyAdequacy`, which the **Scores tab/scorecard** and **zip-adequacy map** read
7. `send_network_completion_slack_notification` — internal post to `#logs-network-prod` **[MED position]**
8. `finalize_score_calculation`
9. `update_task_result` — durably commits `completed_at` + the winning `snapshot_id`
10. `check_batch_completion`
11. 📧 `send_network_completion_email` — **terminal step** (moved here by PR #2957, opened Jun 24 /
    merged ~Jul 9, after the email-then-blank-data race)

> ⭐ **MILESTONE B — scores appear.** Until the adequacy tables are populated for the current
> change event, the scorecard API literally 404s (*"Zip adequacy data is not yet available"*) — a
> blank state, not zeros. Scores landing is a *mid-to-late-chain* event. **[HIGH]**
>
> ⭐ **MILESTONE C — reporting data available** (`reporting_data_available_at`): report building
> and queued PDFs unblock. Whether B and C are one moment or two — and their exact order — is
> genuinely unresolved *inside J2* (it depends on the per-tenant `POPULATE_INITIAL_REPORTING_DATA`
> flag; legacy-path tenants defer reporting sync to first report). The PRD's open-questions table
> asks exactly this. Treat B/C as a fuzzy adjacent pair. **[HIGH that it's unresolved]**
>
> ⭐ **MILESTONE D — the customer is told.** 📧 Email #2 *"your network is ready"* — or its
> sibling, 📧 Email #3 *"…but we found some issues with your data"* (subject "Inaccurate data
> found for <network>") when a troubleshooting file exists (NAVY-1142). Terminal, after
> `completed_at`; stamps `completion_notified_at` under `select_for_update` → **at-most-once, and
> once sent the run can never auto-restart** (`_try_resume` short-circuits; manual rerun clears
> the stamp). Initiator only. **[HIGH]**

### The error path (any phase)

📧 **Email #4 — "Action Required: Problem processing your network"** — a blanket message with no
error detail, sent from **exactly 5 call sites** (pre-pipeline, in-pipeline, score-chain
`link_error` — only if not superseded and not already completed —, the 48-hour watchdog, and a
legacy HTTP notify endpoint). **[HIGH]**

It is **not guaranteed**: at least 7 paths mark the run errored (or kill it) with *no* email —
superseded attempts (deliberate, post-June-10), "newer attempt already completed" races,
PU-contention budget exhaustion, a worker killed without an exception (redelivery resumes
instead), recipient-less tasks, SendGrid failures swallowed to Sentry, and the 12–48h alert-only
watchdog tier. And it is **not deduped** — reruns and the legacy double-notify (PLA-207, still
open) can send more than one. Consequence the Network Status project leans on: **the database's
`errored_at` is more reliable than the email.** **[HIGH]**

**The watchdog** (hourly): >12h running → one aggregated internal Sentry alert per tenant
(no customer signal; added June 2026); >48h → force-errored + error email — which, for a stranded-
but-actually-computed network, is a *false* failure email. It marks; it never recovers. **[HIGH]**

**Guardrails built from scar tissue (2026):**
- *April* — worker wedge: pipeline workers silently stopped consuming (RabbitMQ 4h ack-timeout
  kills); customers got kickoff emails, then silence for hours. Fix: real liveness probes
  (#2401/#2406) → ~8 min auto-recovery.
- *June 10* — reporting-queue starvation stranded 26 fire-and-forgotten chains ~15h; a blind bulk
  re-kick then made the drained originals lose snapshot races → **26 false failure emails** and a
  customer re-upload loop. Fixes: superseded-attempt benign skip (#2805), reporting capacity
  (#2806), 12h watchdog tier (#2807).
- *June 24* — a deploy redelivered a finished-but-unacked run; the email had fired mid-chain, then
  the re-run blanked scores: customer saw *ready-email → data → blank → partial (east coast only)
  → full*. Fix: #2957 (email terminal + `completion_notified_at` gate). A sub-second residual
  window remains (PLA-204, open). **[HIGH]**

## 4. The customer-facing timeline (what the visualization must show)

| When | Machine truth | What the customer sees |
|------|--------------|------------------------|
| T0 upload | records created, file in GCS, task queued | validation modal (only instant feedback); then **nothing** — no row (Create) / stale row (Update) |
| T0+s | — | 📧 #1 "we are processing your network" (initiator only) |
| queue wait (min–hrs) | task sits on `adequacy_pipeline` | nothing; no queue visibility |
| ~15–25+ min | 12 stages / ~25 serial BQ jobs | nothing (stages are internal-only) |
| handoff | chain fire-and-forgotten; provider rows in Postgres | ⭐ **A: network appears & is selectable — scoreless, unannounced** |
| chain, mid | scores computed & merged | scorecard still 404s ("not yet available") |
| chain, late | reporting + adequacy tables fill | ⭐ **B/C: scores render; reports unblock** (fuzzy pair, flag-dependent order) |
| terminal | `completed_at` → `completion_notified_at` | ⭐ **D: 📧 #2 "ready" / #3 "ready, but issues"** |
| any failure | `errored_at` (maybe) | 📧 #4 "problem processing" — *maybe*, and maybe twice; no in-app error state |

Typical healthy end-to-end: **~25–75 minutes** (queue wait + pipeline floor + 6–14 min reporting
hop); big, national, or cold-cache runs stretch to hours; the watchdog's tiers are 12h/48h. **[MED
— composed from verified parts; no single verified end-to-end trace]**

## 5. Shape analysis → why the visualization looks the way it does

The system's true shape is **two conveyor belts in series with a dropped baton between them** —
a synchronous, stage-tracked belt (upload → BQ compute → Postgres migration), then an untracked
asynchronous belt (score chain) that nobody watches — **plus a second, parallel track: the
customer's view**, which stays dark for almost the whole run and lights up at four milestones
(A/B/C/D) that are *offset* from the machine's own sense of progress.

So the visualization is a **dual-lane journey map** ("machine lane" vs "customer lane") with a
scrubbable clock: you drag (or play) a network run left-to-right; the machine lane animates
stages, queues, and the fire-and-forget handoff; the customer lane stays conspicuously empty
except at the milestone flags — which is exactly the product story. Error paths appear as
side-exits with the email/no-email split, and the three 2026 incidents are told as optional
"war story" annotations at the point where each bit. Whimsy: the network is a little CSV file
character that gets geocoded, measured, scored, and finally mailed home. 🎉

## 6. Primary sources

- **Notion PRD** — "Network Processing Statuses and Customer Experience Improvements"
  (`35d58d7d507880ee8a02ce2e353dd2be`), read in full via API.
- **Fathom** — Network Status Project Kickoff, 2026-07-20 (`fathom.video/calls/751458630`),
  quotes verified against the transcript.
- **Slack** — #team-platform incident explainer (`C0ANV1TE295` ts 1781143817), June-24 race thread
  (`C0B1K1AERA5` ts 1782315623), email state-of-the-world (`C0AS2QVNLJJ` ts 1784642024), error-email
  audit (`C0BCGMG0YDR` ts 1784568457), stage-machine technical doc (file `F0BJJMCMZSM`), BQ
  row-count trace (`C0AS21S9UNR` ts 1776979820), intake lineage (`C06GUHW8272` ts 1784737800),
  score-chain traces (`C0B1K1AERA5` ts 1781189855), #logs-network-prod (`C04L0AZTTFD`), and others.
- **Linear** — PLA-175, PLA-200, PLA-204, PLA-207, SUP-166, NAVY-1142, MNDRN-4710, MNDRN-3592.
- **Amplitude** — production project 629417 event taxonomy (UI surface names).
- Full research corpus (five sliced reports + recon notes) generated 2026-07-22.
