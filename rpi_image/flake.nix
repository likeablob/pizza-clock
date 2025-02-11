{
  description = "Pizza Clock NixOS image for Raspberry Pi Zero 2 W";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-24.11";
    rpi-nix.url = "github:nix-community/raspberry-pi-nix/master";
    home-manager = {
      url = "github:nix-community/home-manager/release-24.11";
      inputs.nixpkgs.follows = "nixpkgs";
    };
  };

  outputs =
    inputs@{
      self,
      nixpkgs,
      rpi-nix,
      home-manager,
      ...
    }:
    {
      localConfig = import ./localConfig.nix;
      nixosConfigurations = {
        rpi = nixpkgs.lib.nixosSystem {
          system = "aarch64-linux";
          modules = [
            rpi-nix.nixosModules.raspberry-pi
            rpi-nix.nixosModules.sd-image
            ./configuration.nix
            home-manager.nixosModules.home-manager
            {
              home-manager.useGlobalPkgs = true;
              home-manager.useUserPackages = true;
              home-manager.users.user = import ./home.nix;
            }
          ];
          specialArgs = {
            localConfig = self.localConfig;
          };
        };
      };
    };

  nixConfig = {
    extra-substituters = [ "https://nix-community.cachix.org" ];
    extra-trusted-public-keys = [
      "nix-community.cachix.org-1:mB9FSh9qf2dCimDSUo8Zy7bkq5CX+/rkCWyvRCYg3Fs="
    ];
  };
}
