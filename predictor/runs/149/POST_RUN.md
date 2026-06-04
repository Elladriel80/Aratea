**Run 149 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 3, 2026?
Bin cible : `KXLOWTMIA-26JUN03-B77.5` · Outcome : NO · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.271, Brier=0.0732, P&L réel=$-5.58
- `learned_v2` (challenger) — p_yes=0.363, Brier=0.1317, P&L théorique=$-5.58
- `kalshi_mid_baseline` (baseline) — p_yes=0.155, Brier=0.0240, P&L théorique=$-5.58 ⭐

Verdict run 149 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/149/report.json
