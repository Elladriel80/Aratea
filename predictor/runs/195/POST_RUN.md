**Run 195 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 9, 2026?
Bin cible : `KXLOWTMIA-26JUN09-B77.5` · Outcome : YES · Low observée (bin gagnant) : 77-78°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.211, Brier=0.6230, P&L réel=$-24.50
- `learned_v2` (challenger) — p_yes=0.158, Brier=0.7094, P&L théorique=$-24.50
- `kalshi_mid_baseline` (baseline) — p_yes=0.510, Brier=0.2401, P&L théorique=$-24.50 ⭐

Verdict run 195 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/195/report.json
