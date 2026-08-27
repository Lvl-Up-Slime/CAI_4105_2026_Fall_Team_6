{
  description = "Jupiter Lab dev environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs";

  outputs = { self, nixpkgs }: {
    devShells.x86_64-linux.default = let
      pkgs = nixpkgs.legacyPackages.x86_64-linux;
    in
    pkgs.mkShell {
      buildInputs = with pkgs; [
        pyright
        nil
        nixd
        fish
        (pkgs.python3.withPackages (python-pkgs: [
            python-pkgs.pandas
            python-pkgs.requests
            python-pkgs.numpy
            python-pkgs.jupyterlab

        ]))
      ];
    };
  };
}
