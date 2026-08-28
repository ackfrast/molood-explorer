# Local installation

MolOOD Explorer can run entirely on your own computer. Python, RDKit, Streamlit, and all other dependencies are installed into `.molood-env` inside this folder. Existing Python and Conda installations are not changed. Internet access is needed during the first installation only; normal use and molecular analysis are local and offline.

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

The UI normally opens at `http://127.0.0.1:8501`. If that port is already occupied, the launcher automatically tries the next available port and prints the actual URL. It is accessible only from your own computer. Stop it with `Ctrl+C` in the terminal.

On managed Windows computers, the installer keeps temporary files under `.local-temp` inside the extracted project. It does not require access to pytest's usual `AppData\\Local\\Temp` location. If an older v0.1.0 installer stopped at `Project tests failed` with `WinError 5`, the environment was already installed; run `scripts\\run-local.ps1` directly or update to v0.1.1.

Private input files can be placed under `data/private/`; they are excluded from Git. Output ZIP files are downloaded through the browser, while CLI outputs default to whichever directory you select.

## Updating or reinstalling

Run the platform installation command again to update the environment. If installation was interrupted, rerun it. The environment is intentionally not included in the download because it is operating-system and CPU specific and would make the archive several gigabytes larger.
