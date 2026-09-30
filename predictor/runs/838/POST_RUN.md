**Run 838 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Sep 29, 2026?
Bin cible : `KXHIGHTSFO-26SEP29-B73.5` · Outcome : NO · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.166, Brier=0.0277, P&L réel=$-65.72
- `learned_v2` (challenger) — p_yes=0.287, Brier=0.0823, P&L théorique=$-65.72
- `kalshi_mid_baseline` (baseline) — p_yes=0.055, Brier=0.0030, P&L théorique=$-65.72 ⭐

Verdict run 838 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/838/report.json
