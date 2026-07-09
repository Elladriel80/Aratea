**Run 406 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 8, 2026?
Bin cible : `KXLOWTNYC-26JUL08-B65.5` · Outcome : NO · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.317, Brier=0.1004, P&L réel=$+33.75 ⭐
- `learned_v2` (challenger) — p_yes=0.539, Brier=0.2909, P&L théorique=$+33.75
- `kalshi_mid_baseline` (baseline) — p_yes=0.375, Brier=0.1406, P&L théorique=$+33.75

Verdict run 406 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/406/report.json
