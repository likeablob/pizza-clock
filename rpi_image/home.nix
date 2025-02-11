{ config, pkgs, ... }:

{
  home.username = "user";
  home.homeDirectory = "/home/user";

  # encode the file content in nix configuration file directly
  home.file.".config/luakit/userconf.lua".text = ''
    local window = require "window"
    window.add_signal("init", function (w)
        w.win.fullscreen = true; 
    end)
  '';

  home.stateVersion = "24.11";
  programs.home-manager.enable = true;
}
