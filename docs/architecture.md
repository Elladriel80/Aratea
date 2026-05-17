# Aratea — architecture overview

*Date : 2026-05-08 — version 0.1*

## Vision

Aratea est un protocole décentralisé de **mutuelle paramétrique météo**, alimenté par un moteur prédictif communautaire. Trois piliers :

1. **Moteur prédictif** : méta-ensemble de modèles météo IA + données crowdsourcées. Open-source, contributif, mesuré sur Kalshi en phase POC.
2. **DAO mutualiste** : pool de mutualisation tokenisé façon Nexus Mutual. Membres apportent du collatéral, payouts paramétriques déclenchés par oracles météo.
3. **DePIN data layer** : stations physiques rémunérées en token. Améliore la résolution locale et réduit la dépendance aux feeds gouvernementaux.

> **Précision juridique** — Aratea n'est pas un assureur réglementé. Le terme "mutuelle" recouvre ici une **mutuelle discrétionnaire décentralisée** : les membres mutualisent un pool, l'exécution des indemnisations est paramétrique-automatique (oracle on-chain), aucun engagement contractuel d'assureur. Cf. white paper section 4.

Les trois piliers se renforcent : meilleure prédiction → meilleur pricing → plus de contrats vendus → plus de stakers attirés → financement de plus de capteurs DePIN → meilleure prédiction.

## Phases

### Phase 1 — POC Kalshi *(en cours)*

Objectif : démontrer que le moteur prédictif a un edge mesurable. Pas de produit final, pas de smart contract, pas de risk pool. Le critère go/no-go est strictement quantitatif : ensemble IA bat best single model et bat climatologie sur N>50 events forward-testés (sans data leakage).

Code : `predictor/`. Off-chain entièrement. Bankroll de trading sur Kalshi finance la suite.

### Phase 2 — DAO Aratea (token + gouvernance)

Démarre une fois la Phase 1 validée. Objectifs :
- Déployer l'ERC-20 AUG-POC sur Base/Arbitrum/Optimism (chain à trancher).
- Activer le module mint via les rounds mensuels existants (déjà testés en off-chain).
- Mettre en place la gouvernance par panel Top-X holders.
- Convertir AUG-POC vers ARA (token DAO final) par vote ≥ 67 %.

Code : `contracts/token/`, `contracts/rounds/`, `contracts/governance/`.

### Phase 3 — Mutuelle paramétrique

Démarre une fois la DAO opérationnelle et le predictor démontré en live. Objectifs :
- Pool de mutualisation : les membres déposent USDC/BTC, perçoivent les primes des contrats vendus via appréciation de la NAV.
- Pricing : moteur prédictif (off-chain) émet des prix de contrat, signés et postés on-chain.
- Résolution : Chainlink Custom au-dessus des feeds NOAA/NWS (et DePIN propre quand disponible).
- Catégories initiales : température extrême, précipitations cumulées, événements vent.

**Promesse de couverture bornée et transparence radicale.** La mutuelle s'engage à indemniser chaque sinistre paramétrique éligible *dans la limite des capitaux disponibles* du pool, tels qu'établis on-chain à la liquidation. Si plusieurs engagements actifs se déclenchent simultanément au-delà du *Free Capital* disponible, l'indemnisation est exécutée au prorata. Le ratio engagements actifs / capital total mobilisable est lisible on-chain en continu, et opposable au souscripteur de plein droit (cf. article 4 bis des statuts).

Cette mécanique est l'inverse exact du modèle classique d'assurance, dont l'opacité a été identifiée comme un facteur central de l'effondrement d'AIG en 2008 (≈ 440 milliards USD de CDS notionnels souscrits via AIG Financial Products sans capitalisation correspondante, sauvetage fédéral américain ≈ 182 milliards USD). En rendant le ratio engagements/capital visible en temps réel, l'architecture rend toute opacité de cette nature structurellement impossible.

Code : `contracts/mutual/`, `predictor/oracle/` (signature des prix), pipeline de résolution dans `predictor/scripts/`.

### Phase 4 — DePIN data layer

Stations physiques (partenariat WeatherXM ou réseau propre, à arbitrer). Récompense en token ARA basée sur :
- Disponibilité de la station (uptime).
- Qualité des données (cohérence avec voisins, validation par modèles, pas d'outliers manuels).
- Densité géographique (bonus pour les zones sous-couvertes).

Le module rounds gère la valuation de ces apports comme tout autre travail (non-code).

## Composants transverses

### Modèle économique du token

Voir [`token_model.md`](token_model.md) — un seul token, valeur travail comme principe unifiant, mint à NAV, refusabilité symétrique entre apports cash et travail, gouvernance Top-X holders.

### Moteur de valuation

Voir [`value_engine.md`](value_engine.md) — agent IA fact-only sur artefacts Git, rubric et grille de taux publics et versionnés, fenêtre de challenge 7 jours, ratification par panel des Top-X holders en cas de contestation.

### Oracles météo

Phase 3+. Architecture cible :
1. Source primaire : NOAA / NWS pour les marchés US (résolutions Kalshi-compatibles).
2. Source secondaire : ECMWF / Météo-France / DWD pour les marchés européens à venir.
3. Cross-validation : DePIN stations propres pour résolution locale haute fréquence.

Le module `predictor/src/kalshi/resolution.py` actuel sert de prototype : règles précises de mapping station ↔ market, gestion des arrondis, conventions Trace. Sera ré-utilisé et étendu pour l'oracle on-chain.

### Stack data

- Forecasts : Open-Meteo (gratuit, multi-modèle) en POC. Aurora/Pangu/FourCastNet/GenCast via HuggingFace + GPU cloud en Phase A.2.
- Historical : ERA5 via Open-Meteo.
- Markets Kalshi : API REST publique (lecture). Intégration write API quand DAO active si élargissement à d'autres prediction markets.
- Crowdsourced : à intégrer (PWS, Twitter, traffic cams).

## Décisions ouvertes

- **Chain de déploiement** : Base / Arbitrum / Optimism. Critères : gas, écosystème DeFi/risk-pool, custody options.
- **Stable de bankroll** : USDC, EURC, multi-stable. Impact : frais conversion Kalshi (USD only).
- **Custody Kalshi POC** : compte personnel JS, structure intermédiaire LLC US, foundation. Détermine la structure juridique amont.
- **Toolchain smart contracts** : Foundry retenu, à graver dans `contracts/README.md`.
- **Wallet registry** : fichier signé en Phase 1 (`rounds/WALLETS.md`), registry on-chain à partir de Phase 2.

## Voir aussi

- Modèle de tokens (§7.7 Garde-fous) → [`token_model.md`](token_model.md)
- Moteur de valuation (§7 Garde-fous opérationnels) → [`value_engine.md`](value_engine.md)
- **Projet de statuts FR** (art. 4 bis « Limite des engagements de couverture et principe de transparence radicale » + art. 32 « Moteur de valuation et émission de tokens ») → [`../../statuts-aratea-v0-projet-2026-05-16.md`](../../statuts-aratea-v0-projet-2026-05-16.md)
- **Draft Articles of Association EN** → [`../../statuts-aratea-v0-projet-2026-05-16-EN.md`](../../statuts-aratea-v0-projet-2026-05-16-EN.md)
