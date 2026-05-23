**Run 020 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on May 22, 2026?
Bin cible : `KXLOWTMIA-26MAY22-B76.5` · Outcome : NO · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.173, Brier=0.0299, P&L réel=$+13.04
- `learned_v2` (challenger) — p_yes=0.091, Brier=0.0083, P&L théorique=$+13.04 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.395, Brier=0.1560, P&L théorique=$+13.04

Verdict run 020 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/020/report.json
