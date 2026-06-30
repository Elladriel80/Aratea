**Run 337 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jun 29, 2026?
Bin cible : `KXLOWTSFO-26JUN29-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.392, Brier=0.3693, P&L réel=$-62.80
- `learned_v2` (challenger) — p_yes=0.191, Brier=0.6547, P&L théorique=$-62.80
- `kalshi_mid_baseline` (baseline) — p_yes=0.600, Brier=0.1600, P&L théorique=$-62.80 ⭐

Verdict run 337 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/337/report.json
