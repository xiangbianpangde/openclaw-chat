import 'package:flutter/material.dart';
import '../services/openim_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _serverController = TextEditingController(text: 'http://38.226.195.166:10002');
  final _userIdController = TextEditingController();
  final _secretController = TextEditingController();
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void dispose() {
    _serverController.dispose();
    _userIdController.dispose();
    _secretController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    final result = await OpenIMService.loginWithCredentials(
      _serverController.text.trim(),
      _userIdController.text.trim(),
      _secretController.text.trim(),
    );

    setState(() {
      _isLoading = false;
    });

    if (result['success'] == true) {
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(builder: (_) => const Scaffold(body: Text('Chat'))),
        );
      }
    } else {
      setState(() {
        _errorMessage = result['error'] ?? '登录失败';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(24.0),
      child: Form(
        key: _formKey,
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.chat, size: 80, color: Colors.blue),
            const SizedBox(height: 32),
            const Text(
              'OpenClaw Chat',
              style: TextStyle(fontSize: 28, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 8),
            const Text(
              '基于 OpenIM 的专用聊天客户端',
              style: TextStyle(color: Colors.grey),
            ),
            const SizedBox(height: 48),
            TextFormField(
              controller: _serverController,
              decoration: const InputDecoration(
                labelText: '服务器地址',
                prefixIcon: Icon(Icons.dns),
                border: OutlineInputBorder(),
              ),
              validator: (v) => v!.isEmpty ? '请输入服务器地址' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _userIdController,
              decoration: const InputDecoration(
                labelText: '用户 ID',
                prefixIcon: Icon(Icons.person),
                border: OutlineInputBorder(),
              ),
              validator: (v) => v!.isEmpty ? '请输入用户 ID' : null,
            ),
            const SizedBox(height: 16),
            TextFormField(
              controller: _secretController,
              obscureText: true,
              decoration: const InputDecoration(
                labelText: '密码',
                prefixIcon: Icon(Icons.lock),
                border: OutlineInputBorder(),
              ),
              validator: (v) => v!.isEmpty ? '请输入密码' : null,
            ),
            if (_errorMessage != null) ...[
              const SizedBox(height: 16),
              Text(
                _errorMessage!,
                style: const TextStyle(color: Colors.red),
              ),
            ],
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton(
                onPressed: _isLoading ? null : _login,
                child: _isLoading
                    ? const CircularProgressIndicator()
                    : const Text('登录', style: TextStyle(fontSize: 16)),
              ),
            ),
            const SizedBox(height: 16),
            TextButton(
              onPressed: () => _showHelp(),
              child: const Text('如何获取账号？'),
            ),
          ],
        ),
      ),
    );
  }

  void _showHelp() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('获取账号'),
        content: const Text(
          '1. 联系管理员创建账号\n\n'
          '2. 或使用 OpenIM Web 管理后台:\n'
          '   http://服务器 IP:11001\n\n'
          '3. 默认管理员:\n'
          '   用户：admin\n'
          '   密码：openIM123',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('知道了'),
          ),
        ],
      ),
    );
  }
}
