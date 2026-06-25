**Run 315 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Jun 24, 2026?
Bin cible : `KXLOWTDEN-26JUN24-B55.5` · Outcome : NO · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.061, Brier=0.0038, P&L réel=$+13.01
- `learned_v2` (challenger) — p_yes=0.016, Brier=0.0003, P&L théorique=$+13.01 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.255, Brier=0.0650, P&L théorique=$+13.01

Verdict run 315 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/315/report.json
