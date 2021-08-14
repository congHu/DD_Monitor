# DD监控室

## Cong的Fork
增加了遥控器功能。
- 打开DD监控室程序后后允许windows防火墙。
- 打开设置菜单 -> 遥控器，如果有多个网卡，确保点击与手机连通的局域网地址，生成相应的二维码。
- 经测试，iOS用Safari、微信都正常。用安卓自带浏览器，一些第三方浏览器都有点问题，安卓用微信、手机QQ、QQ浏览器打开正常。
- 安卓一些浏览器有点问题，主要是浏览器拦截了长按事件，弹出了各自的长按菜单。(y1s1有点恶心)
- 任意支持JS的浏览器输入IP:30148也可以打开，理论上都可以正常使用，可能主要还是会遇到长按事件被拦截的情况。
- 主要功能在类`WebRemoteServer`中，在文件`WebRemote.py`中，有flask接口的代码。可以在其他局域网设备用代码请求这些接口。

## 运行指南

确保安装VLC, `HELP.html`内有更多解释。

## 开发指南

推荐在venv/anaconda环境下开发

### 所需包
 - PyQt5

 - requests

 - aiowebsocket

 - python-vlc

 - pyinstaller

 - dnspython    

   

   pip安装

   ```bash
   pip install -r requirements.txt
   ```

   

### 打包

在 `scripts` 文件夹下有各平台的打包脚本，需要在仓库根目录运行。

## TODO

### 全平台
 - [X] 加载热播主播时显示加载状态（在Macos上有明显卡顿）

### Windows平台
 - [ ] ?

### MacOS平台
 - [X] 保证程序打包后附带文件可以被访问
 - [ ] 弹幕窗口在启动后不显示
 - [X] 添加热播主播后Thread卡死
 - [ ] ~~添加主播到播放器后不会继承窗口大小，需要重整layout来激活~~ (VLC bug)

### Linux平台
 - [ ] 弹幕窗口在启动后不显示