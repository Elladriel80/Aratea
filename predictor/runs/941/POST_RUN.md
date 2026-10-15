**Run 941 — résolu YES · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 14, 2026?
Bin cible : `KXHIGHTSFO-26OCT14-B75.5` · Outcome : YES · Low observée (bin gagnant) : 75-76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.207, Brier=0.6290, P&L réel=$-77.14
- `learned_v2` (challenger) — p_yes=0.043, Brier=0.9157, P&L théorique=$-77.14
- `kalshi_mid_baseline` (baseline) — p_yes=0.335, Brier=0.4422, P&L théorique=$-77.14 ⭐

Verdict run 941 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/941/report.json
