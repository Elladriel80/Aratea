**Run 154 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Jun 3, 2026?
Bin cible : `KXHIGHTSFO-26JUN03-B70.5` · Outcome : YES · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.117, Brier=0.7802, P&L réel=$-21.15
- `learned_v2` (challenger) — p_yes=0.136, Brier=0.7463, P&L théorique=$-21.15
- `kalshi_mid_baseline` (baseline) — p_yes=0.295, Brier=0.4970, P&L théorique=$-21.15 ⭐

Verdict run 154 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/154/report.json
