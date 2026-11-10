**Run 1126 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Nov 9, 2026?
Bin cible : `KXLOWTNYC-26NOV09-B48.5` · Outcome : NO · Low observée (bin gagnant) : ≥49°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.124, Brier=0.0155, P&L réel=$+133.10 ⭐
- `learned_v2` (challenger) — p_yes=0.232, Brier=0.0536, P&L théorique=$+133.10
- `kalshi_mid_baseline` (baseline) — p_yes=0.550, Brier=0.3025, P&L théorique=$+133.10

Verdict run 1126 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1126/report.json
