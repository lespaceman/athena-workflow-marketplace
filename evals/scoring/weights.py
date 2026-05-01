DEFAULT_WEIGHTS: dict[str, float] = {
    "health": 0.25,
    "provenance": 0.25,
    "compliance": 0.30,
    "security": 0.20,
}

TIER_THRESHOLDS: list[tuple[str, float]] = [
    ("S", 90.0),
    ("A", 80.0),
    ("B", 70.0),
    ("C", 60.0),
    ("D", 0.0),
]

BUCKET_EVALUATORS: dict[str, tuple[str, ...]] = {
    "health": ("repo-health", "release-cadence"),
    "provenance": ("follower-authenticity", "contributor-authenticity"),
    "compliance": ("compliance-check", "cross-runtime", "live-validator", "report-quality"),
    "security": ("security-scan",),
}
