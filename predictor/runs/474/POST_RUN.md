**Run 474 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Jul 16, 2026?
Bin cible : `KXLOWTLAX-26JUL16-B68.5` · Outcome : YES · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.221, Brier=0.6076, P&L réel=$-69.68
- `learned_v2` (challenger) — p_yes=0.059, Brier=0.8849, P&L théorique=$-69.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.665, Brier=0.1122, P&L théorique=$-69.68 ⭐

Verdict run 474 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/474/report.json
