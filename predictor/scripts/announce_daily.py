#!/usr/bin/env python3
"""announce_daily.py — annonce Discord des captures et résolutions du jour.

Conçu pour tourner dans daily-trading.yml APRÈS daily_auto.py et AVANT le
commit : il détecte via `git status --porcelain` ce que daily_auto vient
d'écrire dans le working tree, et poste deux digests :

  - nouvelles captures (nouveau dossier predictor/runs/NNN/)
        → #predictions  (env DISCORD_WEBHOOK_PREDICTIONS)
  - résolutions (nouveau POST_RUN.md dans un run existant)
        → #pnl-tracker  (env DISCORD_WEBHOOK_PNL_TRACKER)

Pourquoi ce script existe : les annonces par run étaient déclenchées par
les tags `run-NNN` manuels (CONVENTION §4). Quand daily_auto a automatisé
la capture (fin mai 2026), plus personne n'a créé de tags et #predictions /
#pnl-tracker sont restés muets. Ce script ferme ce trou.

Garde-fous :
  - webhook absent → warning GitHub Actions visible (::warning::) + exit 0,
    jamais d'échec silencieux invisible NI de step rouge bloquant ;
  - toute erreur Discord → exit 1, mais le step CI est continue-on-error :
    le commit/push du manifest passe TOUJOURS avant la communication
    (leçon du gel du 8-11 juin 2026) ;
  - un digest par channel (pas un message par run) pour ne pas spammer.

Usage : python predictor/scripts/announce_daily.py [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent   # predictor/
REPO = ROOT.parent                               # racine du repo
RUNS = ROOT / "runs"

sys.path.insert(0, str(ROOT / "scripts"))
from post_to_discord import post, truncate  # noqa: E402  (stdlib only)

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def git_porcelain() -> list[str]:
    out = subprocess.run(
        ["git", "status", "--porcelain", "--", "predictor/runs"],
        cwd=str(REPO), capture_output=True, text=True, check=True,
    )
    return [line for line in out.stdout.splitlines() if line.strip()]


def detect_changes() -> tuple[list[str], list[str]]:
    """→ (run_ids capturés, run_ids résolus), triés numériquement."""
    captured: set[str] = set()
    resolved: set[str] = set()
    for line in git_porcelain():
        status, path = line[:2], line[3:].strip().strip('"')
        m = re.match(r"predictor/runs/(\d+)(/|$)", path)
        if not m:
            continue
        run_id = m.group(1)
        if status.strip() == "??":
            # dossier entier nouveau (`?? predictor/runs/206/`) = capture ;
            # POST_RUN.md nouveau dans un run déjà tracké = résolution.
            if path.rstrip("/").endswith("POST_RUN.md"):
                resolved.add(run_id)
            else:
                captured.add(run_id)
    captured -= resolved
    key = lambda s: int(s)  # noqa: E731
    return sorted(captured, key=key), sorted(resolved, key=key)


def load_report(run_id: str) -> dict | None:
    p = RUNS / run_id / "report.json"
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        print(f"  !! report illisible pour run {run_id}: {e}")
        return None


def fmt_capture_line(run_id: str, r: dict) -> str:
    mkt = (r.get("markets") or [{}])[0]
    pos = mkt.get("champion_position") or {}
    snap = mkt.get("snapshot_pre") or {}
    champion = r.get("champion_at_time_of_run")
    p_yes = next(
        (m.get("p_yes") for m in r.get("models", []) if m.get("name") == champion),
        None,
    )
    ticker = mkt.get("ticker", "?")
    side = pos.get("side", "?")
    p_txt = f"{p_yes * 100:.0f}%" if isinstance(p_yes, (int, float)) else "?"
    mid = snap.get("yes_mid")
    mid_txt = f"{mid * 100:.0f}%" if isinstance(mid, (int, float)) else "?"
    return f"`{run_id}` {ticker} — **{side}** (modèle {p_txt} vs marché {mid_txt})"


def fmt_resolution_line(run_id: str, r: dict) -> tuple[str, float]:
    mkt = (r.get("markets") or [{}])[0]
    res = mkt.get("resolution") or {}
    pnl = res.get("champion_pnl_usd")
    won = res.get("champion_won")
    ticker = mkt.get("ticker", "?")
    icon = "✅" if won else "❌"
    pnl_f = float(pnl) if isinstance(pnl, (int, float)) else 0.0
    sign = "+" if pnl_f >= 0 else "−"
    return f"{icon} `{run_id}` {ticker} — {sign}${abs(pnl_f):.2f}", pnl_f


def build_digest(header: str, lines: list[str], footer: str = "") -> str:
    body = header + "\n" + "\n".join(lines)
    if footer:
        body += "\n" + footer
    if len(body) > 1900:  # garde la place pour la troncature de post()
        kept: list[str] = []
        for line in lines:
            candidate = header + "\n" + "\n".join(kept + [line]) + "\n" + footer
            if len(candidate) > 1850:
                kept.append(f"… +{len(lines) - len(kept)} autres (voir le dashboard)")
                break
            kept.append(line)
        body = header + "\n" + "\n".join(kept) + ("\n" + footer if footer else "")
    return truncate(body)


def send(channel_env: str, content: str, dry_run: bool) -> bool:
    url = os.environ.get(channel_env, "").strip()
    if not url:
        # Visible dans l'UI GitHub Actions — JAMAIS de skip invisible
        # (c'est un skip silencieux de ce genre qui a masqué le webhook
        # recap pendant un mois).
        print(f"::warning::{channel_env} non défini — annonce Discord sautée.")
        return False
    if dry_run:
        print(f"--- DRY RUN → {channel_env} ---\n{content}\n---")
        return True
    post(url, content)
    print(f"Posté sur {channel_env} ({len(content)} chars).")
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dry-run", action="store_true",
                        help="Affiche les messages sans poster")
    args = parser.parse_args()

    captured, resolved = detect_changes()
    print(f"Détecté : {len(captured)} capture(s), {len(resolved)} résolution(s).")
    if not captured and not resolved:
        print("Rien à annoncer aujourd'hui.")
        return 0

    dashboard = "https://aratea-app.vercel.app/predictor"

    if captured:
        lines = []
        for rid in captured:
            r = load_report(rid)
            if r:
                lines.append(fmt_capture_line(rid, r))
        if lines:
            msg = build_digest(
                f"📡 **{len(lines)} nouvelle(s) position(s) paper** — "
                f"champion vs marché :",
                lines,
                f"Détail et Brier : {dashboard}",
            )
            send("DISCORD_WEBHOOK_PREDICTIONS", msg, args.dry_run)

    if resolved:
        lines, total = [], 0.0
        for rid in resolved:
            r = load_report(rid)
            if r:
                line, pnl = fmt_resolution_line(rid, r)
                lines.append(line)
                total += pnl
        if lines:
            sign = "+" if total >= 0 else "−"
            msg = build_digest(
                f"💰 **{len(lines)} résolution(s)** — P&L paper du lot : "
                f"**{sign}${abs(total):.2f}**",
                lines,
                f"Ledger complet : {dashboard}",
            )
            send("DISCORD_WEBHOOK_PNL_TRACKER", msg, args.dry_run)

    return 0


if __name__ == "__main__":
    sys.exit(main())
