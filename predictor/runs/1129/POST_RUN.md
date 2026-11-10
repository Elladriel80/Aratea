**Run 1129 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 9, 2026?
Bin cible : `KXLOWTSFO-26NOV09-B55.5` · Outcome : NO · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.443, Brier=0.1962, P&L réel=$+127.98 ⭐
- `learned_v2` (challenger) — p_yes=0.739, Brier=0.5463, P&L théorique=$+127.98
- `kalshi_mid_baseline` (baseline) — p_yes=0.540, Brier=0.2916, P&L théorique=$+127.98

Verdict run 1129 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1129/report.json
