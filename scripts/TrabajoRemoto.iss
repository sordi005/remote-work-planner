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
; Firma opcional: usa variables de entorno si existen, si no, omite firma
#define SignPfx GetEnv("SIGN_PFX_PATH")
#define SignPfxPass GetEnv("SIGN_PFX_PASS")
#define SignTsEnv GetEnv("SIGN_TIMESTAMP_URL")
#if SignTsEnv == ""
  #define SignTs "http://timestamp.digicert.com"
#else
  #define SignTs SignTsEnv
#endif
#if (SignPfx != "") && (SignPfxPass != "")
SignTool=signtool sign /fd SHA256 /tr $q{#SignTs}$q /td SHA256 /f $q{#SignPfx}$q /p $q{#SignPfxPass}$q $f
#endif

[Files]
; Modo onedir: empaqueta la carpeta completa generada por PyInstaller
Source: "..\dist\TrabajoRemoto\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\Trabajo Remoto"; Filename: "{app}\TrabajoRemoto.exe"
Name: "{userdesktop}\Trabajo Remoto"; Filename: "{app}\TrabajoRemoto.exe"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "Crear acceso directo en el Escritorio"; Flags: unchecked