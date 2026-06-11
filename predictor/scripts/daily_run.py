"""Routine quotidienne autonome : fetch markets → forward predict → score résolus.

Lancée chaque jour à heure fixe par la skill `schedule`. Idempotente :
- Si un step échoue, les autres tournent quand même.
- Toutes les sorties sont stockées disque (pas de perte si le run plante).
- Trace stdout structurée pour debug a posteriori.

Usage manuel :
    python scripts/daily_run.py

Exit code : 0 si tous les steps OK, 1 si au moins un step a planté
(mais on continue quand même les suivants).
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
            # daily_auto, sinon le job est tué AVANT que le step échoue
            # proprement et daily_auto + manifest + push ne tournent jamais
            # (site figé du 8 au 11 juin 2026, runs 34-35 cancelled à 25 min).
            # Le 11 juin, un plafond uniforme de 13 min a tué forward_predict
            # (~16 min en conditions réelles) : d'où les budgets différenciés.
            timeout=60 * timeout_min,
        )
        ok = result.returncode == 0
        print(f"  → exit code: {result.returncode} ({'OK' if ok else 'FAIL'})")
        return ok
    except subprocess.TimeoutExpired:
        print(f"  → TIMEOUT après {timeout_min} min")
        return False
    except Exception:
        print(f"  → EXCEPTION:")
        traceback.print_exc()
        return False


def main() -> int:
    started_at = datetime.now(timezone.utc)
    print(f"daily_run start @ {started_at.isoformat()}")
    print(f"working dir : {ROOT}")

    py = sys.executable

    steps = [
        # `--all-weather` est requis : sans ce flag, fetch_markets écrit
        # seulement un summary et ne refresh PAS les snapshots des markets,
        # donc forward_predict bosse sur des données 2-3 jours obsolètes.
        # Cf. bug détecté le 2026-05-10 (predictions sur target_date passé).
        # Budgets : somme = 40 min < 50 min de job CI (− setup − daily_auto).
        # fetch_markets et score_forward tournent en ~1 min ; forward_predict
        # itère sur tous les markets avec des APIs throttlées (NDFD 1 req/s)
        # → ~16 min observées le 8 juin, 30 min de marge.
        ("fetch_markets",   [py, str(SCRIPTS / "fetch_markets.py"), "--all-weather"], 5),
        ("forward_predict", [py, str(SCRIPTS / "forward_predict.py")], 30),
        # Le score essaie de récupérer les résolutions Kalshi pour les markets
        # capturés les jours précédents. C'est ce qui ferme la boucle.
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
