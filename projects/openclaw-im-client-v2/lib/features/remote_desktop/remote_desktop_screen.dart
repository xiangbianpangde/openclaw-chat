import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

/// 远程桌面屏幕 - noVNC 集成
/// 
/// 注意：完整实现需要将 noVNC 静态资源打包到 assets/noVNC/
/// 并通过 WebView 加载本地 noVNC 页面
class RemoteDesktopScreen extends StatefulWidget {
  const RemoteDesktopScreen({super.key});

  @override
  State<RemoteDesktopScreen> createState() => _RemoteDesktopScreenState();
}

class _RemoteDesktopScreenState extends State<RemoteDesktopScreen> {
  WebViewController? _controller;
  final _vncHostController = TextEditingController();
  final _vncPortController = TextEditingController(text: '5900');
  final _vncPasswordController = TextEditingController();
  
  bool _isConnected = false;
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _initializeWebView();
  }

  void _initializeWebView() {
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (url) {
            setState(() => _isLoading = true);
          },
          onPageFinished: (url) {
            setState(() => _isLoading = false);
          },
          onWebResourceError: (error) {
            _showError('加载失败：${error.description}');
          },
        ),
      );
    
    // 加载 noVNC 页面（本地或远程）
    // TODO: 将 noVNC 打包到 assets 后加载本地页面
    // _controller!.loadFlutterAsset('assets/noVNC/vnc.html');
    
    // 临时使用远程 noVNC 演示
    _controller!.loadRequest(Uri.parse('https://novnc.com/example/'));
  }

  void _connectVNC() {
    final host = _vncHostController.text.trim();
    final port = _vncPortController.text.trim();
    final password = _vncPasswordController.text;

    if (host.isEmpty) {
      _showError('请输入 VNC 服务器地址');
      return;
    }

    // 构建 noVNC URL
    // 格式：vnc.html?host=xxx&port=xxx&password=xxx
    final url = Uri.parse(
      'https://novnc.com/example/vnc.html'
      '?host=$host'
      '&port=$port'
      '&password=$password'
    );

    _controller?.loadRequest(url);
    setState(() => _isConnected = true);
    
    _showSuccess('正在连接 $host:$port');
  }

  void _disconnectVNC() {
    _controller?.loadRequest(Uri.parse('about:blank'));
    setState(() => _isConnected = false);
    _showSuccess('已断开连接');
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  void _showSuccess(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  void _showConnectionDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('VNC 连接'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            TextField(
              controller: _vncHostController,
              decoration: const InputDecoration(
                labelText: 'VNC 服务器地址',
                hintText: '192.168.1.100',
                prefixIcon: Icon(Icons.dns),
              ),
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _vncPortController,
              decoration: const InputDecoration(
                labelText: '端口',
                hintText: '5900',
                prefixIcon: Icon(Icons.numbers),
              ),
              keyboardType: TextInputType.number,
            ),
            const SizedBox(height: 16),
            TextField(
              controller: _vncPasswordController,
              decoration: const InputDecoration(
                labelText: '密码（可选）',
                hintText: 'VNC 密码',
                prefixIcon: Icon(Icons.vpn_key),
              ),
              obscureText: true,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              _connectVNC();
            },
            child: const Text('连接'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('远程桌面'),
        actions: [
          if (!_isConnected)
            IconButton(
              icon: const Icon(Icons.add),
              onPressed: _showConnectionDialog,
            )
          else
            IconButton(
              icon: const Icon(Icons.close),
              onPressed: _disconnectVNC,
            ),
        ],
      ),
      body: Stack(
        children: [
          if (_controller != null) WebViewWidget(controller: _controller!),
          
          if (!_isConnected)
            Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(
                    Icons.desktop_windows,
                    size: 80,
                    color: Colors.grey,
                  ),
                  const SizedBox(height: 16),
                  const Text(
                    '远程桌面',
                    style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold),
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    '点击 + 按钮添加 VNC 连接',
                    style: TextStyle(color: Colors.grey),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton.icon(
                    onPressed: _showConnectionDialog,
                    icon: const Icon(Icons.add),
                    label: const Text('添加连接'),
                  ),
                ],
              ),
            ),
          
          if (_isLoading && _isConnected)
            Positioned.fill(
              child: const Center(
                child: CircularProgressIndicator(),
              ),
            ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _vncHostController.dispose();
    _vncPortController.dispose();
    _vncPasswordController.dispose();
    super.dispose();
  }
}
