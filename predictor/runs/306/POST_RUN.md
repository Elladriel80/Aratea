**Run 306 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jun 24, 2026?
Bin cible : `KXLOWTSFO-26JUN24-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.605, Brier=0.1560, P&L réel=$+31.05
- `learned_v2` (challenger) — p_yes=0.606, Brier=0.1553, P&L théorique=$+31.05 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.550, Brier=0.2025, P&L théorique=$+31.05

Verdict run 306 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/306/report.json
