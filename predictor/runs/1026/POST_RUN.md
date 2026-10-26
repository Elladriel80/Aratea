**Run 1026 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 25, 2026?
Bin cible : `KXHIGHTDC-26OCT25-B70.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.075, Brier=0.0056, P&L réel=$-97.03
- `learned_v2` (challenger) — p_yes=0.161, Brier=0.0260, P&L théorique=$-97.03
- `kalshi_mid_baseline` (baseline) — p_yes=0.025, Brier=0.0006, P&L théorique=$-97.03 ⭐

Verdict run 1026 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1026/report.json
