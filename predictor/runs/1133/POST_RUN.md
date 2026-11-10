**Run 1133 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Nov 9, 2026?
Bin cible : `KXLOWTMIA-26NOV09-B73.5` · Outcome : NO · Low observée (bin gagnant) : ≥74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.300, Brier=0.0898, P&L réel=$+122.96 ⭐
- `learned_v2` (challenger) — p_yes=0.370, Brier=0.1370, P&L théorique=$+122.96
- `kalshi_mid_baseline` (baseline) — p_yes=0.530, Brier=0.2809, P&L théorique=$+122.96

Verdict run 1133 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1133/report.json
