**Run 1068 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 31, 2026?
Bin cible : `KXHIGHTSFO-26OCT31-B64.5` · Outcome : YES · Low observée (bin gagnant) : 64-65°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.200, Brier=0.6397, P&L réel=$-132.94
- `learned_v2` (challenger) — p_yes=0.242, Brier=0.5742, P&L théorique=$-132.94
- `kalshi_mid_baseline` (baseline) — p_yes=0.540, Brier=0.2116, P&L théorique=$-132.94 ⭐

Verdict run 1068 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1068/report.json
