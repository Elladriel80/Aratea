**Run 1003 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Oct 22, 2026?
Bin cible : `KXLOWTBOS-26OCT22-B45.5` · Outcome : NO · Low observée (bin gagnant) : 47-48°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.098, Brier=0.0096, P&L réel=$+34.45 ⭐
- `learned_v2` (challenger) — p_yes=0.118, Brier=0.0140, P&L théorique=$+34.45
- `kalshi_mid_baseline` (baseline) — p_yes=0.265, Brier=0.0702, P&L théorique=$+34.45

Verdict run 1003 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1003/report.json
