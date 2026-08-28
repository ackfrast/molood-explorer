# Local installation

MolOOD Explorer can run entirely on your own computer. Python, RDKit, Streamlit, and all other dependencies are installed into `.molood-env` inside this folder. Existing Python and Conda installations are not changed. Internet access is needed during the first installation only; normal use and molecular analysis are local and offline.

## Windows 10/11 (64-bit)

Open the extracted folder in File Explorer. Shift-right-click an empty area, choose **Open PowerShell window here** (or open Windows Terminal in this folder), then run:

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

If macOS asks for permission to run a downloaded program, approve Micromamba in **System Settings → Privacy & Security**.

## Linux (x86-64 or ARM64)

Open a terminal in the extracted folder and run:

```bash
bash scripts/install-local.sh
bash scripts/run-local.sh
```

The UI opens at `http://127.0.0.1:8501`. It is accessible only from your own computer. Stop it with `Ctrl+C` in the terminal.

Private input files can be placed under `data/private/`; they are excluded from Git. Output ZIP files are downloaded through the browser, while CLI outputs default to whichever directory you select.

## Updating or reinstalling

Run the platform installation command again to update the environment. If installation was interrupted, rerun it. The environment is intentionally not included in the download because it is operating-system and CPU specific and would make the archive several gigabytes larger.

