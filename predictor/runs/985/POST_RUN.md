**Run 985 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 20, 2026?
Bin cible : `KXLOWTNYC-26OCT20-B52.5` · Outcome : NO · Low observée (bin gagnant) : 50-51°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.083, Brier=0.0069, P&L réel=$+20.30
- `learned_v2` (challenger) — p_yes=0.023, Brier=0.0005, P&L théorique=$+20.30 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.165, Brier=0.0272, P&L théorique=$+20.30

Verdict run 985 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/985/report.json
