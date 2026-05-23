**Run 028 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on May 22, 2026?
Bin cible : `KXHIGHTSFO-26MAY22-B68.5` · Outcome : YES · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.101, Brier=0.8080, P&L réel=$-20.16
- `learned_v2` (challenger) — p_yes=0.173, Brier=0.6838, P&L théorique=$-20.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.305, Brier=0.4830, P&L théorique=$-20.16 ⭐

Verdict run 028 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/028/report.json
