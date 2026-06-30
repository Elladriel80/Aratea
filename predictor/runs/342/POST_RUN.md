**Run 342 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jun 29, 2026?
Bin cible : `KXLOWTPHX-26JUN29-B78.5` · Outcome : YES · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.234, Brier=0.5874, P&L réel=$+403.95
- `learned_v2` (challenger) — p_yes=0.303, Brier=0.4863, P&L théorique=$+403.95 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.135, Brier=0.7482, P&L théorique=$+403.95

Verdict run 342 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/342/report.json
