**Run 868 — résolu NO · Multi-model A/B**

Event : Highest temperature in Boston on Oct 3, 2026?
Bin cible : `KXHIGHTBOS-26OCT03-B71.5` · Outcome : NO · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.151, Brier=0.0227, P&L réel=$-59.94
- `learned_v2` (challenger) — p_yes=0.235, Brier=0.0550, P&L théorique=$-59.94
- `kalshi_mid_baseline` (baseline) — p_yes=0.045, Brier=0.0020, P&L théorique=$-59.94 ⭐

Verdict run 868 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/868/report.json
