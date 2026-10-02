**Run 843 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Oct 1, 2026?
Bin cible : `KXLOWTSFO-26OCT01-B55.5` · Outcome : NO · Low observée (bin gagnant) : 53-54°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.311, Brier=0.0970, P&L réel=$+130.34
- `learned_v2` (challenger) — p_yes=0.241, Brier=0.0583, P&L théorique=$+130.34 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.655, Brier=0.4290, P&L théorique=$+130.34

Verdict run 843 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/843/report.json
