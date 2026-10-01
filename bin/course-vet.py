#!/usr/bin/env python3
"""course-vet.py — validate a herdr-lab course against the herdr-lab/course.v1 format.

One command, run BEFORE teaching or quiz mode (SKILL.md §6/§7 vet-first rule):

    course-vet.py <course-dir>              # structural vet: manifest, lessons, quizzes, steps
    course-vet.py <course-dir> --rehearse   # + require steps.json 'recorded' evidence and
                                            #   verify it contains the expected fragments

Checks performed:
  * course.yaml parses, matches course.schema.v1.json, and every listed lesson
    dir exists with a frontmatter-complete README.md (id/module/title/objectives)
  * every lesson dir on disk is either manifest-listed or reported as an
    orphan warning; frontmatter 'module' values must resolve to the manifest
  * steps.json matches steps.schema.v1.json; silent/output_fragment consistency;
    --rehearse additionally requires each step to carry a 'recorded' transcript
    containing at least one expected output_fragment
  * quiz-<id>.json matches quiz.schema.v1.json, schema string is right,
    mcq/preview items have exactly one correct option, multi at least one,
    'short' items are gradable (answer_key) and only short items may carry
    accepted_synonyms, task items carry task_id, and the 2026-09-25 option-
    position anti-pattern is audited across consecutive optioned items
  * quiz items[].objectives must be a subset of the lesson's declared
    objectives (error on unknown, warning-only on untested)
  * frontmatter 'deck:' (§10) points at an existing file with no leftover
    'Template Reference' slides, and every data-step resolves to a
    steps.json step id (unslided steps are a warning)

Exit 0 = vetted; 1 = errors found; 2 = couldn't start (missing files/deps).

Dependencies: PyYAML (required), jsonschema (optional — absent, a structural
fallback covers schema/version/required-field invariants). Read-only by
design: the script never fetches and never executes lesson commands — live
rehearsal stays the agent-driven §6 hidden-tab recipe, not a script runner.
"""

from __future__ import annotations

import argparse
from html import unescape
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # skill root (bin/ is a sibling of the schemas)

try:
    import yaml
except ImportError:
    sys.exit("course-vet.py: PyYAML required: `uv pip install pyyaml` (or pip install pyyaml)")

try:
    import jsonschema

    _HAS_JSONSCHEMA = True
except ImportError:
    _HAS_JSONSCHEMA = False

SCHEMA_CONST_REQUIRED = {
    "course.schema.v1.json": ("herdr-lab/course.v1", ["schema", "name", "modules"]),
    "steps.schema.v1.json": ("herdr-lab/steps.v1", ["schema", "lesson_id", "steps"]),
    "quiz.schema.v1.json": ("herdr-lab/quiz.v1", ["schema", "title", "items"]),
}


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def err(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)

    def dump(self) -> bool:
        for w in self.warnings:
            print(f"  WARN  {w}")
        for e in self.errors:
            print(f"  ERROR {e}")
        if not self.errors and not self.warnings:
            print("  (no issues)")
        return bool(self.errors)


def load_schema(name: str) -> dict:
    path = HERE / name
    if not path.is_file():
        sys.exit(f"course-vet.py: cannot find {name} next to bin/ — run from the herdr-lab repo layout")
    return json.loads(path.read_text(encoding="utf-8"))


def schema_check(schema_name: str, doc: object, where: str, rep: Report) -> None:
    if _HAS_JSONSCHEMA:
        for e in sorted(jsonschema.Draft202012Validator(load_schema(schema_name)).iter_errors(doc),
                        key=lambda x: list(x.absolute_path)):
            loc = ".".join(str(p) for p in e.absolute_path) or "(root)"
            rep.err(f"{where}: schema violation at {loc}: {e.message}")
    const, required = SCHEMA_CONST_REQUIRED[schema_name]
    if isinstance(doc, dict):
        if doc.get("schema") != const:
            rep.err(f"{where}: schema string {doc.get('schema')!r} != {const!r}")
        for k in required:
            if k not in doc:
                rep.err(f"{where}: missing required field {k!r}")
    else:
        rep.err(f"{where}: top-level must be an object")


