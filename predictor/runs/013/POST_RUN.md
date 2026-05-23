**Run 013 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on May 22, 2026?
Bin cible : `KXLOWTLAX-26MAY22-B61.5` · Outcome : NO · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.269, Brier=0.0723, P&L réel=$-4.83
- `learned_v2` (challenger) — p_yes=0.207, Brier=0.0427, P&L théorique=$-4.83
- `kalshi_mid_baseline` (baseline) — p_yes=0.105, Brier=0.0110, P&L théorique=$-4.83 ⭐

Verdict run 013 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/013/report.json
