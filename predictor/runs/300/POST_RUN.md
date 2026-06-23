**Run 300 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 22, 2026?
Bin cible : `KXLOWTDEN-26JUN22-B52.5` · Outcome : YES · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.053, Brier=0.8968, P&L réel=$-35.04
- `learned_v2` (challenger) — p_yes=0.110, Brier=0.7920, P&L théorique=$-35.04
- `kalshi_mid_baseline` (baseline) — p_yes=0.270, Brier=0.5329, P&L théorique=$-35.04 ⭐

Verdict run 300 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/300/report.json
