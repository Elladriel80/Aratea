**Run 597 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Aug 1, 2026?
Bin cible : `KXLOWTCHI-26AUG01-B66.5` · Outcome : YES · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.428, Brier=0.3270, P&L réel=$+208.07
- `learned_v2` (challenger) — p_yes=0.672, Brier=0.1072, P&L théorique=$+208.07 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.275, Brier=0.5256, P&L théorique=$+208.07

Verdict run 597 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/597/report.json
