**Run 423 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 10, 2026?
Bin cible : `KXLOWTNYC-26JUL10-B73.5` · Outcome : YES · Low observée (bin gagnant) : 73-74°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.509, Brier=0.2414, P&L réel=$+200.10
- `learned_v2` (challenger) — p_yes=0.818, Brier=0.0331, P&L théorique=$+200.10 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.310, Brier=0.4761, P&L théorique=$+200.10

Verdict run 423 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/423/report.json
