**Run 574 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jul 30, 2026?
Bin cible : `KXLOWTNYC-26JUL30-B64.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.131, Brier=0.0171, P&L réel=$+26.46
- `learned_v2` (challenger) — p_yes=0.024, Brier=0.0006, P&L théorique=$+26.46 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.245, Brier=0.0600, P&L théorique=$+26.46

Verdict run 574 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/574/report.json
