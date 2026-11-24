## Installation

<badge color="info">Windows only</badge>

FractalScript's original runtime requires **Python 3.13** and **Pygame 2.6.1**.

### Step 1 — Install Python

Open PowerShell and paste:

```powershell
$installer = "$env:TEMP\python-3.13-installer.exe"

Invoke-WebRequest `
  "https://www.python.org/ftp/python/3.13.9/python-3.13.9-amd64.exe" `
  -OutFile $installer

Start-Process $installer -ArgumentList "/passive InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait

Remove-Item $installer
```

Close and reopen PowerShell after installation.

### Step 2 — Install Pygame

Paste this into PowerShell:

```powershell
py -3.13 -m pip install pygame==2.6.1
```

### Step 3 — Download FractalScript

Run this command in PowerShell:

```powershell
Invoke-WebRequest `
  "https://github.com/TheNewExtremeRay/EzCode/releases/download/1.0.0/EzCode.zip" `
  -OutFile "$env:USERPROFILE\Downloads\EzCode.zip"
```

Extract `EzCode.zip` directly into `C:\`.

Your directory should look like this:

```text
C:\
└── EzCode\
    ├── launcher.bat
    ├── Main Files\
    └── Examples4EzCode\
```

### Step 4 — Configure script launching

1. Navigate to `C:\EzCode\Examples4EzCode`.
2. Right-click any `.ez` file.
3. Select **Open with** → **Choose another app**.
4. Browse for an application on your computer.
5. Navigate to `C:\EzCode\`.
6. Select `launcher.bat`.

The launcher opens a Command Prompt window and starts your script.

### Step 5 — Test your installation (Optional)

Download the testing files:

[Download FractalScript Test Set](https://github.com/TheNewExtremeRay/EzCode/releases/download/EzCodeMainReleases/Test.Set.zip)

Open the included files individually to verify your installation.

