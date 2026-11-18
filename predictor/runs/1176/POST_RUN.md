**Run 1176 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Nov 16, 2026?
Bin cible : `KXLOWTSFO-26NOV16-B52.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.425, Brier=0.1811, P&L réel=$+155.69 ⭐
- `learned_v2` (challenger) — p_yes=0.622, Brier=0.3868, P&L théorique=$+155.69
- `kalshi_mid_baseline` (baseline) — p_yes=0.535, Brier=0.2862, P&L théorique=$+155.69

Verdict run 1176 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1176/report.json