def read_frontmatter(path: Path) -> dict | None:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end == -1:
        return None
    try:
        return yaml.safe_load(text[3:end]) or {}
    except yaml.YAMLError as e:
        return {"__parse_error__": f"YAML error in frontmatter: {e}"}


def listed_slugs(course_dir: Path) -> list[str]:
    try:
        manifest = yaml.safe_load((course_dir / "course.yaml").read_text(encoding="utf-8"))
        return [l for mod in manifest["modules"] for l in mod["lessons"]]
    except Exception:
        return []


def vet_course(course_dir: Path, rehearse: bool, rep: Report) -> None:
    manifest_path = course_dir / "course.yaml"
    if not manifest_path.is_file():
        rep.err(f"{course_dir}: no course.yaml manifest (format: SKILL.md §6 'Course format contract')")
        return
    try:
        manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        rep.err(f"course.yaml: YAML parse error: {exc}")
        return
    schema_check("course.schema.v1.json", manifest, "course.yaml", rep)
    if rep.errors:
        return  # the manifest is the spine; don't vet lessons against a broken one

    lessons_dir = course_dir / "lessons"
    if not lessons_dir.is_dir():
        rep.err(f"{course_dir}: no lessons/ directory next to course.yaml")
        return

    shell = manifest.get("shell", "bash")
    passing = manifest.get("passing_score", 0.8)
    on_disk = {d.name for d in lessons_dir.iterdir() if d.is_dir()}
    listed = [l for m in manifest["modules"] for l in m["lessons"]]

    dupes = sorted({l for l in listed if listed.count(l) > 1})
    if dupes:
        rep.err(f"course.yaml: duplicate lesson entries: {dupes}")

    for slug in sorted(on_disk - set(listed)):
        rep.warn(f"course.yaml: lesson '{slug}' exists on disk but is not manifest-listed (orphan — not teachable)")
    for slug in set(listed) - on_disk:
        rep.err(f"course.yaml: lesson '{slug}' is manifest-listed but lessons/{slug}/ does not exist")

    module_ids = {m["id"] for m in manifest["modules"]}
    for slug in sorted(on_disk & set(listed)):
        vet_lesson(course_dir, lessons_dir / slug, slug, module_ids, shell, passing, rehearse, rep)


