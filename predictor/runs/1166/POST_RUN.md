**Run 1166 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 13, 2026?
Bin cible : `KXHIGHTSFO-26NOV13-B59.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.130, Brier=0.0168, P&L réel=$-96.65
- `learned_v2` (challenger) — p_yes=0.197, Brier=0.0387, P&L théorique=$-96.65
- `kalshi_mid_baseline` (baseline) — p_yes=0.025, Brier=0.0006, P&L théorique=$-96.65 ⭐

Verdict run 1166 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1166/report.json
