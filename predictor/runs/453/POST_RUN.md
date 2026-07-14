**Run 453 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 13, 2026?
Bin cible : `KXLOWTCHI-26JUL13-B69.5` · Outcome : YES · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.495, Brier=0.2550, P&L réel=$-83.83
- `learned_v2` (challenger) — p_yes=0.406, Brier=0.3523, P&L théorique=$-83.83
- `kalshi_mid_baseline` (baseline) — p_yes=0.585, Brier=0.1722, P&L théorique=$-83.83 ⭐

Verdict run 453 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/453/report.json
