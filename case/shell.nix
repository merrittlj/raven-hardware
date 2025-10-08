{ pkgs ? import (fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-25.05") {} }:

pkgs.mkShellNoCC {
  packages = with pkgs; [
    python3
    python3Packages.pip

    openscad
  ];

  shellHook = ''
    python -m venv .venv
    source .venv/bin/activate

    pip install solidpython2
  '';
}

