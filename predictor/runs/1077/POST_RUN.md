**Run 1077 — résolu YES · Multi-model A/B**

Event : Highest temperature in Phoenix on Oct 31, 2026?
Bin cible : `KXHIGHTPHX-26OCT31-B78.5` · Outcome : YES · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.311, Brier=0.4746, P&L réel=$-133.12
- `learned_v2` (challenger) — p_yes=0.579, Brier=0.1773, P&L théorique=$-133.12 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.480, Brier=0.2704, P&L théorique=$-133.12

Verdict run 1077 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1077/report.json
