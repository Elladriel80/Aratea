**Run 117 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Seattle on May 30, 2026?
Bin cible : `KXLOWTSEA-26MAY30-B45.5` · Outcome : YES · Low observée (bin gagnant) : 45-46°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.272, Brier=0.5300, P&L réel=$-14.88
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$-14.88 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.380, Brier=0.3844, P&L théorique=$-14.88

Verdict run 117 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/117/report.json
