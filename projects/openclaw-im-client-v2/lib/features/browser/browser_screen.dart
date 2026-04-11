import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class BrowserScreen extends StatefulWidget {
  const BrowserScreen({super.key});

  @override
  State<BrowserScreen> createState() => _BrowserScreenState();
}

class _BrowserScreenState extends State<BrowserScreen> {
  late final WebViewController _controller;
  final _urlController = TextEditingController();
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (url) {
            setState(() {
              _isLoading = true;
              _urlController.text = url;
            });
          },
          onPageFinished: (url) {
            setState(() {
              _isLoading = false;
            });
          },
          onWebResourceError: (error) {
            _showError('加载失败：${error.description}');
          },
        ),
      )
      ..loadRequest(Uri.parse('https://www.bing.com'));
  }

  void _navigateToUrl() {
    var url = _urlController.text.trim();
    if (url.isEmpty) return;
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
      url = 'https://$url';
    }
    
    _controller.loadRequest(Uri.parse(url));
    FocusScope.of(context).unfocus();
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message)),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: TextField(
          controller: _urlController,
          decoration: const InputDecoration(
            hintText: '输入网址',
            border: InputBorder.none,
          ),
          onSubmitted: (_) => _navigateToUrl(),
          style: const TextStyle(fontSize: 14),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () => _controller.reload(),
          ),
          IconButton(
            icon: const Icon(Icons.home),
            onPressed: () => _controller.loadRequest(Uri.parse('https://www.bing.com')),
          ),
          PopupMenuButton<String>(
            onSelected: (value) {
              if (value == 'back') {
                _controller.goBack();
              } else if (value == 'forward') {
                _controller.goForward();
              }
            },
            itemBuilder: (context) => [
              const PopupMenuItem(
                value: 'back',
                child: Row(
                  children: [
                    Icon(Icons.arrow_back),
                    SizedBox(width: 8),
                    Text('后退'),
                  ],
                ),
              ),
              const PopupMenuItem(
                value: 'forward',
                child: Row(
                  children: [
                    Icon(Icons.arrow_forward),
                    SizedBox(width: 8),
                    Text('前进'),
                  ],
                ),
              ),
            ],
          ),
        ],
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_isLoading)
            const Positioned(
              top: 0,
              left: 0,
              right: 0,
              child: LinearProgressIndicator(),
            ),
        ],
      ),
    );
  }

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
  }
}
