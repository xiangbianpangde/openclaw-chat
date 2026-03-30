import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'home_screen.dart';

/// 登录页面 - 直接集成 OpenClaw API
class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _serverController = TextEditingController();
  final _agentIdController = TextEditingController(text: 'taizi');
  bool _isLoading = false;

  @override
  void initState() {
    super.initState();
    _loadSavedConfig();
  }

  Future<void> _loadSavedConfig() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _serverController.text = prefs.getString('server_url') ?? 'http://38.226.195.166:7891';
    });
  }

  Future<void> _login() async {
    if (_serverController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入服务器地址')),
      );
      return;
    }

    setState(() => _isLoading = true);

    try {
      // 保存配置
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('server_url', _serverController.text);
      await prefs.setString('agent_id', _agentIdController.text);

      // 跳转到主页
      if (mounted) {
        Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => HomeScreen(
              serverUrl: _serverController.text,
              agentId: _agentIdController.text,
            ),
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('登录失败：$e')),
        );
      }
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  void dispose() {
    _serverController.dispose();
    _agentIdController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OpenClaw IM'),
      ),
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                // Logo
                Icon(
                  Icons.chat_bubble_outline,
                  size: 80,
                  color: Theme.of(context).colorScheme.primary,
                ),
                const SizedBox(height: 16),
                Text(
                  'OpenClaw IM',
                  style: Theme.of(context).textTheme.headlineMedium?.copyWith(
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  '直接集成 OpenClaw API',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: Colors.grey,
                  ),
                ),
                const SizedBox(height: 48),

                // 服务器地址
                TextField(
                  controller: _serverController,
                  decoration: const InputDecoration(
                    labelText: 'OpenClaw 服务器地址',
                    prefixIcon: Icon(Icons.dns),
                    border: OutlineInputBorder(),
                    helperText: '例如：http://38.226.195.166:7891',
                  ),
                  keyboardType: TextInputType.url,
                ),
                const SizedBox(height: 16),

                // 选择 Agent
                DropdownButtonFormField<String>(
                  value: _agentIdController.text,
                  decoration: const InputDecoration(
                    labelText: '默认 Agent',
                    prefixIcon: Icon(Icons.rocket),
                    border: OutlineInputBorder(),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'taizi', child: Text('太子 - 消息分拣')),
                    DropdownMenuItem(value: 'zhongshu', child: Text('中书省 - 研拟方案')),
                    DropdownMenuItem(value: 'shangshu', child: Text('尚书省 - 执行工程')),
                    DropdownMenuItem(value: 'menxia', child: Text('门下省 - 审核审议')),
                  ],
                  onChanged: (value) {
                    if (value != null) {
                      setState(() => _agentIdController.text = value);
                    }
                  },
                ),
                const SizedBox(height: 24),

                // 登录按钮
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: FilledButton(
                    onPressed: _isLoading ? null : _login,
                    child: _isLoading
                        ? const CircularProgressIndicator()
                        : const Text('进入应用', style: TextStyle(fontSize: 16)),
                  ),
                ),
                const SizedBox(height: 16),

                // 说明
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          '💡 使用说明',
                          style: Theme.of(context).textTheme.titleSmall,
                        ),
                        const SizedBox(height: 8),
                        const Text(
                          '1. 输入 OpenClaw 服务器地址\n'
                          '2. 选择默认 Agent\n'
                          '3. 点击"进入应用"\n'
                          '4. 在聊天页面与 Agent 对话\n'
                          '5. 可随时切换 Agent',
                        ),
                      ],
                    ),
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
