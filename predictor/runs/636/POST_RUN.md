**Run 636 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Denver on Aug 5, 2026?
Bin cible : `KXLOWTDEN-26AUG05-B53.5` · Outcome : NO · Low observée (bin gagnant) : ≤53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.135, Brier=0.0183, P&L réel=$+0.00 ⭐
- `learned_v2` (challenger) — p_yes=0.186, Brier=0.0347, P&L théorique=$+0.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.295, Brier=0.0870, P&L théorique=$+0.00

Verdict run 636 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/636/report.json
