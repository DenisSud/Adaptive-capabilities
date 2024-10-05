{
  description = "A Nix-flake-based Rust development environment";

  inputs = {
    nixpkgs.url = "https://flakehub.com/f/NixOS/nixpkgs/0.1.*.tar.gz";
    rust-overlay = {
      url = "github:oxalica/rust-overlay";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs = { self, nixpkgs, rust-overlay }:
    let
      supportedSystems = [ "x86_64-linux" "aarch64-linux" "x86_64-darwin" "aarch64-darwin" ];
      forEachSupportedSystem = f: nixpkgs.lib.genAttrs supportedSystems (system: f {
        pkgs = import nixpkgs {
          inherit system;
          overlays = [ rust-overlay.overlays.default self.overlays.default ];
        };
      });
    in
    {
      overlays.default = final: prev: {
        rustToolchain =
          let
            rust = prev.rust-bin;
          in
          if builtins.pathExists ./rust-toolchain.toml then
            rust.fromRustupToolchainFile ./rust-toolchain.toml
          else if builtins.pathExists ./rust-toolchain then
            rust.fromRustupToolchainFile ./rust-toolchain
          else
            rust.stable.latest.default.override {
              extensions = [ "rust-src" "rustfmt" ];
            };
      };

      devShells = forEachSupportedSystem ({ pkgs }: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            rustToolchain
            openssl
            pkg-config
            cargo-deny
            cargo-edit
            cargo-watch
            rust-analyzer

            # C++ development tools
            gcc
            gdb
            cmake
            gnumake

            llvmPackages.libclang
            llvmPackages.clang
          ];

          buildInputs = with pkgs; [
            opencv
            pkg-config
            gcc
            clang
            libclang
            glibc.dev
          ];

          env = {
            CPLUS_INCLUDE_PATH = "${pkgs.gcc-unwrapped}/include/c++/${pkgs.gcc-unwrapped.version}:${pkgs.gcc-unwrapped}/include/c++/${pkgs.gcc-unwrapped.version}/${pkgs.stdenv.targetPlatform.config}:${pkgs.glibc.dev}/include";
            RUST_SRC_PATH = "${pkgs.rustToolchain}/lib/rustlib/src/rust/library";
            LIBCLANG_PATH = "${pkgs.libclang.lib}/lib";
            OPENCV_LINK_LIBS = "opencv_core,opencv_imgproc,opencv_imgcodecs";
            OPENCV_LINK_PATHS = "${pkgs.opencv}/lib";
            RUST_BACKTRACE = 1;
          };

          shellHook = ''
            export PATH=$PATH:${pkgs.opencv}/bin
            export CPATH="${pkgs.glibc.dev}/include:${pkgs.clang.cc}/include:$CPATH"
          '';
        };
      });
    };
}
