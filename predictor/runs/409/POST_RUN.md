**Run 409 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Jul 8, 2026?
Bin cible : `KXLOWTCHI-26JUL08-B63.5` · Outcome : NO · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.014, Brier=0.0002, P&L réel=$+4.57 ⭐
- `learned_v2` (challenger) — p_yes=0.076, Brier=0.0058, P&L théorique=$+4.57
- `kalshi_mid_baseline` (baseline) — p_yes=0.075, Brier=0.0056, P&L théorique=$+4.57

Verdict run 409 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/409/report.json
