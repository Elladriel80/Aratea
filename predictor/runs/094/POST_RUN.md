**Run 094 — résolu NO · Multi-model A/B**

Event : Lowest temperature in Seattle on May 28, 2026?
Bin cible : `KXLOWTSEA-26MAY28-B54.5` · Outcome : NO · Low observée (bin gagnant) : ≥55°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.273, Brier=0.0746, P&L réel=$+20.58 ⭐
- `learned_v2` (challenger) — p_yes=0.500, Brier=0.2500, P&L théorique=$+20.58
- `kalshi_mid_baseline` (baseline) — p_yes=0.490, Brier=0.2401, P&L théorique=$+20.58

Verdict run 094 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/094/report.json
