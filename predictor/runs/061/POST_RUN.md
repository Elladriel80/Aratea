**Run 061 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on May 26, 2026?
Bin cible : `KXLOWTDC-26MAY26-B63.5` · Outcome : YES · Low observée (bin gagnant) : 63-64°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.124, Brier=0.7669, P&L réel=$+18.20 ⭐
- `learned_v2` (challenger) — p_yes=0.092, Brier=0.8237, P&L théorique=$+18.20
- `kalshi_mid_baseline` (baseline) — p_yes=0.090, Brier=0.8281, P&L théorique=$+18.20

Verdict run 061 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/061/report.json
