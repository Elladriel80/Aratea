**Run 519 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 22, 2026?
Bin cible : `KXLOWTNYC-26JUL22-B70.5` · Outcome : YES · Low observée (bin gagnant) : 70-71°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.450, Brier=0.3023, P&L réel=$+143.56 ⭐
- `learned_v2` (challenger) — p_yes=0.293, Brier=0.5002, P&L théorique=$+143.56
- `kalshi_mid_baseline` (baseline) — p_yes=0.260, Brier=0.5476, P&L théorique=$+143.56

Verdict run 519 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/519/report.json
