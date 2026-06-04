**Run 162 — résolu NO · Multi-model A/B**

Event : Highest temperature in Seattle on Jun 3, 2026?
Bin cible : `KXHIGHTSEA-26JUN03-B73.5` · Outcome : NO · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.061, Brier=0.0037, P&L réel=$+9.76
- `learned_v2` (challenger) — p_yes=0.054, Brier=0.0030, P&L théorique=$+9.76 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.315, Brier=0.0992, P&L théorique=$+9.76

Verdict run 162 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/162/report.json
