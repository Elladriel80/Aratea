**Run 694 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Sep 11, 2026?
Bin cible : `KXHIGHTDC-26SEP11-B86.5` · Outcome : NO · Low observée (bin gagnant) : 82-83°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.156, Brier=0.0244, P&L réel=$-60.48
- `learned_v2` (challenger) — p_yes=0.281, Brier=0.0789, P&L théorique=$-60.48
- `kalshi_mid_baseline` (baseline) — p_yes=0.105, Brier=0.0110, P&L théorique=$-60.48 ⭐

Verdict run 694 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/694/report.json
