**Run 242 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jun 16, 2026?
Bin cible : `KXLOWTSFO-26JUN16-B55.5` · Outcome : NO · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.191, Brier=0.0364, P&L réel=$+46.11
- `learned_v2` (challenger) — p_yes=0.119, Brier=0.0141, P&L théorique=$+46.11 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.435, Brier=0.1892, P&L théorique=$+46.11

Verdict run 242 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/242/report.json
