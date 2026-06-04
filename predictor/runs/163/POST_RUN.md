**Run 163 — résolu NO · Multi-model A/B**

Event : Highest temperature in Seattle on Jun 3, 2026?
Bin cible : `KXHIGHTSEA-26JUN03-B71.5` · Outcome : NO · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.096, Brier=0.0091, P&L réel=$+7.47
- `learned_v2` (challenger) — p_yes=0.069, Brier=0.0047, P&L théorique=$+7.47 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.325, Brier=0.1056, P&L théorique=$+7.47

Verdict run 163 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/163/report.json
