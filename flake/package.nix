{
  perSystem =
    { pkgs, ... }:
    {
      packages = rec {
        steam-platform-stats = pkgs.python314Packages.buildPythonApplication {
          pname = "steam-platform-stats";
          version = "0.4.2";
          pyproject = true;

          src = ../.;

          nativeBuildInputs = with pkgs; [
            makeWrapper
            python314Packages.uv-build
          ];

          propagatedBuildInputs = with pkgs.python314Packages; [
            keyring
            pydantic
            requests
            rich
            secretstorage
            xdg-base-dirs
          ];

          makeWrapperArgs = [
            "--prefix PATH : ${
              pkgs.lib.makeBinPath [
                pkgs.fzf
                pkgs.libnotify
              ]
            }"
          ];

          meta = with pkgs.lib; {
            description = "Display user's Steam games statistics by platform";
            homepage = "https://github.com/blackfan321/steam-platform-stats";
            license = licenses.mit;
            mainProgram = "steam-platform-stats";
          };
        };
        default = steam-platform-stats;
      };
    };
}
