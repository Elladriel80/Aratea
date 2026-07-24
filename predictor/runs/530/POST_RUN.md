**Run 530 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 23, 2026?
Bin cible : `KXLOWTDC-26JUL23-B64.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.076, Brier=0.0058, P&L réel=$+14.35
- `learned_v2` (challenger) — p_yes=0.016, Brier=0.0002, P&L théorique=$+14.35 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.205, Brier=0.0420, P&L théorique=$+14.35

Verdict run 530 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/530/report.json
