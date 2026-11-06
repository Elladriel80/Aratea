**Run 1097 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 5, 2026?
Bin cible : `KXLOWTSFO-26NOV05-B53.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.172, Brier=0.0295, P&L réel=$+167.24 ⭐
- `learned_v2` (challenger) — p_yes=0.187, Brier=0.0350, P&L théorique=$+167.24
- `kalshi_mid_baseline` (baseline) — p_yes=0.565, Brier=0.3192, P&L théorique=$+167.24

Verdict run 1097 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1097/report.json
