**Run 1046 — résolu YES · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 27, 2026?
Bin cible : `KXHIGHTDC-26OCT27-B72.5` · Outcome : YES · Low observée (bin gagnant) : 72-73°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.129, Brier=0.7587, P&L réel=$+0.00
- `learned_v2` (challenger) — p_yes=0.258, Brier=0.5500, P&L théorique=$+0.00 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.240, Brier=0.5776, P&L théorique=$+0.00

Verdict run 1046 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1046/report.json
