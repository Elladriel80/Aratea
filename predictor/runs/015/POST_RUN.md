**Run 015 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on May 22, 2026?
Bin cible : `KXLOWTLAX-26MAY22-B59.5` · Outcome : YES · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.387, Brier=0.3764, P&L réel=$-17.36
- `learned_v2` (challenger) — p_yes=0.285, Brier=0.5114, P&L théorique=$-17.36
- `kalshi_mid_baseline` (baseline) — p_yes=0.440, Brier=0.3136, P&L théorique=$-17.36 ⭐

Verdict run 015 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/015/report.json
