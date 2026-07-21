**Run 508 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 20, 2026?
Bin cible : `KXLOWTCHI-26JUL20-B64.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.528, Brier=0.2789, P&L réel=$-7.54
- `learned_v2` (challenger) — p_yes=0.468, Brier=0.2189, P&L théorique=$-7.54
- `kalshi_mid_baseline` (baseline) — p_yes=0.260, Brier=0.0676, P&L théorique=$-7.54 ⭐

Verdict run 508 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/508/report.json
