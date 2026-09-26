**Run 797 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Sep 25, 2026?
Bin cible : `KXLOWTCHI-26SEP25-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.342, Brier=0.4334, P&L réel=$-50.82
- `learned_v2` (challenger) — p_yes=0.134, Brier=0.7499, P&L théorique=$-50.82
- `kalshi_mid_baseline` (baseline) — p_yes=0.395, Brier=0.3660, P&L théorique=$-50.82 ⭐

Verdict run 797 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/797/report.json
