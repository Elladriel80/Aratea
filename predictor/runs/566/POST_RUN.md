**Run 566 — résolu YES · Multi-model A/B**

Event : Lowest temperature in Washington DC on Jul 28, 2026?
Bin cible : `KXLOWTDC-26JUL28-B69.5` · Outcome : YES · Low observée (bin gagnant) : 69-70°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.218, Brier=0.6121, P&L réel=$+1055.55
- `learned_v2` (challenger) — p_yes=0.284, Brier=0.5127, P&L théorique=$+1055.55 ⭐
- `kalshi_mid_baseline` (baseline) — p_yes=0.070, Brier=0.8649, P&L théorique=$+1055.55

Verdict run 566 : Challenger `learned_v2` ahead this run.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/566/report.json
