**Run 1120 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Nov 7, 2026?
Bin cible : `KXLOWTMIA-26NOV07-B69.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.256, Brier=0.0656, P&L réel=$-125.46
- `learned_v2` (challenger) — p_yes=0.361, Brier=0.1303, P&L théorique=$-125.46
- `kalshi_mid_baseline` (baseline) — p_yes=0.045, Brier=0.0020, P&L théorique=$-125.46 ⭐

Verdict run 1120 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1120/report.json
