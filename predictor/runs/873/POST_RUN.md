**Run 873 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 5, 2026?
Bin cible : `KXLOWTNYC-26OCT05-B57.5` · Outcome : NO · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.151, Brier=0.0229, P&L réel=$-66.64
- `learned_v2` (challenger) — p_yes=0.189, Brier=0.0358, P&L théorique=$-66.64
- `kalshi_mid_baseline` (baseline) — p_yes=0.045, Brier=0.0020, P&L théorique=$-66.64 ⭐

Verdict run 873 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/873/report.json
