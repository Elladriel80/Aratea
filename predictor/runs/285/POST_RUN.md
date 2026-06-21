**Run 285 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 20, 2026?
Bin cible : `KXLOWTSEA-26JUN20-B53.5` · Outcome : YES · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.266, Brier=0.5385, P&L réel=$-16.00
- `learned_v2` (challenger) — p_yes=0.192, Brier=0.6530, P&L théorique=$-16.00
- `kalshi_mid_baseline` (baseline) — p_yes=0.500, Brier=0.2500, P&L théorique=$-16.00 ⭐

Verdict run 285 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/285/report.json
