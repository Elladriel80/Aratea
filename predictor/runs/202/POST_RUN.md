**Run 202 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 9, 2026?
Bin cible : `KXLOWTSEA-26JUN09-B51.5` · Outcome : YES · Low observée (bin gagnant) : 51-52°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.320, Brier=0.4630, P&L réel=$-24.29
- `learned_v2` (challenger) — p_yes=0.169, Brier=0.6907, P&L théorique=$-24.29
- `kalshi_mid_baseline` (baseline) — p_yes=0.435, Brier=0.3192, P&L théorique=$-24.29 ⭐

Verdict run 202 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/202/report.json
