# Local installation

MolOOD Explorer can run entirely on your own computer. Python, RDKit, Streamlit, and all other dependencies are installed into `.molood-env` inside this folder. Existing Python and Conda installations are not changed. Internet access is needed during the first installation only; normal use and molecular analysis are local and offline.

The first installation downloads approximately 265 MB. The usable environment is approximately 1.3 GB; temporary package caches are removed automatically after a successful installation. Exact allocated size varies by operating system and filesystem.

## Windows 10/11 (64-bit)

After extracting the release ZIP, double-click `Install-Windows.bat`. When installation finishes, double-click `Run-Windows.bat`.

The equivalent terminal commands are:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\install-local.ps1
powershell -ExecutionPolicy Bypass -File scripts\run-local.ps1
```

## macOS (Intel or Apple Silicon)

Open Terminal, change into the extracted folder, then run:

```bash
bash scripts/install-local.sh
bash scripts/run-local.sh
```

The release also includes `Install-macOS-Linux.command` and `Run-macOS-Linux.command` launchers. macOS may require right-clicking a downloaded launcher and choosing **Open** the first time.

If macOS asks for permission to run a downloaded program, approve Micromamba in **System Settings → Privacy & Security**.

## Linux (x86-64 or ARM64)

Open a terminal in the extracted folder and run:

```bash
bash scripts/install-local.sh
bash scripts/run-local.sh
```

The UI normally opens at `http://127.0.0.1:8501`. If that port is already occupied, the launcher asks the operating system for another available local port; a URL such as `http://127.0.0.1:57050` is normal. Always open the exact URL printed in the PowerShell/terminal window. The port may differ each time. The UI is accessible only from your own computer. Keep the launcher window open and press `Ctrl+C` there to stop the app.

On managed Windows computers, the installer keeps temporary files under `.local-temp` inside the extracted project. It does not require access to pytest's usual `AppData\\Local\\Temp` location. If an older v0.1.0 installer stopped at `Project tests failed` with `WinError 5`, the environment was already installed; run `scripts\\run-local.ps1` directly or update to v0.1.1.

Private input files can be placed under `data/private/`; they are excluded from Git. Output ZIP files are downloaded through the browser, while CLI outputs default to whichever directory you select.

## Disk usage and cleanup

Each extracted release folder has its own `.molood-env`. Do not install several release folders unless you intentionally want several independent copies: `molood-explorer-0.1.1`, `molood-explorer-0.2.0`, and similar folders can each consume more than 1 GB.

For an installation made with v0.2.0 or earlier, remove only the re-downloadable Micromamba cache from PowerShell:

```powershell
$env:MAMBA_ROOT_PREFIX = (Resolve-Path .\.local-tools\mamba-root).Path
.\.local-tools\micromamba.exe clean --all --yes
```

On macOS/Linux:

```bash
export MAMBA_ROOT_PREFIX="$PWD/.local-tools/mamba-root"
./.local-tools/bin/micromamba clean --all --yes
```

These commands keep `.molood-env`, the application, and molecular data. Old extracted release folders can be deleted after confirming that all needed input/output files have been copied elsewhere. Do not delete your current `.molood-env` unless you want to reinstall.

## Updating or reinstalling

Run the platform installation command again to update the environment. If installation was interrupted, rerun it. The environment is intentionally not included in the download because it is operating-system and CPU specific and would make the archive several gigabytes larger.
