**Run 953 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Oct 16, 2026?
Bin cible : `KXLOWTDC-26OCT16-B61.5` · Outcome : YES · Low observée (bin gagnant) : 61-62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.437, Brier=0.3166, P&L réel=$-61.88
- `learned_v2` (challenger) — p_yes=0.285, Brier=0.5118, P&L théorique=$-61.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.545, Brier=0.2070, P&L théorique=$-61.88 ⭐

Verdict run 953 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/953/report.json
