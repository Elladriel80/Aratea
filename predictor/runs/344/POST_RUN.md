**Run 344 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 29, 2026?
Bin cible : `KXLOWTSEA-26JUN29-B50.5` · Outcome : NO · Low observée (bin gagnant) : 52-53°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.199, Brier=0.0398, P&L réel=$-63.06
- `learned_v2` (challenger) — p_yes=0.178, Brier=0.0317, P&L théorique=$-63.06
- `kalshi_mid_baseline` (baseline) — p_yes=0.060, Brier=0.0036, P&L théorique=$-63.06 ⭐

Verdict run 344 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/344/report.json
