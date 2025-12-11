; Crystal POS Inno Setup Script
; Professional Windows Installer for Crystal POS Application

#define MyAppName "Crystal POS"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "Crystal POS Team"
#define MyAppURL "https://crystalpos.com"
#define MyAppExeName "CrystalPOS.exe"
#define ProjectRoot ".."

[Setup]
; App identity
AppId={{A1B2C3D4-E5F6-7890-ABCD-EF1234567890}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}

; Installation settings
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
AllowNoIcons=yes

; Output settings
OutputDir={#ProjectRoot}\dist\installer
OutputBaseFilename=CrystalPOS-Setup-{#MyAppVersion}
Compression=lzma2/ultra64
SolidCompression=yes
WizardStyle=modern

; Privileges
PrivilegesRequired=admin
PrivilegesRequiredOverridesAllowed=dialog

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1; Check: not IsAdminInstallMode

[Files]
; Backend files (excluding virtual env and build artifacts)
Source: "{#ProjectRoot}\backend\core\*"; DestDir: "{app}\backend\core"; Flags: ignoreversion recursesubdirs createallsubdirs
Source: "{#ProjectRoot}\backend\users\*"; DestDir: "{app}\backend\users"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\customers\*"; DestDir: "{app}\backend\customers"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\vendors\*"; DestDir: "{app}\backend\vendors"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\products\*"; DestDir: "{app}\backend\products"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\raw_materials\*"; DestDir: "{app}\backend\raw_materials"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\sales\*"; DestDir: "{app}\backend\sales"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\purchases\*"; DestDir: "{app}\backend\purchases"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\assets\*"; DestDir: "{app}\backend\assets"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\payments\*"; DestDir: "{app}\backend\payments"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\reports\*"; DestDir: "{app}\backend\reports"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\bank_accounts\*"; DestDir: "{app}\backend\bank_accounts"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "__pycache__,*.pyc"
Source: "{#ProjectRoot}\backend\manage.py"; DestDir: "{app}\backend"; Flags: ignoreversion
Source: "{#ProjectRoot}\backend\requirements.txt"; DestDir: "{app}\backend"; Flags: ignoreversion

; Frontend dist (built Vue app)
Source: "{#ProjectRoot}\frontend\dist\*"; DestDir: "{app}\frontend\dist"; Flags: ignoreversion recursesubdirs createallsubdirs

; Installer scripts
Source: "setup.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion
Source: "start-app.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion
Source: "start-backend.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion
Source: "start-frontend.ps1"; DestDir: "{app}\installer"; Flags: ignoreversion

[Dirs]
Name: "{app}\logs"; Permissions: users-modify
Name: "{app}\data"; Permissions: users-modify

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\installer\start-app.ps1"""; WorkingDir: "{app}"
Name: "{group}\Start Backend Server"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -File ""{app}\installer\start-backend.ps1"""; WorkingDir: "{app}"
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\installer\start-app.ps1"""; WorkingDir: "{app}"; Tasks: desktopicon

[Run]
; Run setup script after installation (visible console so users see progress)
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -File ""{app}\installer\setup.ps1"" ""{app}"""; StatusMsg: "Setting up Crystal POS (this may take a few minutes)..."; Flags: waituntilterminated

; Show setup log if exists (for debugging)
; Filename: "notepad.exe"; Parameters: """{app}\logs\setup_latest.log"""; Flags: postinstall skipifsilent shellexec nowait unchecked; Description: "View setup log"

; Option to launch app after install
Filename: "powershell.exe"; Parameters: "-NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File ""{app}\installer\start-app.ps1"""; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent

[UninstallRun]
; Stop any running processes
Filename: "powershell.exe"; Parameters: "-ExecutionPolicy Bypass -Command ""Stop-Process -Name python -Force -ErrorAction SilentlyContinue"""; Flags: runhidden

[UninstallDelete]
Type: filesandordirs; Name: "{app}\venv"
Type: filesandordirs; Name: "{app}\data"
Type: filesandordirs; Name: "{app}\logs"
Type: filesandordirs; Name: "{app}\backend\__pycache__"

[Messages]
WelcomeLabel2=This will install [name] on your computer.%n%nRequirements:%n- Python 3.10 or later must be installed%n- Internet connection for initial setup%n%nThe setup will automatically configure the database and create a default admin user.

[Code]
function IsPythonInstalled(): Boolean;
var
  ResultCode: Integer;
begin
  Result := Exec('python', '--version', '', SW_HIDE, ewWaitUntilTerminated, ResultCode) and (ResultCode = 0);
end;

function InitializeSetup(): Boolean;
var
  ErrorCode: Integer;
begin
  Result := True;
  
  if not IsPythonInstalled() then
  begin
    if MsgBox('Python is not installed or not in PATH.' + #13#10 + #13#10 +
              'Crystal POS requires Python 3.10 or later.' + #13#10 +
              'Would you like to download Python now?' + #13#10 + #13#10 +
              'Click Yes to open the Python download page, then run this installer again.',
              mbConfirmation, MB_YESNO) = IDYES then
    begin
      ShellExec('open', 'https://www.python.org/downloads/', '', '', SW_SHOWNORMAL, ewNoWait, ErrorCode);
    end;
    Result := False;
  end;
end;
