**Run 1136 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Nov 9, 2026?
Bin cible : `KXLOWTPHX-26NOV09-B60.5` · Outcome : NO · Low observée (bin gagnant) : ≥61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.226, Brier=0.0512, P&L réel=$+96.35 ⭐
- `learned_v2` (challenger) — p_yes=0.408, Brier=0.1666, P&L théorique=$+96.35
- `kalshi_mid_baseline` (baseline) — p_yes=0.470, Brier=0.2209, P&L théorique=$+96.35

Verdict run 1136 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1136/report.json
