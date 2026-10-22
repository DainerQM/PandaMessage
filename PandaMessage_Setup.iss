[Setup]
; Script generado para PandaMessage - Instalador Profesional
AppId={{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}
AppName=PandaMessage
AppVersion=1.0.0
AppVerName=PandaMessage 1.0.0
AppPublisher=Winkie Dev
AppPublisherURL=https://github.com/winkiedev
AppSupportURL=https://github.com/winkiedev/pandamessage
AppUpdatesURL=https://github.com/winkiedev/pandamessage
DefaultDirName={autopf}\PandaMessage
DefaultGroupName=PandaMessage
AllowNoIcons=yes
LicenseFile=
InfoBeforeFile=
InfoAfterFile=
OutputDir=installer
OutputBaseFilename=PandaMessage_Setup_v1.0.0
SetupIconFile=assets\icon.ico
Compression=lzma
SolidCompression=yes
WizardStyle=modern
PrivilegesRequired=admin
ArchitecturesInstallIn64BitMode=x64
DisableProgramGroupPage=yes
UninstallDisplayIcon={app}\PandaMessage.exe
UninstallDisplayName=PandaMessage
VersionInfoVersion=1.0.0.0
VersionInfoCompany=Winkie Dev
VersionInfoDescription=Cliente WhatsApp para envío masivo de mensajes
VersionInfoCopyright=Copyright (C) 2025 Winkie Dev

[Languages]
Name: "spanish"; MessagesFile: "compiler:Languages\Spanish.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked
Name: "quicklaunchicon"; Description: "{cm:CreateQuickLaunchIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked; OnlyBelowVersion: 6.1
Name: "startmenu"; Description: "Crear acceso directo en el menú inicio"; GroupDescription: "{cm:AdditionalIcons}"

[Files]
; Archivo ejecutable principal
Source: "dist\PandaMessage\PandaMessage.exe"; DestDir: "{app}"; Flags: ignoreversion
; Carpeta _internal completa con todas las dependencias
Source: "dist\PandaMessage\_internal\*"; DestDir: "{app}\_internal"; Flags: ignoreversion recursesubdirs createallsubdirs
; Archivos de documentación
Source: "readme.md"; DestDir: "{app}"; Flags: ignoreversion; DestName: "Readme.txt"
Source: "requirements.txt"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
; Acceso directo en el menú inicio
Name: "{group}\PandaMessage"; Filename: "{app}\PandaMessage.exe"; WorkingDir: "{app}"; IconFilename: "{app}\PandaMessage.exe"; IconIndex: 0; Tasks: startmenu
; Acceso directo en el escritorio
Name: "{autodesktop}\PandaMessage"; Filename: "{app}\PandaMessage.exe"; WorkingDir: "{app}"; IconFilename: "{app}\PandaMessage.exe"; IconIndex: 0; Tasks: desktopicon
; Acceso directo en la barra de tareas (quick launch)
Name: "{userappdata}\Microsoft\Internet Explorer\Quick Launch\PandaMessage"; Filename: "{app}\PandaMessage.exe"; WorkingDir: "{app}"; IconFilename: "{app}\PandaMessage.exe"; IconIndex: 0; Tasks: quicklaunchicon
; Desinstalador en el menú inicio
Name: "{group}\{cm:UninstallProgram,PandaMessage}"; Filename: "{uninstallexe}"; Tasks: startmenu

[Run]
; Ejecutar la aplicación después de la instalación
Filename: "{app}\PandaMessage.exe"; Description: "{cm:LaunchProgram,PandaMessage}"; Flags: nowait postinstall skipifsilent

[UninstallDelete]
Type: filesandordirs; Name: "{app}\_internal"
Type: files; Name: "{app}\*.log"
Type: files; Name: "{app}\*.tmp"

[Registry]
; Registrar la aplicación en el sistema para que aparezca en "Programas y características"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}"; ValueType: string; ValueName: "DisplayName"; ValueData: "PandaMessage"; Flags: uninsdeletekey
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}"; ValueType: string; ValueName: "DisplayVersion"; ValueData: "1.0.0"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}"; ValueType: string; ValueName: "Publisher"; ValueData: "Winkie Dev"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}"; ValueType: string; ValueName: "InstallLocation"; ValueData: "{app}"
Root: HKLM; Subkey: "Software\Microsoft\Windows\CurrentVersion\Uninstall\{{A7B8C9D0-E1F2-3456-7890-ABCDEF123456}"; ValueType: string; ValueName: "UninstallString"; ValueData: "{uninstallexe}"

[Code]
// Función para verificar si hay una instalación previa
function GetUninstallString(): String;
var
  sUnInstPath: String;
  sUnInstallString: String;
begin
  sUnInstPath := ExpandConstant('Software\Microsoft\Windows\CurrentVersion\Uninstall\{#emit SetupSetting("AppId")}_is1');
  sUnInstallString := '';
  if not RegQueryStringValue(HKLM, sUnInstPath, 'UninstallString', sUnInstallString) then
    RegQueryStringValue(HKCU, sUnInstPath, 'UninstallString', sUnInstallString);
  Result := sUnInstallString;
end;

// Función para desinstalar versión previa
function UnInstallOldVersion(): Integer;
var
  sUnInstallString: String;
  iResultCode: Integer;
begin
  Result := 0;
  sUnInstallString := GetUninstallString();
  if sUnInstallString <> '' then begin
    sUnInstallString := RemoveQuotes(sUnInstallString);
    if Exec(sUnInstallString, '/SILENT /NORESTART /SUPPRESSMSGBOXES','', SW_HIDE, ewWaitUntilTerminated, iResultCode) then
      Result := 3
    else
      Result := 2;
  end else
    Result := 1;
end;

// Verificar versión previa antes de instalar
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if (CurStep=ssInstall) then
  begin
    if (UnInstallOldVersion() = 2) then
    begin
      MsgBox('Error al desinstalar la versión anterior. Por favor, desinstálala manualmente.', mbError, MB_OK);
      Abort;
    end;
  end;
end;
