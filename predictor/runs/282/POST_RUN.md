**Run 282 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Phoenix on Jun 20, 2026?
Bin cible : `KXLOWTPHX-26JUN20-B76.5` · Outcome : NO · Low observée (bin gagnant) : ≥79°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.104, Brier=0.0108, P&L réel=$-34.16
- `learned_v2` (challenger) — p_yes=0.107, Brier=0.0114, P&L théorique=$-34.16
- `kalshi_mid_baseline` (baseline) — p_yes=0.035, Brier=0.0012, P&L théorique=$-34.16 ⭐

Verdict run 282 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/282/report.json
