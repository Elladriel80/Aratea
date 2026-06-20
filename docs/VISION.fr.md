# Aratea — Vision & One-Pager

> v0.1 — Juin 2026

---

## Le Problème

L'assurance paramétrique et les marchés de prédiction traditionnels reposent
sur des oracles centralisés, des valorisations opaques et des données en silos.
Les assurés ne peuvent pas vérifier qu'une formule de remboursement est juste,
les fournisseurs de données ne sont pas rémunérés équitablement pour leurs
mesures, et « la maison » fixe toujours les règles en coulisses.

---

## Ce que Construit Aratea

Aratea est un **protocole d'assurance mutualiste décentralisée** combinant
trois couches interconnectées :

### 1 — Moteur Prédictif

Un signal assisté par des agents de traitement qui estime la probabilité d'un
déclencheur paramétrique (température, événement météo…) avant la fermeture du
marché on-chain. Le signal est entraîné sur des données d'observation
historiques, validé sur un holdout gelé par un sign-test rigoureux, et promu
uniquement quand il bat démontrablement le prix de consensus du marché. La
logique de prédiction tourne hors chaîne en open source ; le règlement tourne
on-chain sans tiers de confiance.

État actuel : régression logistique ensembliste entraînée sur 61 dates
historiques. Brier holdout 0,137 vs marché 0,134. Recherche active pour
combler l'écart.

### 2 — DAO Mutualiste

Une couche de gouvernance pondérée par les tokens où les contributeurs gagnent
des `AUG-POC` pour un travail vérifiable (prédictions correctes, données de
qualité, revue de code…). Le token n'a pas de calendrier de mint spéculatif :
chaque token est adossé à un travail validé à la Valeur Nette d'Inventaire.
Le mint est contrôlé par un contrat `RoundRegistry` ; les rounds sont proposés
mensuellement, ouverts à une fenêtre de challenge de 7 jours, et nécessitent
une super-majorité token-weighted pour être annulés. Une fois l'edge Brier
confirmé, le protocole peut payer les sinistres paramétriques directement depuis
le fonds mutuel, gouverné on-chain.

### 3 — Couche de Données DePIN (Phase 4)

Des nœuds d'infrastructure physique décentralisée (stations météo, capteurs
IoT) récompensés en `AUG-POC` pour la fourniture de données d'observation
vérifiables. Cela crée un marché de données transparent, auditable et résistant
à la défaillance d'un seul fournisseur — à l'opposé d'un oracle centralisé.

---

## Modèle de Token

- **Un seul token, une seule mécanique** : travail → contribution validée →
  mint à la VNI.
- **Pas de pré-mine, pas d'allocation VC** : chaque `AUG-POC` en circulation
  représente une contribution vérifiée, enregistrée on-chain.
- **Offre bornée par gouvernance** : le fonds mutuel détermine les montants de
  mint mensuels via la grille de valorisation ; les détenteurs de tokens peuvent
  rejeter tout round jugé sur-évalué.
- **Transparence radicale** : le ratio de couverture (engagements / capital) est
  visible on-chain en permanence.

---

## Phases

| Phase | Objectif | Statut |
|-------|----------|--------|
| 1 — Kalshi POC | Prouver un edge prédictif sur un marché de prédiction réel | En cours |
| 2 — Token DAO | Déployer token + gouvernance on-chain (Arbitrum Sepolia) | Contrats prêts, testnet en attente |
| 3 — Mutuelle Paramétrique | Premier produit d'assurance on-chain adossé au signal prédictif | Planifié |
| 4 — Couche DePIN | Infrastructure météo décentralisée | Planifié |

---

## État Actuel

- **162 tests passants** (unitaires + fuzz + invariants) sur `AugPocToken`,
  `RoundRegistry` et `MintGovernor`. 91 % de couverture branches sur la gouvernance.
- **Sécurité** : Slither CI (fail on medium), Gitleaks scan secrets, GitHub
  Actions SHA-fixées, writes oracle gardés par `KEEPER_ROLE`.
- **Prédiction** : 61 dates historiques dans le jeu d'entraînement. Feature set
  v3 (`p_consensus`, `forecast_spread`, `days_ahead`) en production.
- **Open source** : Apache-2.0. Contributions via workflow PR standard.

---

## Pour les Contributeurs

Le projet est conçu pour les bâtisseurs qui tiennent aux systèmes vérifiables.
Contributions bienvenues dans :

- **Smart contracts** (Solidity / Foundry) : couche de règlement, gouvernance, slashing.
- **Recherche prédictive** (Python) : feature engineering, calibration, backtesting.
- **Infrastructure données** : pipelines IPFS, feeds oracle on-chain.
- **Documentation** : bilingue FR/EN, spécifications de protocole.

Voir `CONTRIBUTING.md` et `STATUS.md` pour l'état actuel de chaque composant.

---

## Contact

Dépôt : https://github.com/Elladriel80/Aratea  
Licence : Apache-2.0
