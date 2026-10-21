**Run 993 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 20, 2026?
Bin cible : `KXHIGHTSFO-26OCT20-B66.5` · Outcome : NO · Low observée (bin gagnant) : 68-69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.254, Brier=0.0645, P&L réel=$+100.98
- `learned_v2` (challenger) — p_yes=0.064, Brier=0.0041, P&L théorique=$+100.98 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.495, Brier=0.2450, P&L théorique=$+100.98

Verdict run 993 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/993/report.json
