**Run 1125 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 7, 2026?
Bin cible : `KXHIGHTSFO-26NOV07-B69.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.224, Brier=0.0503, P&L réel=$+6.32 ⭐
- `learned_v2` (challenger) — p_yes=0.354, Brier=0.1253, P&L théorique=$+6.32
- `kalshi_mid_baseline` (baseline) — p_yes=0.395, Brier=0.1560, P&L théorique=$+6.32

Verdict run 1125 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1125/report.json
