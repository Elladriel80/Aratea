**Run 951 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Oct 16, 2026?
Bin cible : `KXLOWTCHI-26OCT16-B42.5` · Outcome : NO · Low observée (bin gagnant) : 44-45°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.101, Brier=0.0102, P&L réel=$+14.06 ⭐
- `learned_v2` (challenger) — p_yes=0.102, Brier=0.0104, P&L théorique=$+14.06
- `kalshi_mid_baseline` (baseline) — p_yes=0.185, Brier=0.0342, P&L théorique=$+14.06

Verdict run 951 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/951/report.json
