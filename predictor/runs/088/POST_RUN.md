**Run 088 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Miami on May 28, 2026?
Bin cible : `KXLOWTMIA-26MAY28-B75.5` · Outcome : YES · Low observée (bin gagnant) : 75-76°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.154, Brier=0.7155, P&L réel=$-21.61
- `learned_v2` (challenger) — p_yes=0.047, Brier=0.9080, P&L théorique=$-21.61
- `kalshi_mid_baseline` (baseline) — p_yes=0.255, Brier=0.5550, P&L théorique=$-21.61 ⭐

Verdict run 088 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/088/report.json
