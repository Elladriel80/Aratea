**Run 912 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Oct 9, 2026?
Bin cible : `KXLOWTBOS-26OCT09-B52.5` · Outcome : NO · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.386, Brier=0.1489, P&L réel=$+46.41 ⭐
- `learned_v2` (challenger) — p_yes=0.603, Brier=0.3631, P&L théorique=$+46.41
- `kalshi_mid_baseline` (baseline) — p_yes=0.510, Brier=0.2601, P&L théorique=$+46.41

Verdict run 912 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/912/report.json
