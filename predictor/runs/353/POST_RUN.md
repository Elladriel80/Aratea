**Run 353 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 1, 2026?
Bin cible : `KXLOWTCHI-26JUL01-B77.5` · Outcome : YES · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.207, Brier=0.6291, P&L réel=$-72.00
- `learned_v2` (challenger) — p_yes=0.360, Brier=0.4099, P&L théorique=$-72.00 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.280, Brier=0.5184, P&L théorique=$-72.00

Verdict run 353 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/353/report.json
