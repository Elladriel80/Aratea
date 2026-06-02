**Run 140 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Jun 1, 2026?
Bin cible : `KXHIGHTSFO-26JUN01-B73.5` · Outcome : NO · Low observée (bin gagnant) : 71-72°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.078, Brier=0.0061, P&L réel=$+14.53 ⭐
- `learned_v2` (challenger) — p_yes=0.136, Brier=0.0184, P&L théorique=$+14.53
- `kalshi_mid_baseline` (baseline) — p_yes=0.415, Brier=0.1722, P&L théorique=$+14.53

Verdict run 140 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/140/report.json
