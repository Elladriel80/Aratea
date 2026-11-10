**Run 1140 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Nov 9, 2026?
Bin cible : `KXHIGHTSFO-26NOV09-B72.5` · Outcome : YES · Low observée (bin gagnant) : 72-73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.081, Brier=0.8447, P&L réel=$-108.91
- `learned_v2` (challenger) — p_yes=0.158, Brier=0.7082, P&L théorique=$-108.91
- `kalshi_mid_baseline` (baseline) — p_yes=0.205, Brier=0.6320, P&L théorique=$-108.91 ⭐

Verdict run 1140 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1140/report.json
