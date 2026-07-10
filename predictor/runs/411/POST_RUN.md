**Run 411 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 9, 2026?
Bin cible : `KXLOWTNYC-26JUL09-B71.5` · Outcome : YES · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.434, Brier=0.3204, P&L réel=$+201.39 ⭐
- `learned_v2` (challenger) — p_yes=0.311, Brier=0.4742, P&L théorique=$+201.39
- `kalshi_mid_baseline` (baseline) — p_yes=0.265, Brier=0.5402, P&L théorique=$+201.39

Verdict run 411 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/411/report.json
