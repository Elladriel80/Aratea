**Run 511 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 21, 2026?
Bin cible : `KXLOWTNYC-26JUL21-B66.5` · Outcome : NO · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.009, Brier=0.0001, P&L réel=$+8.82 ⭐
- `learned_v2` (challenger) — p_yes=0.055, Brier=0.0030, P&L théorique=$+8.82
- `kalshi_mid_baseline` (baseline) — p_yes=0.140, Brier=0.0196, P&L théorique=$+8.82

Verdict run 511 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/511/report.json
