{
  perSystem =
    { config, pkgs, ... }:
    {
      devShells.default = pkgs.mkShell {
        inherit (config.checks.prek) shellHook;
        buildInputs = [
          pkgs.just
          pkgs.uv
        ]
        ++ config.checks.prek.enabledPackages;
      };
    };
}
