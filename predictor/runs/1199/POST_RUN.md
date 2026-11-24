**Run 1199 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Nov 22, 2026?
Bin cible : `KXLOWTCHI-26NOV22-B36.5` · Outcome : NO · Low observée (bin gagnant) : 38-39°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.076, Brier=0.0057, P&L réel=$+32.96 ⭐
- `learned_v2` (challenger) — p_yes=0.152, Brier=0.0230, P&L théorique=$+32.96
- `kalshi_mid_baseline` (baseline) — p_yes=0.195, Brier=0.0380, P&L théorique=$+32.96

Verdict run 1199 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1199/report.json
