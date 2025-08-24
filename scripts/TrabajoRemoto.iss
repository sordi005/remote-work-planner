[Setup]
AppName= Registro Trabajo Remoto
AppVersion=1.0.0
AppPublisher=SordiCompany
AppId={{2A34B3E8-5E40-4F4D-9F2E-3C9E9B50C7E2}}
DefaultDirName={pf}\TrabajoRemoto
DefaultGroupName=Trabajo Remoto
OutputDir=..\dist
OutputBaseFilename=TrabajoRemoto-Setup
Compression=lzma2
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
PrivilegesRequired=admin
UninstallDisplayIcon={app}\TrabajoRemoto.exe
SetupIconFile=..\ui\resources\app.ico
SignTool=signtool sign /fd SHA256 /tr $q{#GetEnv('SIGN_TIMESTAMP_URL')|http://timestamp.digicert.com}$q /td SHA256 /f $q{#GetEnv('SIGN_PFX_PATH')}$q /p $q{#GetEnv('SIGN_PFX_PASS')}$q $f

[Files]
Source: "..\dist\TrabajoRemoto.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Trabajo Remoto"; Filename: "{app}\TrabajoRemoto.exe"
Name: "{userdesktop}\Trabajo Remoto"; Filename: "{app}\TrabajoRemoto.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; Flags: unchecked