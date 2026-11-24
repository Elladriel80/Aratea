**Run 1193 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Nov 22, 2026?
Bin cible : `KXLOWTLAX-26NOV22-B49.5` · Outcome : NO · Low observée (bin gagnant) : 47-48°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.378, Brier=0.1427, P&L réel=$+106.92 ⭐
- `learned_v2` (challenger) — p_yes=0.598, Brier=0.3581, P&L théorique=$+106.92
- `kalshi_mid_baseline` (baseline) — p_yes=0.440, Brier=0.1936, P&L théorique=$+106.92

Verdict run 1193 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1193/report.json
