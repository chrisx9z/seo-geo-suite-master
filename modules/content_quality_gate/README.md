# Content Quality Gate (MANDATORY, ON BY DEFAULT)

Every publishing pipeline calls `enforce_publish_payload()` right before
`POST /wp-json/wp/v2/posts`. There is **no bypass flag**.

| Pipeline | Site(s) | Hook |
|---|---|---|
| `wp_ai_autopilot/autopilot_orchestrator.py` | nhatthegioi, vibemmo (via their batch schedulers) | `produce_and_publish()` → returns `status=blocked_junk` |
| `travel_scheduler/travel_batch_scheduler.py` | mmdidau, tobeigo | `schedule_single_post()` → returns `None` |
| `travel_scheduler/english_batch_scheduler.py` | triptip | `schedule_single_post()` → returns `None` |

## The gate blocks (post is never published)
- Mad-Libs boilerplate: fake "Guinness", "Vị trí Quán Quân", generic
  "Khám phá toàn diện về <keyword> với đầy đủ số liệu" shells, generic step templates.
- Title and body that don't match: the body covers < 60% of the keyword tokens,
  or none of the keyword tokens appear in any heading.
- "Top N" titles with no list behind them.
- Vietnamese political content or images (city name "TP. Hồ Chí Minh" is still allowed).
- Thin content (< 600 words) or > 15% repeated sentences.
- Text-only placeholder images.

## The gate auto-repairs
- Paragraphs with geography copied from another destination (e.g. "cách trung tâm
  thủ đô không quá xa" on a Phú Quốc post, "núi đá vôi triệu năm tuổi" on a café post).
- Bad slugs → short keyword slugs (ASCII, ≤ 7 words, no year, no `038`, no dangling
  words). Slugs that are already valid are left alone, so URLs don't change for no reason.

## Cleaning up existing posts
```bash
python -m modules.content_quality_gate.audit_cli --site all            # report only -> reports/quality_gate_<site>.json
python -m modules.content_quality_gate.audit_cli --site mmdidau --apply
```
With `--apply`, junk posts are moved to **draft** (you can undo this), and slugs are
renamed. WordPress keeps the old slug in `_wp_old_slug`, so old URLs 301-redirect.

Tests: `python -m pytest tests/test_content_quality_gate.py`
