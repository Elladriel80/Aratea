**Run 037 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Chicago on May 24, 2026?
Bin cible : `KXLOWTCHI-26MAY24-B54.5` · Outcome : NO · Low observée (bin gagnant) : ≥57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.096, Brier=0.0091, P&L réel=$+4.20 ⭐
- `learned_v2` (challenger) — p_yes=0.155, Brier=0.0239, P&L théorique=$+4.20
- `kalshi_mid_baseline` (baseline) — p_yes=0.175, Brier=0.0306, P&L théorique=$+4.20

Verdict run 037 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/037/report.json
