**Run 584 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Boston on Jul 30, 2026?
Bin cible : `KXLOWTBOS-26JUL30-B61.5` · Outcome : NO · Low observée (bin gagnant) : ≥62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.051, Brier=0.0026, P&L réel=$+10.12 ⭐
- `learned_v2` (challenger) — p_yes=0.069, Brier=0.0048, P&L théorique=$+10.12
- `kalshi_mid_baseline` (baseline) — p_yes=0.110, Brier=0.0121, P&L théorique=$+10.12

Verdict run 584 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/584/report.json
