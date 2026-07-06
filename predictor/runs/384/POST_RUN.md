**Run 384 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 5, 2026?
Bin cible : `KXLOWTCHI-26JUL05-B68.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.392, Brier=0.1538, P&L réel=$-79.42
- `learned_v2` (challenger) — p_yes=0.215, Brier=0.0462, P&L théorique=$-79.42 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.225, Brier=0.0506, P&L théorique=$-79.42

Verdict run 384 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/384/report.json
