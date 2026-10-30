**Run 1060 — résolu NO · Multi-model A/B**

Event : Highest temperature in San Francisco on Oct 29, 2026?
Bin cible : `KXHIGHTSFO-26OCT29-B69.5` · Outcome : NO · Low observée (bin gagnant) : 65-66°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.124, Brier=0.0155, P&L réel=$+42.06 ⭐
- `learned_v2` (challenger) — p_yes=0.180, Brier=0.0324, P&L théorique=$+42.06
- `kalshi_mid_baseline` (baseline) — p_yes=0.235, Brier=0.0552, P&L théorique=$+42.06

Verdict run 1060 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/1060/report.json
