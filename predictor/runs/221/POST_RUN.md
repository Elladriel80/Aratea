**Run 221 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 12, 2026?
Bin cible : `KXLOWTMIA-26JUN12-B78.5` · Outcome : YES · Low observée (bin gagnant) : 78-79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.275, Brier=0.5258, P&L réel=$-16.60
- `learned_v2` (challenger) — p_yes=0.087, Brier=0.8336, P&L théorique=$-16.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.585, Brier=0.1722, P&L théorique=$-16.60 ⭐

Verdict run 221 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/221/report.json
