**Run 870 — résolu NO · Multi-model A/B**

Event : Highest temperature in Seattle on Oct 3, 2026?
Bin cible : `KXHIGHTSEA-26OCT03-B70.5` · Outcome : NO · Low observée (bin gagnant) : 66-67°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.175, Brier=0.0307, P&L réel=$+58.41 ⭐
- `learned_v2` (challenger) — p_yes=0.260, Brier=0.0676, P&L théorique=$+58.41
- `kalshi_mid_baseline` (baseline) — p_yes=0.495, Brier=0.2450, P&L théorique=$+58.41

Verdict run 870 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/870/report.json
