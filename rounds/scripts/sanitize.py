"""sanitize.py — prompt-injection mitigations for valuation agent inputs (P4-3).

Hard rule: every untrusted text field that flows from GitHub (PR title/body,
commit messages, issue title/body, review body, branch names) MUST pass through
``sanitize_field`` before being embedded in the agent prompt.

Three layers, applied in order:

1. **Truncate**  — cap each field at ``max_len`` characters (default 500). This
   shrinks the attack surface and the cost of low-information inputs.
2. **Detect**    — scan for known injection patterns and return them as
   ``flags``. The agent caller MUST surface flags as ``STATUS:
   PROMPT_INJECTION_SUSPECTED`` and reduce valuation to 0 for that artifact, per
   PROMPT.md "Suspected fraud" edge case.
3. **XML wrap**  — escape XML specials and wrap in ``<user_content
   field="...">…</user_content>``. The agent's system prompt must treat
   anything inside ``user_content`` as data, never as instructions.

Reference: PROMPT.md v0.2 §"Inviolable rules", §"Edge cases".

Pure stdlib — no extra dependencies.
"""
from __future__ import annotations

import re
from dataclasses import dataclass


# --- Detection -------------------------------------------------------------

# Patterns chosen to be HIGH-precision (false positives are noisy but tolerable;
# false negatives are dangerous). Each regex is anchored on common
# prompt-injection phrasing observed in the wild as of 2026-05.
_INJECTION_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("instruction_override",
     re.compile(r"(?i)\b(ignore|disregard|forget)\s+(all\s+|the\s+|any\s+)?"
                r"(previous|prior|above|earlier|preceding)\s+(instructions?|rules?|prompts?)\b")),
    ("role_hijack",
     re.compile(r"(?i)\byou\s+are\s+(now\s+)?(a|an|the)\s+\w+")),
    ("system_marker",
     re.compile(r"(?im)^\s*(system|assistant|user)\s*[:>]\s*")),
    ("xml_role_tag",
     re.compile(r"(?i)<\s*/?\s*(system|user|assistant|prompt|instruction|rule)s?\s*>")),
    ("training_token",
     re.compile(r"<\|[^|>]{1,40}\|>")),
    ("new_instructions",
     re.compile(r"(?i)\b(new|updated|revised)\s+(instructions?|rules?|system\s+prompt)\s*:")),
    ("inviolable_rule_targeting",
     re.compile(r"(?i)\b(inviolable\s+rule|rule\s+\d+)\b.{0,40}\b(is\s+now|has\s+been|no\s+longer|replaced|overridden)\b")),
    ("output_format_hijack",
     re.compile(r"(?i)\b(output|respond|reply|answer)\s+(only\s+|just\s+|exclusively\s+)?"
                r"(in|with|as)\s+(json|yaml|xml|the\s+following)")),
    ("jailbreak_token",
     re.compile(r"(?i)\b(jailbreak|dan\s+mode|developer\s+mode|debug\s+mode)\b")),
    ("valuation_manipulation",
     re.compile(r"(?i)\b(assign|set|grant|award)\s+(me\s+|this\s+pr\s+|this\s+contributor\s+)"
                r"(a\s+|the\s+)?(maximum|max|highest|huge|massive|large)?\s*"
                r"(value|valuation|score|sats|btc)")),
]


@dataclass(frozen=True)
class SanitizedField:
    """Result of sanitizing one untrusted text field."""
    field: str                # logical name e.g. "pr_title", "commit_message"
    wrapped: str              # XML-wrapped, truncated, escaped — safe to embed
    flags: tuple[str, ...]    # injection-pattern names that matched (may be empty)
    truncated: bool           # True if input was over max_len


def detect_injection(text: str) -> list[str]:
    """Return the names of injection patterns that match ``text``.

    Best-effort only (revue 2026-06-10 D3). These regexes are high-precision
    heuristics tuned on English phrasing, NOT a complete filter: a determined
    or non-English injection can slip past. The real barrier is the XML
    wrapping (``_xml_escape`` + ``<user_content>``) plus the system prompt's
    "treat everything inside user_content as data" rule. Detection is
    defense-in-depth / triage, not the security boundary.
    """
    if not text:
        return []
    return [name for name, pat in _INJECTION_PATTERNS if pat.search(text)]


def _xml_escape(text: str) -> str:
    # Échappe aussi " et ' : _xml_escape produit la VALEUR d'attribut
    # field="..." (entre guillemets doubles). Un " non échappé permettrait de
    # sortir de l'attribut et d'injecter d'autres attributs/balises (revue
    # 2026-06-10 D3). & doit rester en premier pour ne pas ré-échapper.
    return (text.replace("&", "&amp;")
                .replace("<", "&lt;")
                .replace(">", "&gt;")
                .replace('"', "&quot;")
                .replace("'", "&#39;"))


def sanitize_field(
    field: str,
    raw: str | None,
    max_len: int = 500,
) -> SanitizedField:
    """Sanitize one untrusted text field for safe inclusion in the agent prompt.

    Args:
        field: logical name of the field (passed through to the XML attribute).
        raw: untrusted text content, possibly None or empty.
        max_len: truncation cap (default 500 chars).

    Returns:
        ``SanitizedField`` with the wrapped, safe-to-embed string plus flags.
    """
    if raw is None or raw == "":
        return SanitizedField(
            field=field,
            wrapped=f'<user_content field="{_xml_escape(field)}"/>',
            flags=(),
            truncated=False,
        )

    flags = tuple(detect_injection(raw))

    truncated = len(raw) > max_len
    body = raw[:max_len]
    if truncated:
        body += "…[TRUNCATED]"

    safe_field = _xml_escape(field)
    safe_body = _xml_escape(body)
    wrapped = f'<user_content field="{safe_field}">{safe_body}</user_content>'
    return SanitizedField(field=field, wrapped=wrapped, flags=flags, truncated=truncated)


def sanitize_artifact(artifact: dict) -> tuple[dict, list[str]]:
    """Sanitize all known untrusted fields on a GitHub artifact dict.

    Returns a new dict with the same shape, where untrusted text fields are
    replaced by their XML-wrapped form, and a list of ``field:pattern`` flags
    across every field. The caller is responsible for raising
    ``STATUS: PROMPT_INJECTION_SUSPECTED`` on the artifact when flags is
    non-empty, per PROMPT.md edge cases.
    """
    untrusted_keys = (
        "title", "body", "commit_message", "branch", "issue_title",
        "issue_body", "review_body",
    )
    out: dict = dict(artifact)
    flags_collected: list[str] = []
    for key in untrusted_keys:
        if key not in artifact:
            continue
        result = sanitize_field(key, artifact[key])
        out[key] = result.wrapped
        flags_collected.extend(f"{key}:{f}" for f in result.flags)
    if flags_collected:
        out["_sanitizer_flags"] = flags_collected
    return out, flags_collected
