**Run 1007 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Oct 22, 2026?
Bin cible : `KXLOWTPHX-26OCT22-B66.5` · Outcome : NO · Low observée (bin gagnant) : ≥71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.142, Brier=0.0202, P&L réel=$+23.80 ⭐
- `learned_v2` (challenger) — p_yes=0.207, Brier=0.0429, P&L théorique=$+23.80
- `kalshi_mid_baseline` (baseline) — p_yes=0.200, Brier=0.0400, P&L théorique=$+23.80

Verdict run 1007 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1007/report.json
