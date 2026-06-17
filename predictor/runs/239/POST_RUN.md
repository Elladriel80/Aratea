**Run 239 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 16, 2026?
Bin cible : `KXLOWTNYC-26JUN16-B57.5` · Outcome : YES · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.288, Brier=0.5068, P&L réel=$-59.85
- `learned_v2` (challenger) — p_yes=0.334, Brier=0.4440, P&L théorique=$-59.85
- `kalshi_mid_baseline` (baseline) — p_yes=0.370, Brier=0.3969, P&L théorique=$-59.85 ⭐

Verdict run 239 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/239/report.json
