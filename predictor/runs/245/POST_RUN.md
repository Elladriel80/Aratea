**Run 245 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Jun 16, 2026?
Bin cible : `KXLOWTCHI-26JUN16-B60.5` · Outcome : YES · Low observée (bin gagnant) : 60-61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.159, Brier=0.7066, P&L réel=$-60.00
- `learned_v2` (challenger) — p_yes=0.211, Brier=0.6229, P&L théorique=$-60.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.250, Brier=0.5625, P&L théorique=$-60.00 ⭐

Verdict run 245 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/245/report.json
