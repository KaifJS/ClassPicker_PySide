; installer_zh.iss - 智能抽号系统一键安装脚本 (中文界面)
[Setup]
AppName=智能抽号系统 v3.0 Beta
AppVersion=3.0.1
AppPublisher=开方居士
AppPublisherURL=https://github.com/KaifJS/ClassPicker_PySide
AppSupportURL=https://github.com/KaifJS/ClassPicker_PySide
AppUpdatesURL=https://github.com/KaifJS/ClassPicker_PySide
DefaultDirName={code:GetDefaultDir}
DefaultGroupName=智能抽号系统
UninstallDisplayIcon={app}\智能抽号系统_v3.0_beta.exe
Compression=lzma2
SolidCompression=yes
OutputDir=.
OutputBaseFilename=智能抽号系统_Setup_3.0.1
WizardStyle=modern
PrivilegesRequired=admin
AllowNoIcons=yes

[Languages]
Name: "chinesesimplified"; MessagesFile: "compiler:Languages\ChineseSimplified.isl"

[Files]
; 复制所有文件，但排除 saves 文件夹和 app_settings.json，避免覆盖用户数据
Source: "dist\智能抽号系统_v3.0_beta\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs; Excludes: "saves\*,app_settings.json"

[Icons]
Name: "{userdesktop}\智能抽号系统"; Filename: "{app}\智能抽号系统_v3.0_beta.exe"
Name: "{userstartmenu}\智能抽号系统\智能抽号系统"; Filename: "{app}\智能抽号系统_v3.0_beta.exe"
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