// SPDX-License-Identifier: Apache-2.0
pragma solidity 0.8.24;

import {Test} from "forge-std/Test.sol";

import {DeployArateaPhase1} from "../../script/DeployArateaPhase1.s.sol";
import {VerifyDeployment} from "../../script/VerifyDeployment.s.sol";
import {AugPocToken} from "../../src/token/AugPocToken.sol";
import {RoundRegistry} from "../../src/rounds/RoundRegistry.sol";

/// @title  VerifyDeploymentTest — exécute VerifyDeployment contre un déploiement frais.
/// @notice Revue 2026-06-10 B2 / finding S-1 : VerifyDeployment échouait toujours
///         (assertion name attendait "Aratea POC Token" alors que le token déploie
///         "Augure POC Token"). Aucun test ne couvrait ce filet post-déploiement —
///         ce test l'aurait attrapé en faisant reverter run().
contract VerifyDeploymentTest is Test {
    // Anvil default account #0 — déterministe, jamais utilisé en prod.
    address internal constant ANVIL_TEST_ADDR = 0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266;

    function _deploy() internal returns (AugPocToken token, RoundRegistry registry, address admin) {
        vm.setEnv("ADMIN_ADDRESS", "0xf39Fd6e51aad88F6F4ce6aB8827279cffFb92266");
        DeployArateaPhase1 deploy = new DeployArateaPhase1();
        DeployArateaPhase1.DeploymentResult memory result = deploy.run();
        return (result.token, result.registry, result.admin);
    }

    function _wireEnv(
        AugPocToken token,
        RoundRegistry registry,
        address admin
    ) internal {
        vm.setEnv("TOKEN_ADDRESS", vm.toString(address(token)));
        vm.setEnv("REGISTRY_ADDRESS", vm.toString(address(registry)));
        vm.setEnv("ADMIN_ADDRESS", vm.toString(admin));
    }

    /// @dev Le filet doit passer sur un déploiement frais et conforme. Avant le fix,
    ///      l'assertion name "Aratea POC Token" faisait reverter run() ici.
    function test_VerifyDeployment_passesOnFreshDeployment() public {
        (AugPocToken token, RoundRegistry registry, address admin) = _deploy();
        // Le nom on-chain attendu par le filet.
        assertEq(token.name(), "Augure POC Token");

        _wireEnv(token, registry, admin);

        VerifyDeployment verify = new VerifyDeployment();
        verify.run(); // ne doit PAS reverter
    }

    /// @dev Garde-fou : la vérification n'est pas vacuante — un admin erroné fait
    ///      bien reverter run() (sinon le filet ne vérifierait rien).
    function test_VerifyDeployment_revertsOnWrongAdmin() public {
        (AugPocToken token, RoundRegistry registry,) = _deploy();
        _wireEnv(token, registry, address(0xBAD));

        VerifyDeployment verify = new VerifyDeployment();
        vm.expectRevert();
        verify.run();
    }
}
