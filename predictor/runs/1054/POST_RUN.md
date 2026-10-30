**Run 1054 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Oct 29, 2026?
Bin cible : `KXLOWTMIA-26OCT29-B76.5` · Outcome : YES · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.223, Brier=0.6033, P&L réel=$-136.77
- `learned_v2` (challenger) — p_yes=0.051, Brier=0.8997, P&L théorique=$-136.77
- `kalshi_mid_baseline` (baseline) — p_yes=0.515, Brier=0.2352, P&L théorique=$-136.77 ⭐

Verdict run 1054 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1054/report.json
