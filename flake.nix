{
  description = "steam-platform-stats — Steam games statistics by platform";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs =
    { self, nixpkgs }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
        "aarch64-darwin"
      ];
      forAllSystems = nixpkgs.lib.genAttrs systems;
    in
    {
      packages = forAllSystems (
        system:
        let
          pkgs = nixpkgs.legacyPackages.${system};
        in
        rec {
          steam-platform-stats = pkgs.python314Packages.buildPythonApplication {
            pname = "steam-platform-stats";
            version = "0.2.2";
            pyproject = true;

            src = ./.;

            nativeBuildInputs = with pkgs.python314Packages; [ uv-build ];

            propagatedBuildInputs = with pkgs.python314Packages; [
              argcomplete
              prettytable
              python-dotenv
              requests
              rich
              xdg-base-dirs
            ];

            meta = with pkgs.lib; {
              description = "Display user's Steam games statistics by platform";
              homepage = "https://github.com/blackfan321/steam-platform-stats";
              license = licenses.mit;
              mainProgram = "steam-platform-stats";
            };
          };
          default = steam-platform-stats;
        }
      );

      apps = forAllSystems (system: rec {
        steam-platform-stats = {
          type = "app";
          program = "${self.packages.${system}.steam-platform-stats}/bin/steam-platform-stats";
        };
        default = steam-platform-stats;
      });
    };
}
