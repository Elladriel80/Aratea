**Run 552 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 25, 2026?
Bin cible : `KXLOWTDC-26JUL25-B66.5` · Outcome : YES · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.105, Brier=0.8008, P&L réel=$-77.66
- `learned_v2` (challenger) — p_yes=0.028, Brier=0.9456, P&L théorique=$-77.66
- `kalshi_mid_baseline` (baseline) — p_yes=0.165, Brier=0.6972, P&L théorique=$-77.66 ⭐

Verdict run 552 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/552/report.json
