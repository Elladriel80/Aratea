**Run 1047 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 29, 2026?
Bin cible : `KXLOWTNYC-26OCT29-B47.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.409, Brier=0.1670, P&L réel=$-137.12
- `learned_v2` (challenger) — p_yes=0.261, Brier=0.0682, P&L théorique=$-137.12
- `kalshi_mid_baseline` (baseline) — p_yes=0.125, Brier=0.0156, P&L théorique=$-137.12 ⭐

Verdict run 1047 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1047/report.json
