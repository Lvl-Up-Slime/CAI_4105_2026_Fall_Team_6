{
  description = "Container-based Jupyter environment";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";

  outputs = { nixpkgs, ... }:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
    in {
      devShells.${system}.default = pkgs.mkShell {
        packages = [ pkgs.podman ];

        shellHook = ''
          if podman build -t ml-jupyter .; then
            podman run --rm -it \
              -p 127.0.0.1:8888:8888 \
              -v "$PWD":/app \
              ml-jupyter
          fi
        '';
      };
    };
}
