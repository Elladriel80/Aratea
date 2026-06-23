**Run 299 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jun 22, 2026?
Bin cible : `KXLOWTPHX-26JUN22-B79.5` · Outcome : YES · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.153, Brier=0.7165, P&L réel=$-35.03
- `learned_v2` (challenger) — p_yes=0.159, Brier=0.7077, P&L théorique=$-35.03
- `kalshi_mid_baseline` (baseline) — p_yes=0.285, Brier=0.5112, P&L théorique=$-35.03 ⭐

Verdict run 299 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/299/report.json
