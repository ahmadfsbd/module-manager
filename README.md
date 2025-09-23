# module-manager
A POC for modular software installation in shared Virtual Environments.
1. Use ./build for running or creatin build scripts for modules.
2. Build results are in ./modules, modules dir is not tracked and is used just for resulted builds.

## Script Placement
1. module-manager will be placed at /usr/local/bin/module-manager
2. Desktop application at /home/ivm/.local/share/applications/ModuleManager.desktop
3. Python GUI script at /usr/local/bin/module_manager_gui.py

## Systemd service for sartup loader
Create the systemd service at dest: /etc/systemd/system/startup-module-loader.service

```
[Unit]
Description=Load required modules at boot
After=network.target remote-fs.target

[Service]
Type=oneshot
ExecStart=/usr/local/bin/startup-module-loader.sh
Restart=on-failure
RestartSec=10s

[Install]
WantedBy=multi-user.target
```

Run daemon reload and start/enable service

```
systemctl daemon-reload
systemctl enable startup-module-loader.service
```
