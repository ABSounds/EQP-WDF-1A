#define MyAppName "EQP-WDF-1A"
#define MyAppVersion "0.1.10"
#define MyAppPublisher "ABSounds"
#define MyAppURL "https://github.com/ABSounds/EQP-WDF-1A"

[Setup]
AppId={{41A511BE-16A4-4B8E-8B09-AD85D13C98A7}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
VersionInfoVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppPublisherURL={#MyAppURL}
AppSupportURL={#MyAppURL}
AppUpdatesURL={#MyAppURL}
CreateAppDir=no
DefaultGroupName={#MyAppPublisher}
OutputBaseFilename={#MyAppName}_v{#MyAppVersion}_setup
Compression=lzma
SolidCompression=yes
ArchitecturesInstallIn64BitMode=x64
UninstallFilesDir={app}\Uninstall
WizardImageStretch=False

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "..\Builds\VisualStudio2022\x64\Release\VST3\{#MyAppName}.vst3\Contents\Resources\moduleinfo.json"; DestDir: "{commoncf}\VST3\{#MyAppPublisher}\{#MyAppName}.vst3\Contents\Resources"; Flags: ignoreversion;
Source: "..\Builds\VisualStudio2022\x64\Release\VST3\{#MyAppName}.vst3\Contents\x86_64-win\{#MyAppName}.vst3"; DestDir: "{commoncf}\VST3\{#MyAppPublisher}\{#MyAppName}.vst3\Contents\x86_64-win"; Flags: ignoreversion;

[Icons]
Name: "{group}\{cm:UninstallProgram,{#MyAppName}}"; Filename: "{uninstallexe}"

[Components]
Name: "VST3"; Description: "VST3 plugin"; Types: VST3; Flags: fixed

[Types]
Name: "VST3"; Description: "VST3 plugin"
