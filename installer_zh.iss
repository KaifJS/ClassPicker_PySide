; installer_zh.iss - 智能抽号系统 v3.0.2 安装脚本（绝对路径图标）
[Setup]
AppName=智能抽号系统 v3.0 Beta
AppVersion=3.0.2
AppPublisher=开方居士
AppPublisherURL=https://github.com/你的用户名/random-draw-pyside6
AppSupportURL=https://github.com/你的用户名/random-draw-pyside6
AppUpdatesURL=https://github.com/你的用户名/random-draw-pyside6
DefaultDirName={code:GetDefaultDir}
DefaultGroupName=智能抽号系统
UninstallDisplayIcon={app}\智能抽号系统_v3.0_beta.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=智能抽号系统_Setup_3.0.2
WizardStyle=modern
PrivilegesRequired=admin
AllowNoIcons=yes
SetupIconFile=C:\Users\ZhuanZ\Desktop\天命pyside6\random_draw_system_pyside6\app_icon.ico

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
Source: "dist\智能抽号系统_v3.0_beta\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "saves\*,app_settings.json"
Source: "C:\Users\ZhuanZ\Desktop\天命pyside6\random_draw_system_pyside6\app_icon.ico"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{userdesktop}\智能抽号系统"; Filename: "{app}\智能抽号系统_v3.0_beta.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{userstartmenu}\智能抽号系统\智能抽号系统"; Filename: "{app}\智能抽号系统_v3.0_beta.exe"; IconFilename: "{app}\app_icon.ico"
Name: "{userstartmenu}\智能抽号系统\卸载"; Filename: "{uninstallexe}"

[Run]
Filename: "{app}\智能抽号系统_v3.0_beta.exe"; Description: "启动智能抽号系统"; Flags: postinstall nowait skipifsilent

[Code]
function GetDefaultDir(Param: string): string;
begin
  if DirExists('D:\') then
    Result := 'D:\智能抽号系统'
  else
    Result := ExpandConstant('{pf}\智能抽号系统');
end;