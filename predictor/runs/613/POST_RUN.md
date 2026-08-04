**Run 613 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Aug 3, 2026?
Bin cible : `KXLOWTDC-26AUG03-B74.5` · Outcome : YES · Low observée (bin gagnant) : 74-75°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.661, Brier=0.1149, P&L réel=$+99.19
- `learned_v2` (challenger) — p_yes=0.739, Brier=0.0680, P&L théorique=$+99.19 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.455, Brier=0.2970, P&L théorique=$+99.19

Verdict run 613 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/613/report.json
