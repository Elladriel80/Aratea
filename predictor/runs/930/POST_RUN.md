**Run 930 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 11, 2026?
Bin cible : `KXHIGHTSFO-26OCT11-B67.5` · Outcome : NO · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.193, Brier=0.0371, P&L réel=$+47.90 ⭐
- `learned_v2` (challenger) — p_yes=0.223, Brier=0.0499, P&L théorique=$+47.90
- `kalshi_mid_baseline` (baseline) — p_yes=0.515, Brier=0.2652, P&L théorique=$+47.90

Verdict run 930 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/930/report.json
