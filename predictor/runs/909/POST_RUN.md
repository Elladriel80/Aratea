**Run 909 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on Oct 9, 2026?
Bin cible : `KXLOWTCHI-26OCT09-B52.5` · Outcome : NO · Low observée (bin gagnant) : ≥53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.337, Brier=0.1132, P&L réel=$+29.60 ⭐
- `learned_v2` (challenger) — p_yes=0.445, Brier=0.1976, P&L théorique=$+29.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.400, Brier=0.1600, P&L théorique=$+29.60

Verdict run 909 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/909/report.json
