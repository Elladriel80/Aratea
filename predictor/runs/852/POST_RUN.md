**Run 852 — résolu NO · Multi-model A/B**

Event : Highest temperature in Seattle on Oct 1, 2026?
Bin cible : `KXHIGHTSEA-26OCT01-B69.5` · Outcome : NO · Low observée (bin gagnant) : 67-68°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.187, Brier=0.0349, P&L réel=$+23.46 ⭐
- `learned_v2` (challenger) — p_yes=0.272, Brier=0.0740, P&L théorique=$+23.46
- `kalshi_mid_baseline` (baseline) — p_yes=0.255, Brier=0.0650, P&L théorique=$+23.46

Verdict run 852 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/852/report.json
