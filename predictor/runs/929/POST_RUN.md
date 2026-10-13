**Run 929 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on Oct 11, 2026?
Bin cible : `KXLOWTDEN-26OCT11-B56.5` · Outcome : YES · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.229, Brier=0.5944, P&L réel=$-44.88
- `learned_v2` (challenger) — p_yes=0.059, Brier=0.8859, P&L théorique=$-44.88
- `kalshi_mid_baseline` (baseline) — p_yes=0.320, Brier=0.4624, P&L théorique=$-44.88 ⭐

Verdict run 929 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/929/report.json
