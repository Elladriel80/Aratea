**Run 625 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Aug 5, 2026?
Bin cible : `KXLOWTCHI-26AUG05-B69.5` · Outcome : YES · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.305, Brier=0.4833, P&L réel=$-71.82
- `learned_v2` (challenger) — p_yes=0.143, Brier=0.7352, P&L théorique=$-71.82
- `kalshi_mid_baseline` (baseline) — p_yes=0.430, Brier=0.3249, P&L théorique=$-71.82 ⭐

Verdict run 625 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/625/report.json
