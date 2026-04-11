# noVNC Assets

此目录用于存放 noVNC 静态资源文件。

## 需要添加的文件

1. 从 https://github.com/novnc/noVNC 下载 release 版本
2. 将以下文件复制到此目录：
   - vnc.html
   - app/
   - core/
   - vendor/

## 集成步骤

1. 下载 noVNC v1.4.0 或更高版本
2. 解压后将文件复制到此目录
3. 在 pubspec.yaml 中确保 assets/noVNC/ 已声明
4. 在 remote_desktop_screen.dart 中修改 WebView 加载路径：
   ```dart
   _controller!.loadFlutterAsset('assets/noVNC/vnc.html');
   ```

## 参考

- noVNC GitHub: https://github.com/novnc/noVNC
- noVNC 官网：https://novnc.com/
