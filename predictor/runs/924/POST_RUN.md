**Run 924 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Oct 11, 2026?
Bin cible : `KXLOWTBOS-26OCT11-B45.5` · Outcome : NO · Low observée (bin gagnant) : 47-48°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.060, Brier=0.0036, P&L réel=$+7.28 ⭐
- `learned_v2` (challenger) — p_yes=0.105, Brier=0.0110, P&L théorique=$+7.28
- `kalshi_mid_baseline` (baseline) — p_yes=0.140, Brier=0.0196, P&L théorique=$+7.28

Verdict run 924 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/924/report.json
