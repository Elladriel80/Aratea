**Run 1115 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 7, 2026?
Bin cible : `KXLOWTSFO-26NOV07-B53.5` · Outcome : NO · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.404, Brier=0.1634, P&L réel=$+138.60 ⭐
- `learned_v2` (challenger) — p_yes=0.598, Brier=0.3581, P&L théorique=$+138.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.525, Brier=0.2756, P&L théorique=$+138.60

Verdict run 1115 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1115/report.json
