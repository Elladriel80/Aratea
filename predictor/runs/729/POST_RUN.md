**Run 729 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Sep 15, 2026?
Bin cible : `KXHIGHTDC-26SEP15-B81.5` · Outcome : NO · Low observée (bin gagnant) : ≤79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.282, Brier=0.0793, P&L réel=$-13.86
- `learned_v2` (challenger) — p_yes=0.446, Brier=0.1991, P&L théorique=$-13.86
- `kalshi_mid_baseline` (baseline) — p_yes=0.110, Brier=0.0121, P&L théorique=$-13.86 ⭐

Verdict run 729 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/729/report.json
