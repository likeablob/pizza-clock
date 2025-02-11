{
  pkgs,
  lib,
  localConfig,
  ...
}:
{
  nix.settings = {
    sandbox = false;
    experimental-features = [
      "nix-command"
      "flakes"
    ];
  };
  time.timeZone = localConfig.timeZone;
  users.users.root.initialPassword = "root";
  networking = {
    hostName = localConfig.hostName;
    useDHCP = false;
    interfaces = {
      wlan0.useDHCP = true;
    };
  };

  raspberry-pi-nix.board = "bcm2711";
  # This is required to prevent rebuild of several dependencies such as ffmpeg etc.
  raspberry-pi-nix.libcamera-overlay.enable = false;

  security.pam.services.sshd.allowNullPassword = false;
  services.openssh = {
    enable = true;
    openFirewall = true;
    settings = {
      PermitRootLogin = "yes";
      PasswordAuthentication = false;
      PermitEmptyPasswords = "no";
    };
  };

  networking.wireless.enable = true;
  networking.wireless.networks = {
    ${localConfig.wifiSsid} = {
      psk = localConfig.wifiPassword;
    };
  };

  environment.systemPackages = [
    pkgs.htop
    pkgs.neofetch
    pkgs.libinput
    pkgs.foot
    pkgs.cmatrix
    pkgs.luakit
  ];

  systemd.services = {
    disable-wifi-power-management = {
      enable = true;
      description = "Disable wifi power management";
      serviceConfig = {
        Type = "oneshot";
      };
      path = [ "/run/current-system/sw" ];
      wantedBy = [ "network-online.target" ];
      script = "iw wlan0 set power_save off";
    };
  };

  services.speechd.enable = false;
  services.orca.enable = false;
  services.pipewire.enable = false;

  services.cage = {
    enable = true;
    # program = "${pkgs.foot}/bin/foot -F ${pkgs.cmatrix}/bin/cmatrix";
    program = "${pkgs.luakit}/bin/luakit ${localConfig.pizzaClockUrl}";
    user = "user";
    environment = {
      WLR_LIBINPUT_NO_DEVICES = "1";
    };
  };

  # A workaround for hiding mouse cursor by block-listing vc4-hdmi input device.
  # ref: https://github.com/cage-kiosk/cage/issues/299
  # Unfortunately, the midori browser does not work without input.
  services.udev.extraRules = "ACTION!=\"remove\", ATTRS{name}==\"vc4-hdmi\", ENV{LIBINPUT_IGNORE_DEVICE}=\"1\"\n";

  swapDevices = [
    {
      device = "/swapfile";
      size = 1 * 1024; # 1 GiB
    }
  ];

  hardware = {
    raspberry-pi = {
      config = {
        all = {
          options = {
            gpu_mem = {
              value = "64";
              enable = true;
            };
            "hdmi_force_hotplug" = {
              value = "1";
              enable = true;
            };
            "hdmi_group" = {
              value = "2";
              enable = true;
            };
            "hdmi_mode" = {
              value = "87";
              enable = true;
            };
            "hdmi_timings" = {
              value = "720 0 40 40 200 720 0 24 4 12 0 0 0 78 0 59400000 0";
              enable = true;
            };
            "display_hdmi_rotate" = {
              value = "2";
              enable = true;
            };
            "max_framebuffer_width" = {
              value = "720";
              enable = true;
            };
            "max_framebuffer_height" = {
              value = "720";
              enable = true;
            };
            "max_framebuffers" = {
              value = "2";
              enable = true;
            };
            "disable_overscan" = {
              value = "1";
              enable = true;
            };
            "config_hdmi_boost" = {
              value = "9";
              enable = true;
            };
            "hdmi_pixel_encoding=" = {
              value = "2";
              enable = true;
            };
          };
          base-dt-params = {
            BOOT_UART = {
              value = 1;
              enable = true;
            };
            uart_2ndstage = {
              value = 1;
              enable = true;
            };
          };
          dt-overlays = {
            disable-bt = {
              enable = true;
              params = { };
            };
          };
        };
      };
    };
  };

  users.users.user = {
    isNormalUser = true;
    description = "";
    extraGroups = [
      "wheel"
    ];
    openssh.authorizedKeys.keys = [
      localConfig.sshPubKey
    ];
  };

  users.users.root.openssh.authorizedKeys.keys = [
    localConfig.sshPubKey
  ];

  security.sudo.extraRules = [
    {
      users = [ "user" ];
      commands = [
        {
          command = "ALL";
          options = [
            "SETENV"
            "NOPASSWD"
          ];
        }
      ];
    }
  ];
}
