from evals.events.models import EvalCompleted, SkillDiscovered


def test_append_returns_true_on_first_write(store, make_discovered):
    assert store.append(make_discovered()) is True


def test_append_is_idempotent_on_dedupe_key(store, make_discovered):
    event = make_discovered()
    assert store.append(event) is True
    assert store.append(event) is False


def test_read_since_returns_events_in_seq_order(store, make_discovered, make_eval_requested):
    e1 = make_discovered(skill_id="a/repo#s")
    e2 = make_eval_requested(skill_id="a/repo#s")
    store.append(e1)
    store.append(e2)

    rows = list(store.read_since(cursor=0))
    assert [seq for seq, _ in rows] == sorted(seq for seq, _ in rows)
    assert [type(ev) for _, ev in rows] == [SkillDiscovered, type(e2)]


def test_read_since_filters_by_type(store, make_discovered, make_eval_completed):
    store.append(make_discovered(skill_id="a/repo#s"))
    store.append(make_eval_completed(skill_id="a/repo#s"))

    rows = list(store.read_since(cursor=0, types=["eval.completed"]))
    assert len(rows) == 1
    assert isinstance(rows[0][1], EvalCompleted)


def test_read_for_skill_only_returns_matching_skill(store, make_discovered):
    store.append(make_discovered(skill_id="a/repo#one"))
    store.append(make_discovered(skill_id="b/repo#two"))

    events = list(store.read_for_skill("a/repo#one"))
    assert len(events) == 1
    assert events[0].skill_id == "a/repo#one"


def test_has_dedupe_key_reflects_appended_events(store, make_discovered):
    event = make_discovered()
    assert store.has_dedupe_key(event.dedupe_key) is False
    store.append(event)
    assert store.has_dedupe_key(event.dedupe_key) is True
