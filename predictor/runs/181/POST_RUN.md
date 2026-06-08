**Run 181 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Miami on Jun 5, 2026?
Bin cible : `KXLOWTMIA-26JUN05-B72.5` · Outcome : NO · Low observée (bin gagnant) : 76-77°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.035, Brier=0.0012, P&L réel=$+4.42
- `learned_v2` (challenger) — p_yes=0.011, Brier=0.0001, P&L théorique=$+4.42 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.170, Brier=0.0289, P&L théorique=$+4.42

Verdict run 181 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/181/report.json
