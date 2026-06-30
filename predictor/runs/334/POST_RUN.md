**Run 334 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 29, 2026?
Bin cible : `KXLOWTNYC-26JUN29-B68.5` · Outcome : YES · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.576, Brier=0.1799, P&L réel=$+61.38
- `learned_v2` (challenger) — p_yes=0.587, Brier=0.1703, P&L théorique=$+61.38 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.505, Brier=0.2450, P&L théorique=$+61.38

Verdict run 334 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/334/report.json
