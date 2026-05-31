**Run 098 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on May 30, 2026?
Bin cible : `KXLOWTNYC-26MAY30-B52.5` · Outcome : NO · Low observée (bin gagnant) : ≤52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.172, Brier=0.0295, P&L réel=$+9.13 ⭐
- `learned_v2` (challenger) — p_yes=0.213, Brier=0.0455, P&L théorique=$+9.13
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.0992, P&L théorique=$+9.13

Verdict run 098 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/098/report.json
