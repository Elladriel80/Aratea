**Run 468 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 15, 2026?
Bin cible : `KXLOWTSFO-26JUL15-B57.5` · Outcome : YES · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.333, Brier=0.4446, P&L réel=$+98.91 ⭐
- `learned_v2` (challenger) — p_yes=0.121, Brier=0.7720, P&L théorique=$+98.91
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.5700, P&L théorique=$+98.91

Verdict run 468 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/468/report.json
