**Run 036 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on May 24, 2026?
Bin cible : `KXLOWTCHI-26MAY24-B56.5` · Outcome : NO · Low observée (bin gagnant) : ≥57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.125, Brier=0.0157, P&L réel=$+7.70 ⭐
- `learned_v2` (challenger) — p_yes=0.202, Brier=0.0407, P&L théorique=$+7.70
- `kalshi_mid_baseline` (baseline) — p_yes=0.275, Brier=0.0756, P&L théorique=$+7.70

Verdict run 036 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/036/report.json
