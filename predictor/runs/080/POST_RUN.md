**Run 080 — résolu YES · Multi-model A/B**

Event : Lowest temperature in San Francisco on May 28, 2026?
Bin cible : `KXLOWTSFO-26MAY28-B54.5` · Outcome : YES · Low observée (bin gagnant) : 54-55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.489, Brier=0.2613, P&L réel=$-21.36
- `learned_v2` (challenger) — p_yes=0.591, Brier=0.1677, P&L théorique=$-21.36 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.555, Brier=0.1980, P&L théorique=$-21.36

Verdict run 080 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/080/report.json
