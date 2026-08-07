# Contribuer à Aratea

> [Read in English](CONTRIBUTING.md)

Aratea récompense la valeur travail apportée au projet, sous toute forme : code, donnée, recherche, design, documentation, capital. Le système est **fact-only** : seul ce qui est commité dans Git compte.

## Étapes pour participer

1. **Lis** [`README.fr.md`](README.fr.md), [`rounds/RUBRIC.fr.md`](rounds/RUBRIC.fr.md), [`rounds/HOURLY_RATES.fr.md`](rounds/HOURLY_RATES.fr.md). Le modèle économique est non-conventionnel — assure-toi qu'il te convient avant d'investir du temps.
2. **Enregistre ton wallet** dans [`rounds/WALLETS.md`](rounds/WALLETS.md) (PR signé).
3. **Apporte de la valeur** dans le module pertinent :
   - **`predictor/`** — code, datasets, RFCs de recherche sur la prédiction.
   - **`contracts/`** — Solidity, specs, audits (Phase 2+).
   - **`rounds/`** — améliorations du rubric, du prompt, des scripts, de l'automatisation.
   - **`docs/`** — architecture, modèle token, RFCs sur le projet lui-même.
   - **Cash** — virement BTC à l'adresse multisig publiée. Subscription window mensuelle ; le cash est **soumis à ratification** comme tout autre apport et peut être refusé avec motivation écrite.
4. **Cooldown** : ta première contribution doit être mergée > 30 jours avant éligibilité au mint. Filtre les drive-by.

## Pas de plateformes de bounty tierces

Aratea dispose de son propre mécanisme de compensation via les rounds de mint mensuels (voir [`docs/bounty-mechanism.md`](docs/bounty-mechanism.md) et [`rounds/HOURLY_RATES.fr.md`](rounds/HOURLY_RATES.fr.md)). Ce mécanisme est **interne au projet** et entièrement décrit dans ce dépôt.

Ce dépôt **n'est pas enregistré** sur Opire, Algora, ou toute autre plateforme similaire. Les pull requests qui :

- réclament une bounty via une plateforme externe,
- demandent un paiement vers un compte PayPal, portefeuille crypto, ou tout service tiers dans le corps du PR ou dans les commentaires,
- sont ouvertes par des comptes自动化 faisant du ciblage de masse sur les labels `good-first-issue`,

seront **fermées sans examen**. Les récidivistes sont bloqués au niveau du dépôt. Ceci est indépendant du mécanisme de ratification interne qui ne s'applique qu'aux contributions faites via le processus PR décrit ici.

## Configuration locale

Choisis le module correspondant à ta modification et lance uniquement les vérifications pertinentes.

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

### Site statique et docs

Aucun build requis pour `site/` ou les modifications Markdown seules. Utilise les hooks pre-commit ci-dessous pour les vérifications d'hygiène.

## Style de code et vérifications de sécurité

Avant d'ouvrir un PR :

```bash
pip install pre-commit
pre-commit run --all-files
```

Les hooks lancent un scan de secrets et des vérifications basiques d'hygiène des fichiers. Ne les bypass pas sauf si un mainteneur te le demande explicitement et que la raison est documentée dans le PR.

Ne commite jamais de vrais fichiers `.env`, URLs de webhooks, clés privées, seeds de wallet, tokens API, ou datasets privés. Utilise les fichiers `.env.example` comme documentation uniquement.

## Comment proposer une correction

1. Ouvre ou picking une issue avant de commencer un travail non-trivial.
2. Garde le PR cantonné à un module et un problème.
3. Lie l'issue dans la description du PR.
4. Explique la valeur de l'artefact : ce qui a changé, pourquoi c'est important, et comment ça peut être vérifié à partir de preuves visibles dans Git.
5. Inclut les commandes que tu as lancées et leur résultat.
6. Si une commande ne peut pas être lancée localement, explique pourquoi et nomme la plus petite vérification côté reviewer qui couvrirait le changement.

Les bonnes premières issues sont suivies dans [`docs/contributor-starter-issues.md`](docs/contributor-starter-issues.md).
Le placeholder de la future politique de bounty est dans [`docs/bounty-mechanism.md`](docs/bounty-mechanism.md).

## Ce qui n'est PAS valorisé

- Promesses, intentions, brainstorms purs.
- PRs ouverts non-mergés, ou mergés puis revertés.
- Discord, DM, conversations : non-tracé dans Git, pas valorisé.
- Heures auto-déclarées ou submissions narratives : le système ne les accepte pas.
- Code auto-généré sans curation humaine documentée.
- Gaming visible (commits fragmentés, diffs gonflés, sock-puppet reviews).
- PRs de comptes de farming automatisés (corps au template "Implémentation Complète", réclamations de bounty-platform, signatures agent IA, handles génériques sans historique d'activité réelle).


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
