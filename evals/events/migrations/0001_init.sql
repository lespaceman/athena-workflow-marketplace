PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS events (
    seq            INTEGER PRIMARY KEY AUTOINCREMENT,
    event_id       TEXT NOT NULL UNIQUE,
    event_type     TEXT NOT NULL,
    occurred_at    TEXT NOT NULL,
    run_id         TEXT NOT NULL,
    skill_id       TEXT NOT NULL,
    schema_version INTEGER NOT NULL,
    dedupe_key     TEXT NOT NULL UNIQUE,
    payload        TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_skill_id   ON events(skill_id);
CREATE INDEX IF NOT EXISTS idx_events_run_id     ON events(run_id);
CREATE INDEX IF NOT EXISTS idx_events_type_skill ON events(event_type, skill_id);

CREATE TABLE IF NOT EXISTS runs (
    run_id        TEXT PRIMARY KEY,
    started_at    TEXT NOT NULL,
    finished_at   TEXT,
    cost_cap_usd  REAL,
    cost_used_usd REAL DEFAULT 0,
    cli_args      TEXT
);

CREATE TABLE IF NOT EXISTS skills_current (
    skill_id          TEXT PRIMARY KEY,
    repo_url          TEXT NOT NULL,
    last_extracted_at TEXT,
    content_hash      TEXT,
    frontmatter       TEXT,
    last_seq          INTEGER NOT NULL
);

CREATE TABLE IF NOT EXISTS evals_current (
    skill_id          TEXT NOT NULL,
    evaluator         TEXT NOT NULL,
    evaluator_version TEXT NOT NULL,
    score             REAL,
    sub_scores        TEXT,
    findings          TEXT,
    status            TEXT NOT NULL,
    completed_at      TEXT,
    cost_usd          REAL DEFAULT 0,
    PRIMARY KEY (skill_id, evaluator, evaluator_version)
);
CREATE INDEX IF NOT EXISTS idx_evals_status ON evals_current(status);
