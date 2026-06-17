**Run 240 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 16, 2026?
Bin cible : `KXLOWTNYC-26JUN16-B59.5` · Outcome : NO · Low observée (bin gagnant) : 57-58°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.305, Brier=0.0932, P&L réel=$-50.49
- `learned_v2` (challenger) — p_yes=0.422, Brier=0.1783, P&L théorique=$-50.49
- `kalshi_mid_baseline` (baseline) — p_yes=0.255, Brier=0.0650, P&L théorique=$-50.49 ⭐

Verdict run 240 : Challenger `kalshi_mid_baseline` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/240/report.json
