# pizza-clock/rpi_image

## Prerequisites

- Nix (or Nixos installation)
- Raspberry Pi Zero 2 W
- micro SD card (at least 8 GB)

## How it works

- Create a bootable SD image using [`raspberry-pi-nix`](https://github.com/nix-community/raspberry-pi-nix).
- Launch the [`luakit`](https://github.com/NixOS/nixpkgs/blob/nixos-24.11/pkgs/by-name/lu/luakit/package.nix#L88) browser in fullscreen mode using the [`cage`](https://github.com/NixOS/nixpkgs/blob/master/pkgs/applications/window-managers/cage/default.nix) compositor.

## Build SD image

```sh
# Edit config as needed (Timezone, SSID, password, etc.)
$ editor localConfig.nix

# Build SD image
$ nix build '.#nixosConfigurations.rpi.config.system.build.sdImage' --show-trace --print-build-logs --verbose

# Extract image
$ zstd -d result/sd-image/nixos-sd-image-24.11.20250123.035f8c0-aarch64-linux.img.zst -o rpi.img

# Write to SD card
$ sudo dd if=rpi.img of=${SD_DEVICE} bs=4M status=progress
```

## Reconfigure via SSH

- See also: `Compiling through binfmt QEMU` in https://nixos.wiki/wiki/NixOS_on_ARM

```sh
# Reconfigure via SSH
$ nixos-rebuild switch --flake  .#rpi --target-host root@${RPI_IP} --build-host localhost
```

## Ideas

- Read-only rootfs
- Introduce fake-hwclock or alternatives