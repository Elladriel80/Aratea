**Run 675 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Boston on Sep 9, 2026?
Bin cible : `KXLOWTBOS-26SEP09-B60.5` · Outcome : YES · Low observée (bin gagnant) : 60-61°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.172, Brier=0.6860, P&L réel=$+764.02
- `learned_v2` (challenger) — p_yes=0.176, Brier=0.6783, P&L théorique=$+764.02 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.085, Brier=0.8372, P&L théorique=$+764.02

Verdict run 675 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/675/report.json
