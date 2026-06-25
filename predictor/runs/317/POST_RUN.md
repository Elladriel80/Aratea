**Run 317 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 24, 2026?
Bin cible : `KXLOWTSEA-26JUN24-B58.5` · Outcome : YES · Low observée (bin gagnant) : 58-59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.235, Brier=0.5856, P&L réel=$+769.27
- `learned_v2` (challenger) — p_yes=0.320, Brier=0.4619, P&L théorique=$+769.27 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.025, Brier=0.9506, P&L théorique=$+769.27

Verdict run 317 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/317/report.json
