"""Routine quotidienne autonome : fetch markets -> forward predict -> score resolus.

Lancee chaque jour a heure fixe par la skill `schedule`. Idempotente :
- Si un step echoue, les autres tournent quand meme.
- Toutes les sorties sont stockees disque (pas de perte si le run plante).
- Trace stdout structuree pour debug a posteriori.

Usage manuel :
    python scripts/daily_run.py

Exit code : 0 si tous les steps OK, 1 si au moins un step a plante
(mais on continue quand meme les suivants).
"""
from __future__ import annotations

import subprocess
import sys
import traceback
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SCRIPTS = ROOT / "scripts"

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


def run_step(name: str, cmd: list[str], timeout_min: int) -> bool:
    print(f"\n{'=' * 70}")
    print(f"[STEP] {name} (timeout {timeout_min} min)")
    print(f"  cmd : {' '.join(cmd)}")
    print(f"  at  : {datetime.now(timezone.utc).isoformat()}")
    print("-" * 70)
    try:
        result = subprocess.run(
            cmd, cwd=str(ROOT), check=False,
            # Budgets par step (voir main()) : la somme des timeouts DOIT
            # rester < timeout-minutes du job CI (50 min) moins setup et
            # daily_auto, sinon le job est tue AVANT que le step echoue
            # proprement et daily_auto + manifest + push ne tournent jamais
            # (site fige du 8 au 11 juin 2026, runs 34-35 cancelled a 25 min).
            timeout=60 * timeout_min,
        )
        ok = result.returncode == 0
        print(f"  -> exit code: {result.returncode} ({'OK' if ok else 'FAIL'})")
        return ok
    except subprocess.TimeoutExpired:
        print(f"  -> TIMEOUT apres {timeout_min} min")
        return False
    except Exception:
        print(f"  -> EXCEPTION:")
        traceback.print_exc()
        return False


def main() -> int:
    started_at = datetime.now(timezone.utc)
    print(f"daily_run start @ {started_at.isoformat()}")
    print(f"working dir : {ROOT}")

    py = sys.executable

    steps = [
        # `--all-weather` est requis : sans ce flag, fetch_markets ecrit
        # seulement un summary et ne refresh PAS les snapshots des markets,
        # donc forward_predict bosse sur des donnees 2-3 jours obsoletes.
        # Cf. bug detecte le 2026-05-10 (predictions sur target_date passe).
        ("fetch_markets",   [py, str(SCRIPTS / "fetch_markets.py"), "--all-weather"], 5),
        # forward_predict recoit un BUDGET LOGICIEL de 26 min (1560s) : il
        # s'arrete proprement et ecrit le carburant deja produit AVANT le kill
        # dur de 30 min ci-dessous (qui ne sert plus que de filet ultime).
        # Fini la perte de 100 % du carburant au timeout (gel du 9-16 juin 2026).
        ("forward_predict", [py, str(SCRIPTS / "forward_predict.py"),
                             "--time-budget-seconds", "1560"], 30),
        # Le score essaie de recuperer les resolutions Kalshi pour les markets
        # captures les jours precedents. C'est ce qui ferme la boucle.
        ("score_forward",   [py, str(SCRIPTS / "score_forward.py")], 5),
    ]

    results: dict[str, bool] = {}
    for name, cmd, timeout_min in steps:
        results[name] = run_step(name, cmd, timeout_min)

    print(f"\n{'=' * 70}")
    print("SUMMARY")
    for name, ok in results.items():
        print(f"  {name:<20} {'OK' if ok else 'FAIL'}")
    duration = (datetime.now(timezone.utc) - started_at).total_seconds()
    print(f"  total duration   : {duration:.1f}s")

    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
