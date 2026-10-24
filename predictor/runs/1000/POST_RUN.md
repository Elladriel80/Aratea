**Run 1000 — résolu YES · Multi-model A/B**

Event : Lowest temperature in New York City on Oct 22, 2026?
Bin cible : `KXLOWTNYC-26OCT22-B49.5` · Outcome : YES · Low observée (bin gagnant) : 49-50°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.129, Brier=0.7591, P&L réel=$-95.58
- `learned_v2` (challenger) — p_yes=0.032, Brier=0.9373, P&L théorique=$-95.58
- `kalshi_mid_baseline` (baseline) — p_yes=0.410, Brier=0.3481, P&L théorique=$-95.58 ⭐

Verdict run 1000 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1000/report.json