def vet_lesson(
    course_dir: Path,
    lesson_dir: Path,
    slug: str,
    module_ids: set[str],
    shell: str,
    passing: float,
    rehearse: bool,
    rep: Report,
) -> None:
    where = f"lessons/{slug}"
    readme = lesson_dir / "README.md"
    if not readme.is_file():
        rep.err(f"{where}: README.md missing")
        return

    fm = read_frontmatter(readme)
    if fm is None:
        rep.err(f"{where}/README.md: no YAML frontmatter block — required by vet (id, module, title, objectives)")
        return
    if "__parse_error__" in fm:
        rep.err(f"{where}/README.md: {fm['__parse_error__']}")
        return
    if str(fm.get("status") or "").startswith("skeleton"):
        rep.err(
            f"{where}/README.md: lesson skeleton unfilled (frontmatter status: {fm['status']!r}) —"
            " fill README/exercises/steps/quiz from the source before teaching (vet-first rule)"
        )
        return  # one clean fill-first error per skeleton lesson; deeper checks are noise until it is filled
    for field in ("id", "title", "objectives"):
        if not fm.get(field):
            rep.err(f"{where}/README.md: frontmatter missing/wrong value for {field!r}")
    if isinstance(fm.get("objectives"), str):
        rep.err(f"{where}/README.md: objectives must be a YAML list, not a bare string")
        return
    if fm.get("id") and fm["id"] != slug:
        rep.err(f"{where}/README.md: frontmatter id {fm['id']!r} != directory slug {slug!r}")
    mod = fm.get("module")
    if mod and mod not in module_ids:
        rep.err(f"{where}/README.md: frontmatter module {mod!r} not declared in course.yaml modules[]")
    slug_set = set(listed_slugs(course_dir))
    for p in fm.get("prerequisites") or []:
        if str(p) not in slug_set:
            rep.warn(f"{where}: prerequisite lesson {p!r} not in the manifest")

    # steps.json — the §6 gate contract
    steps_file = lesson_dir / "steps.json"
    if steps_file.is_file():
        try:
            steps = json.loads(steps_file.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            rep.err(f"{where}/steps.json: invalid JSON: {exc}")
            return
        schema_check("steps.schema.v1.json", steps, f"{where}/steps.json", rep)
        steps_id, fm_id = steps.get("lesson_id"), fm.get("id")
        if fm_id and steps_id and steps_id != fm_id:
            rep.err(f"{where}/steps.json: lesson_id {steps_id!r} != frontmatter id {fm_id!r}")
        vet_steps(steps, lesson_dir, where, rehearse, rep)
    else:
        steps = None
        rep.warn(f"{where}: no steps.json — §6 step-(b) evidence check stays LLM-judged (allowed, not ideal)")

    # deck.html — the §10 slide deck (html-template-pack slide template)
    if fm.get("deck"):
        vet_deck(lesson_dir / str(fm["deck"]), steps, where, rep)

    # quizzes
    if fm.get("quiz") and not list(lesson_dir.glob("quiz-*.json")):
        rep.err(f"{where}: frontmatter quiz:{fm['quiz']!r} but no quiz-*.json on disk")
    for qf in sorted(lesson_dir.glob("quiz-*.json")):
        vet_quiz(qf, lesson_dir, fm, passing, shell, rep)


def vet_deck(deck: Path, steps: dict | None, where: str, rep: Report) -> None:
    if not deck.is_file():
        rep.err(f"{where}: frontmatter deck:{deck.name!r} but the file is missing")
        return
    html = deck.read_text(encoding="utf-8")
    if "Template Reference" in html:
        rep.err(f"{where}/{deck.name}: html-template-pack 'Template Reference' slides left in — delete them (§10)")
    step_list = (steps or {}).get("steps", [])
    step_ids = {s.get("id") for s in step_list}
    deck_ids = set(re.findall(r'data-step="([^"]+)"', html))
    # accept[] is exact-match: a student copying the slide's command must pass "check task <id>"
    for s in step_list:
        m = re.search(rf'<section[^>]*data-step="{re.escape(str(s.get("id")))}".*?</section>', html, re.S)
        lines = {ln.strip() for c in re.findall(r"<code>(.*?)</code>", m.group(0) if m else "", re.S)
                 for ln in unescape(c).splitlines()}
        if m and not lines & set(s.get("accept", [])):
            rep.warn(f"{where}/{deck.name}: slide for {s['id']!r} shows no accept[] form verbatim — "
                     "a student copying it would fail the evidence check")
    for sid in sorted(deck_ids - step_ids):
        rep.err(f"{where}/{deck.name}: data-step {sid!r} has no matching steps.json step id")
    for sid in sorted(step_ids - deck_ids):
        rep.warn(f"{where}/{deck.name}: steps.json step {sid!r} has no practice slide (data-step)")


def vet_steps(steps: dict, lesson_dir: Path, where: str, rehearse: bool, rep: Report) -> None:
    seen_ids: set[str] = set()
    for i, st in enumerate(steps.get("steps") or []):
        sid = st.get("id")
        label = f"{where}/steps.json[{sid or f'idx{i}'}]"
        if not sid or not str(sid).strip():
            rep.err(f"{label}: missing id")
            continue
        if sid in seen_ids:
            rep.err(f"{label}: duplicate step id")
        seen_ids.add(sid)

        accepts = st.get("accept") or []
        if not accepts:
            rep.err(f"{label}: needs at least one accepted command form in 'accept'")
        if any(not a.strip() for a in accepts):
            rep.err(f"{label}: whitespace-only entry in 'accept'")

        silent = bool(st.get("silent", False))
        frag = st.get("output_fragment") or []
        if silent and frag:
            rep.err(f"{label}: silent:true conflicts with output_fragment{frag}")
        if not silent and not frag:
            rep.warn(f"{label}: neither output_fragment nor silent — gate proof is command-match only")

        rec = st.get("recorded")
        if not rec:
            (rep.err if rehearse else rep.warn)(
                f"{label}: no 'recorded' rehearsal evidence"
                + (" — --rehearse demands it (run the §6 hidden-tab recipe first)" if rehearse else " (optional)")
            )
            continue
        rec_path = lesson_dir / str(rec)
        if not rec_path.is_file():
            (rep.err if rehearse else rep.warn)(f"{label}: recorded file {rec!r} not found")
            continue
        if frag:
            text = rec_path.read_text(encoding="utf-8", errors="replace")
            missing = [f for f in frag if f not in text]
            if len(missing) == len(frag):
                (rep.err if rehearse else rep.warn)(
                    f"{label}: recorded {rec!r} contains none of the expected fragments {frag}"
                )


def vet_quiz(qf: Path, lesson_dir: Path, fm: dict, passing: float, shell: str, rep: Report) -> None:
    where = f"lessons/{lesson_dir.name}/{qf.name}"
    try:
        doc = json.loads(qf.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        rep.err(f"{where}: invalid JSON: {exc}")
        return
    if _HAS_JSONSCHEMA:
        for e in sorted(jsonschema.Draft202012Validator(load_schema("quiz.schema.v1.json")).iter_errors(doc),
                        key=lambda x: list(x.absolute_path)):
            loc = ".".join(str(p) for p in e.absolute_path) or "(root)"
            rep.err(f"{where}: schema violation at {loc}: {e.message}")

    lesson_objectives = set(fm.get("objectives") or [])
    tagged: set[str] = set()
    optioned_pos: list[int | None] = []  # correct-option index per optioned item, in order

    for i, item in enumerate(doc.get("items") or []):
        where_i = f"{where} item[{i}]"
        kind = item.get("kind")
        options = item.get("options") or []

        if item.get("accepted_synonyms") and kind != "short":
            rep.err(f"{where_i}: accepted_synonyms only valid on 'short' items (kind={kind!r})")
        if kind == "short" and not item.get("answer_key"):
            rep.err(f"{where_i}: 'short' item without answer_key is ungradable")
        if kind == "task" and not item.get("task_id"):
            rep.err(f"{where_i}: 'task' item without task_id")

        unknown = [o for o in item.get("objectives") or [] if o not in lesson_objectives]
        if unknown:
            rep.err(f"{where_i}: objectives {unknown} not declared in {lesson_dir.name}'s frontmatter")
        tagged.update(item.get("objectives") or [])

        if kind in ("mcq", "preview"):
            correct = [j for j, o in enumerate(options) if o.get("correct")]
            if len(correct) != 1:
                rep.err(f"{where_i}: {kind} needs exactly one option with correct:true (found {len(correct)})")
            elif len(options) >= 2:
                optioned_pos.append(correct[0])
        elif kind == "multi":
            if not any(o.get("correct") for o in options):
                rep.err(f"{where_i}: multi needs at least one option with correct:true")
            optioned_pos.append(None)

    for k in range(1, len(optioned_pos)):
        if optioned_pos[k] is not None and optioned_pos[k] == optioned_pos[k - 1]:
            rep.warn(
                f"{where}: consecutive optioned items {k - 1} and {k} both place the correct option at index"
                f" {optioned_pos[k]} — vary the position (2026-09-25 anti-pattern)"
            )

    untested = sorted(o for o in lesson_objectives if o not in tagged)
    if untested:
        rep.warn(f"{where}: objectives {untested} are tagged by no quiz item (coverage warning only)")

    if shell == "fish":
        for i, item in enumerate(doc.get("items") or []):
            blob = str(item.get("instruction") or "") + str(item.get("q") or "")
            if "$(" in blob or "$?" in blob:
                rep.warn(f"{where} item[{i}]: bash syntax in text but course shell is fish ($status / set VAR val)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Course vet for the herdr-lab hlab-course.v1 format (see SKILL.md §6/§7)")
    ap.add_argument("course_dir", help="course directory containing course.yaml")
    ap.add_argument("--rehearse", action="store_true", help="require and verify steps.json 'recorded' evidence")
    ap.add_argument("--quiet", action="store_true", help="suppress 'no issues' line")
    args = ap.parse_args()

    course_dir = Path(args.course_dir)
    if not course_dir.is_dir():
        print(f"course-vet.py: {course_dir} is not a directory")
        return 2

    rep = Report()
    vet_course(course_dir, args.rehearse, rep)
    failed = rep.dump()
    status = "FAIL" if failed else "PASS ✓"
    print(f"course-vet: {status}  (jsonschema: {'yes' if _HAS_JSONSCHEMA else 'fallback structural checks'})")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())