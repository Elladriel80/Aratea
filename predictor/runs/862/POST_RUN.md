**Run 862 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 3, 2026?
Bin cible : `KXHIGHTSFO-26OCT03-B89.5` · Outcome : YES · Low observée (bin gagnant) : 89-90°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.091, Brier=0.8257, P&L réel=$-59.28
- `learned_v2` (challenger) — p_yes=0.192, Brier=0.6527, P&L théorique=$-59.28 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.165, Brier=0.6972, P&L théorique=$-59.28

Verdict run 862 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/862/report.json
