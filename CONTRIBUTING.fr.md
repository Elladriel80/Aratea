# Contribuer à Aratea

> [Read in English](CONTRIBUTING.md)

Aratea récompense la valeur travail apportée au projet, sous toute forme : code, donnée, recherche, design, documentation, capital. Le système est **fact-only** : seul ce qui est commité dans Git compte.

## Pas de plateformes de bounty tierces

Aratea possède son propre mécanisme de compensation de la valeur travail à travers les sessions mensuelles de mint du projet (voir [`docs/bounty-mechanism.md`](docs/bounty-mechanism.md) et [`rounds/HOURLY_RATES.md`](rounds/HOURLY_RATES.md)). Ce mécanisme est **interne au projet** et entièrement décrit dans ce dépôt.

Ce dépôt n'est **pas** enregistré sur Opire, Algora ou toute autre plateforme de bounty tierce. Les pull requests qui :

- réclament un bounty via une plateforme externe,
- demandent un paiement vers une adresse PayPal, un portefeuille crypto ou tout service tiers dans le corps de la PR ou les commentaires,
- sont soumises par des comptes d'agents IA automatisés ciblant les labels `good-first-issue` en masse sur de nombreux dépôts,

seront **fermées sans examen**. Les récidivistes seront bloqués au niveau du dépôt. Ceci est indépendant du mécanisme de ratification du projet, qui s'applique uniquement aux contributions effectuées via le processus normal de PR décrit ci-dessous.

## Étapes pour participer

1. **Lis** [`README.md`](README.md), [`rounds/RUBRIC.md`](rounds/RUBRIC.md), et [`rounds/HOURLY_RATES.md`](rounds/HOURLY_RATES.md). Le modèle économique est non-conventionnel — assure-toi qu'il te convient avant d'investir du temps.
2. **Enregistre ton wallet** dans [`rounds/WALLETS.md`](rounds/WALLETS.md) (PR signé).
3. **Apporte de la valeur** dans le module pertinent :
   - **`predictor/`** — code, datasets, RFCs de recherche sur la prédiction.
   - **`contracts/`** — Solidity, specs, audits (Phase 2+).
   - **`rounds/`** — améliorations du rubric, du prompt, des scripts, de l'automatisation.
   - **`docs/`** — architecture, modèle token, RFCs sur le projet lui-même.
   - **Cash** — virement BTC à l'adresse multisig publiée. Subscription window mensuelle ; le cash est **soumis à ratification** comme tout autre apport et peut être refusé avec motivation écrite.
4. **Cooldown** : ta première contribution doit être mergée > 30 jours avant éligibilité au mint. Filtre les drive-by.

## Configuration locale

Choisis le module correspondant à ta modification et exécute uniquement les vérifications pertinentes.

### Predictor

```bash
cd predictor
python -m venv .venv
.venv\Scripts\activate   # Windows
source .venv/bin/activate              # Linux / macOS
pip install -r requirements.lock --require-hashes
python scripts/test_ensemble.py
python scripts/test_resolution.py
python scripts/test_microstructure.py
```

### Contracts

```bash
cd contracts
forge install --no-commit foundry-rs/forge-std@v1.9.4 OpenZeppelin/openzeppelin-contracts@v5.1.0
forge build
forge test -vvv
```

### Dashboard

```bash
cd dashboard
cp .env.example .env.local
npm install
npm run typecheck
npm run build
```

### Site statique et documentation

Aucune étape de build n'est requise pour `site/` ou la plupart des modifications uniquement en Markdown. Utilise les hooks pre-commit ci-dessous pour les contrôles d'hygiène.

## Style de code et contrôles de sécurité

Avant d'ouvrir une PR :

```bash
pip install pre-commit
pre-commit run --all-files
```

Les hooks exécutent la détection de secrets et des vérifications de base d'hygiène de fichiers. Ne les contourne pas sauf si un mainteneur te le demande explicitement et que la raison est documentée dans la PR.

Ne commite jamais de vrais fichiers `.env`, URLs de webhook, clés privées, clés RPC, phrases secrètes de portefeuille, tokens d'API ou jeux de données privés. Utilise les fichiers `.env.example` uniquement comme documentation.

## Comment proposer un patch

1. Ouvre ou choisis une issue avant de commencer un travail non trivial.
2. Garde la PR ciblée sur un seul module et un seul problème.
3. Lie l'issue dans la description de la PR.
4. Explique la valeur de l'artefact : ce qui a changé, pourquoi c'est important et comment cela peut être vérifié à partir des preuves visibles dans Git.
5. Inclus les commandes que tu as exécutées et leur résultat.
6. Si une commande ne peut pas être exécutée localement, explique pourquoi et indique la plus petite vérification côté réviseur qui couvrirait la modification.

Les starter issues sont suivies dans [`docs/contributor-starter-issues.md`](docs/contributor-starter-issues.md). L'emplacement réservé pour la future politique de bounty est [`docs/bounty-mechanism.md`](docs/bounty-mechanism.md).

## Ce qui n'est PAS valorisé

- Promesses, intentions, brainstorms purs.
- PRs ouverts non-mergés, ou mergés puis revertés.
- Discord, DM, conversations : non-tracé dans Git, pas valorisé.
- Heures auto-déclarées ou submissions narratives : le système ne les accepte pas.
- Code auto-généré sans curation humaine documentée.
- Gaming visible (commits fragmentés, diffs gonflés, sock-puppet reviews).
- PRs provenant de comptes de farming automatisés (corps de PR préformatés "Implementation Complete", réclamations sur des plateformes de bounty, signatures d'agents IA, pseudos génériques sans historique d'activité réel).

## Bonnes pratiques

- **Ouvre une issue avant un gros PR**, évite les efforts qui ne mergeront pas.
- **Lie tes PRs à des issues** pour que l'impact soit visible à l'agent.
- **Écris des descriptions PR et commit messages substantiels.** C'est l'input principal de l'agent — descriptions creuses → valuation au plancher.
- **Tests, doc, code propre augmentent ton coefficient qualité**, jusqu'à ×1,3.
- **Dette technique, régressions, travail incomplet le diminuent**, jusqu'à ×0,5.

## Mécanisme de challenge

Si tu estimes que ta valuation dans un round est incorrecte, dépose un **challenge formel** pendant la fenêtre de 7 jours :
- Commente le PR du round avec le label `challenge`.
- Signe le commentaire avec ton wallet enregistré (message signé de la forme `challenge-round-YYYY-MM-<ton-handle>`).
- Précise exactement le point de valuation contesté et pourquoi.

Un challenge déposé déclenche un vote du panel Top-X holders. Le panel valide la valuation telle quelle ou la renvoie avec instructions écrites pour révision.

## Conduite

Standard : respect, honnêteté intellectuelle, transparence. Sanctionné (warning → exclusion → slashing par vote 67 %) :

- Plagiat ou copie de code propriétaire sans attribution / licence compatible.
- Soumission répétée d'artefacts intentionnellement faits pour gamer le rubric.
- Manipulation des challenges (sock puppets, intimidation).
- Conduite hostile envers d'autres contributeurs.

## Questions

Discord du projet : `<lien à venir>`. Forum : `<lien à venir>`.
