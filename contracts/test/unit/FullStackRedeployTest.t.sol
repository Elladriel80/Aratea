// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";

import {DeployArateaPhase1} from "../../script/DeployArateaPhase1.s.sol";
import {DeployPhase2Governor} from "../../script/DeployPhase2Governor.s.sol";
import {AugPocToken} from "../../src/token/AugPocToken.sol";
import {RoundRegistry} from "../../src/rounds/RoundRegistry.sol";
import {MintGovernor} from "../../src/governance/MintGovernor.sol";
import {IRoundRegistry} from "../../src/interfaces/IRoundRegistry.sol";

/// @title  FullStackRedeployTest — dry-run complet Phase 1 → Genesis → Phase 2
/// @notice Valide la séquence de redéploiement complet suite au bloqueur DEPLOY-1 :
///         le registry déployé en mai manquait ROUND_CHALLENGER_ROLE, rendant
///         DeployPhase2Governor inopérant. Ce test prouve que la séquence corrigée
///         fonctionne de bout en bout sur le code ACTUEL.
///
///         Exécuter avec :
///           forge test --match-contract FullStackRedeployTest -vv
///         Ou sur fork testnet :
///           forge test --match-contract FullStackRedeployTest --fork-url $RPC_ARBITRUM_SEPOLIA -vv
contract FullStackRedeployTest is Test {
    // Adresses Anvil de référence (mêmes rôles que la vrai séquence Ledger)
    address internal constant ADMIN     = 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266;
    address internal constant KEEPER    = 0x70997970C51812dc3A010C7d01b50e0d17dc79C8;
    // Bénéficiaire genesis = fondateur (identique à la prod)
    address internal constant ELLADRIEL = 0x9a94552DCB67F036af6eccc9111b749856ab8EEA;

    uint256 internal constant GENESIS_AMOUNT_WEI  = 34_039_500 ether;
    // Fenêtre courte pour testnet (5 min) — permet Phase 1→Genesis→Phase2 en UNE session.
    // Mainnet : passer CHALLENGE_WINDOW_SECONDS=2592000 (30 jours) à ProposeGenesisRound.
    uint32  internal constant GENESIS_WINDOW_SEC   = 300;
    // URI identique à la prod — même rapport de valorisation 2026-05
    string  internal constant GENESIS_IPFS =
        "ipfs://bafybeih5jb2vk577w57uw62m4j7opyke4poryrphscydhzmd3htvm2ug7u";

    AugPocToken   internal token;
    RoundRegistry internal registry;
    MintGovernor  internal governor;
    bytes32       internal genesisHash;

    function setUp() public {
        // ── Phase 1 : déployer token + registry (code actuel, avec ROUND_CHALLENGER_ROLE) ──
        vm.setEnv("ADMIN_ADDRESS", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266");
        DeployArateaPhase1 deploy1 = new DeployArateaPhase1();
        DeployArateaPhase1.DeploymentResult memory r1 = deploy1.run();
        token    = r1.token;
        registry = r1.registry;

        // Preuve que ROUND_CHALLENGER_ROLE est bien défini (échouerait sur l'ancien déployé)
        bytes32 challengerRole = registry.ROUND_CHALLENGER_ROLE();
        assertTrue(challengerRole != bytes32(0), "ROUND_CHALLENGER_ROLE doit exister");

        // ── Genesis : proposer + attendre 30j + exécuter (AVANT Phase 2, admin tient EXECUTOR) ──
        address[] memory bens = new address[](1);
        bens[0] = ELLADRIEL;
        uint256[] memory amts = new uint256[](1);
        amts[0] = GENESIS_AMOUNT_WEI;
        genesisHash = keccak256(abi.encode(bens, amts, GENESIS_IPFS));

        // Admin tient ROUND_PROPOSER_ROLE depuis Phase 1
        vm.prank(ADMIN);
        registry.proposeRound(genesisHash, bens, amts, GENESIS_IPFS, GENESIS_WINDOW_SEC);

        assertEq(
            uint8(registry.statusOf(genesisHash)),
            uint8(IRoundRegistry.RoundStatus.Proposed),
            "genesis doit etre Proposed"
        );

        // Fast-forward fenêtre courte (300 s testnet — vs 30 j mainnet)
        vm.warp(block.timestamp + GENESIS_WINDOW_SEC + 1);

        // Admin tient ROUND_EXECUTOR_ROLE depuis Phase 1 — AVANT révocation Phase 2
        vm.prank(ADMIN);
        registry.executeRound(genesisHash);

        assertEq(
            uint8(registry.statusOf(genesisHash)),
            uint8(IRoundRegistry.RoundStatus.Executed),
            "genesis doit etre Executed"
        );
        assertEq(token.totalSupply(), GENESIS_AMOUNT_WEI, "supply = tokens genesis");

        // ── Phase 2 : déployer MintGovernor + recâbler les rôles ──
        vm.setEnv("TOKEN_ADDRESS",    vm.toString(address(token)));
        vm.setEnv("REGISTRY_ADDRESS", vm.toString(address(registry)));
        vm.setEnv("KEEPER_ADDRESS",   "0x70997970C51812dc3A010C7d01b50e0d17dc79C8");
        DeployPhase2Governor deploy2 = new DeployPhase2Governor();
        governor = deploy2.run();
    }

    // ── Assertions ──────────────────────────────────────────────────────────────────

    function test_Genesis_TokensMinted() public view {
        assertEq(
            token.balanceOf(ELLADRIEL),
            GENESIS_AMOUNT_WEI,
            "fondateur doit avoir les tokens genesis"
        );
        assertEq(token.totalSupply(), GENESIS_AMOUNT_WEI);
        assertEq(token.totalSupply() / 1e18, 34_039_500, "34 039 500 tokens en unites humaines");
    }

    function test_ChallengerRole_DefinedOnNewRegistry() public view {
        bytes32 role = registry.ROUND_CHALLENGER_ROLE();
        assertTrue(role != bytes32(0), "ROUND_CHALLENGER_ROLE existe sur le NOUVEAU registry");
        assertTrue(
            registry.hasRole(role, address(governor)),
            "governor tient ROUND_CHALLENGER_ROLE"
        );
    }

    function test_Phase2_AdminLosesExecutorAndProposer() public view {
        assertFalse(
            registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), ADMIN),
            "REG-1: admin ne doit PAS tenir ROUND_EXECUTOR_ROLE apres Phase 2"
        );
        assertFalse(
            registry.hasRole(registry.ROUND_PROPOSER_ROLE(), ADMIN),
            "admin ne doit PAS tenir ROUND_PROPOSER_ROLE apres Phase 2"
        );
    }

    function test_Phase2_GovernorHoldsAllOperationalRoles() public view {
        assertTrue(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(),   address(governor)));
        assertTrue(registry.hasRole(registry.ROUND_PROPOSER_ROLE(),   address(governor)));
        assertTrue(registry.hasRole(registry.ROUND_CANCELLER_ROLE(),  address(governor)));
        assertTrue(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), address(governor)));
        assertFalse(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(),   address(governor)));
    }

    function test_Phase2_KeeperIsProposerOnly() public view {
        assertTrue(registry.hasRole(registry.ROUND_PROPOSER_ROLE(), KEEPER));
        assertFalse(registry.hasRole(registry.ROUND_EXECUTOR_ROLE(), KEEPER));
        assertFalse(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), KEEPER));
        assertFalse(registry.hasRole(registry.ROUND_CHALLENGER_ROLE(), KEEPER));
    }

    function test_Phase2_AdminKeepsCircuitBreaker() public view {
        assertTrue(registry.hasRole(registry.DEFAULT_ADMIN_ROLE(), ADMIN));
        assertTrue(registry.hasRole(registry.ROUND_CANCELLER_ROLE(), ADMIN));
    }

    function test_Phase2_GovernorWiredCorrectly() public view {
        assertEq(address(governor.registry()), address(registry));
        assertEq(address(governor.token()),    address(token));
        assertTrue(token.hasRole(token.MINTER_ROLE(), address(registry)));
        assertFalse(token.hasRole(token.MINTER_ROLE(), address(governor)));
    }
}
