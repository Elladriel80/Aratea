**Run 972 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Chicago on Oct 18, 2026?
Bin cible : `KXLOWTCHI-26OCT18-B41.5` · Outcome : YES · Low observée (bin gagnant) : 41-42°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.242, Brier=0.5742, P&L réel=$-90.95
- `learned_v2` (challenger) — p_yes=0.064, Brier=0.8759, P&L théorique=$-90.95
- `kalshi_mid_baseline` (baseline) — p_yes=0.465, Brier=0.2862, P&L théorique=$-90.95 ⭐

Verdict run 972 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/972/report.json
