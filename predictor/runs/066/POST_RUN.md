**Run 066 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Phoenix on May 26, 2026?
Bin cible : `KXLOWTPHX-26MAY26-B72.5` · Outcome : YES · Low observée (bin gagnant) : 72-73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.152, Brier=0.7187, P&L réel=$-20.55
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$-20.55 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.4692, P&L théorique=$-20.55

Verdict run 066 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/066/report.json
