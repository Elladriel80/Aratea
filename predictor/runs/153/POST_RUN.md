**Run 153 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on Jun 3, 2026?
Bin cible : `KXLOWTSEA-26JUN03-B52.5` · Outcome : NO · Low observée (bin gagnant) : 56-57°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.165, Brier=0.0270, P&L réel=$-2.81
- `learned_v2` (challenger) — p_yes=0.159, Brier=0.0252, P&L théorique=$-2.81
- `kalshi_mid_baseline` (baseline) — p_yes=0.085, Brier=0.0072, P&L théorique=$-2.81 ⭐

Verdict run 153 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/153/report.json
