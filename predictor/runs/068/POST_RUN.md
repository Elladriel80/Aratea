**Run 068 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Denver on May 26, 2026?
Bin cible : `KXLOWTDEN-26MAY26-B53.5` · Outcome : YES · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.101, Brier=0.8080, P&L réel=$-20.41
- `learned_v2` (challenger) — p_yes=0.172, Brier=0.6848, P&L théorique=$-20.41
- `kalshi_mid_baseline` (baseline) — p_yes=0.215, Brier=0.6162, P&L théorique=$-20.41 ⭐

Verdict run 068 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/068/report.json
