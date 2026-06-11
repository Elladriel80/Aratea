**Run 187 — résolu NO · Multi-model A/B**

Event : Lowest temperature in New York City on Jun 9, 2026?
Bin cible : `KXLOWTNYC-26JUN09-B56.5` · Outcome : NO · Low observée (bin gagnant) : ≥59°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.157, Brier=0.0245, P&L réel=$+10.68 ⭐
- `learned_v2` (challenger) — p_yes=0.200, Brier=0.0399, P&L théorique=$+10.68
- `kalshi_mid_baseline` (baseline) — p_yes=0.305, Brier=0.0930, P&L théorique=$+10.68

Verdict run 187 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/187/report.json
