**Run 866 — résolu NO · Multi-model A/B**

Event : Highest temperature in Washington DC on Oct 3, 2026?
Bin cible : `KXHIGHTDC-26OCT03-B71.5` · Outcome : NO · Low observée (bin gagnant) : ≤69°F

Modèles en course (⭐ = best Brier sur ce run) :
- `vendor_ensemble` (champion) — p_yes=0.249, Brier=0.0619, P&L réel=$+39.60 ⭐
- `learned_v2` (challenger) — p_yes=0.428, Brier=0.1836, P&L théorique=$+39.60
- `kalshi_mid_baseline` (baseline) — p_yes=0.400, Brier=0.1600, P&L théorique=$+39.60

Verdict run 866 : Champion best ✓.

Champion actuel : `vendor_ensemble` (la ligne réelle du ledger paper_bets.csv = celle de ce modèle).
Challengers et baselines : positions shadow, P&L théorique, pas d'exposition réelle.

Compteur Phase 1 : voir `dashboard/public/predictor_manifest.json` après rebuild.

Règle de promotion : un challenger n'est pas promoté sur un seul win. Il faut N>=10 résolus avec rolling-mean Brier strictement inférieur ET sign test 1-sided p<0.10. Cf. `predictor/runs_learning/CHAMPION.json`.

Log complet : https://github.com/Elladriel80/aratea/blob/main/predictor/runs/866/report.json
