**Run 1165 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 13, 2026?
Bin cible : `KXHIGHTSFO-26NOV13-B63.5` · Outcome : YES · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.166, Brier=0.6961, P&L réel=$-96.38
- `learned_v2` (challenger) — p_yes=0.164, Brier=0.6997, P&L théorique=$-96.38
- `kalshi_mid_baseline` (baseline) — p_yes=0.605, Brier=0.1560, P&L théorique=$-96.38 ⭐

Verdict run 1165 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1165/report.json
