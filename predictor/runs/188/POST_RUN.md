**Run 188 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 9, 2026?
Bin cible : `KXLOWTNYC-26JUN09-B58.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.224, Brier=0.0504, P&L réel=$+14.43
- `learned_v2` (challenger) — p_yes=0.186, Brier=0.0347, P&L théorique=$+14.43 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.370, Brier=0.1369, P&L théorique=$+14.43

Verdict run 188 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/188/report.json
