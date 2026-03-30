import 'package:flutter/material.dart';

/// 浏览器页面 - 内置网页浏览功能
class BrowserScreen extends StatefulWidget {
  const BrowserScreen({super.key});

  @override
  State<BrowserScreen> createState() => _BrowserScreenState();
}

class _BrowserScreenState extends State<BrowserScreen> {
  final _urlController = TextEditingController(text: 'https://www.google.com');
  String _currentUrl = 'https://www.google.com';
  bool _isLoading = false;

  @override
  void dispose() {
    _urlController.dispose();
    super.dispose();
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
          onSubmitted: (_) => _navigate(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _navigate,
          ),
        ],
      ),
      body: Center(
        child: _isLoading
            ? const CircularProgressIndicator()
            : Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.language,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '浏览器功能开发中',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '将集成 WebView 支持',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                  const SizedBox(height: 24),
                  ElevatedButton(
                    onPressed: () {
                      setState(() {
                        _currentUrl = _urlController.text;
                        _isLoading = true;
                      });
                      // 模拟加载
                      Future.delayed(const Duration(seconds: 2), () {
                        if (mounted) {
                          setState(() => _isLoading = false);
                        }
                      });
                    },
                    child: const Text('访问'),
                  ),
                ],
              ),
      ),
    );
  }

  void _navigate() {
    setState(() {
      _currentUrl = _urlController.text;
      _isLoading = true;
    });
    // 模拟加载
    Future.delayed(const Duration(seconds: 2), () {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    });
  }
}
