**Run 1032 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Los Angeles on Oct 27, 2026?
Bin cible : `KXLOWTLAX-26OCT27-B59.5` · Outcome : YES · Low observée (bin gagnant) : 59-60°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.602, Brier=0.1587, P&L réel=$+131.60
- `learned_v2` (challenger) — p_yes=0.665, Brier=0.1125, P&L théorique=$+131.60 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.440, Brier=0.3136, P&L théorique=$+131.60

Verdict run 1032 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1032/report.json
