**Run 459 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 14, 2026?
Bin cible : `KXLOWTCHI-26JUL14-B75.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.380, Brier=0.1444, P&L réel=$+83.46
- `learned_v2` (challenger) — p_yes=0.203, Brier=0.0412, P&L théorique=$+83.46 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.535, Brier=0.2862, P&L théorique=$+83.46

Verdict run 459 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/459/report.json
