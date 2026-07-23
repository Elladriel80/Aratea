**Run 523 — résolu NO · Multi-model A/B**

Event : Lowest temperature in San Francisco on Jul 22, 2026?
Bin cible : `KXLOWTSFO-26JUL22-B63.5` · Outcome : NO · Low observée (bin gagnant) : 61-62°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.219, Brier=0.0479, P&L réel=$+24.09
- `learned_v2` (challenger) — p_yes=0.049, Brier=0.0024, P&L théorique=$+24.09 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.395, Brier=0.1560, P&L théorique=$+24.09

Verdict run 523 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/523/report.json
