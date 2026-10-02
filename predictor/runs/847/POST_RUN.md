**Run 847 — résolu YES · Multi-model A/B**

Event : Highest temperature in Boston on Oct 1, 2026?
Bin cible : `KXHIGHTBOS-26OCT01-B79.5` · Outcome : YES · Low observée (bin gagnant) : 79-80°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.239, Brier=0.5783, P&L réel=$-68.27
- `learned_v2` (challenger) — p_yes=0.438, Brier=0.3158, P&L théorique=$-68.27 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.385, Brier=0.3782, P&L théorique=$-68.27

Verdict run 847 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/847/report.json
