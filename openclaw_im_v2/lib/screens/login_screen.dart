import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
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
  final _tokenController = TextEditingController();
  bool _isLoading = false;
  bool _saveToken = true;
  String? _connectionError;

  @override
  void initState() {
    super.initState();
    _loadSavedConfig();
  }

  Future<void> _loadSavedConfig() async {
    final prefs = await SharedPreferences.getInstance();
    setState(() {
      _serverController.text = prefs.getString('server_url') ?? 'http://38.226.195.166:7891';
      _tokenController.text = prefs.getString('auth_token') ?? '';
      _agentIdController.text = prefs.getString('agent_id') ?? 'taizi';
    });
  }

  /// 将 WebSocket URL 转换为 HTTP URL
  String _convertWsToHttp(String wsUrl) {
    return wsUrl
        .replaceFirst('ws://', 'http://')
        .replaceFirst('wss://', 'https://');
  }

  /// 测试服务器连接
  Future<bool> _testConnection(String serverUrl) async {
    try {
      // 转换协议：ws:// → http://, wss:// → https://
      final httpUrl = _convertWsToHttp(serverUrl);
      print('[LoginScreen] 测试连接：$serverUrl → $httpUrl');
      
      // 测试 HTTP 连接
      final url = Uri.parse('$httpUrl/api/history?agentId=taizi&limit=1');
      final headers = <String, String>{};
      if (_tokenController.text.isNotEmpty) {
        headers['Authorization'] = 'Bearer ${_tokenController.text}';
      }
      
      final response = await http.get(url, headers: headers).timeout(
        const Duration(seconds: 5),
        onTimeout: () {
          print('[LoginScreen] 连接超时（5 秒）');
          return http.Response('{"error": "timeout"}', 408);
        },
      );
      
      print('[LoginScreen] 连接测试响应：${response.statusCode}');
      
      if (response.statusCode == 200 || response.statusCode == 401) {
        // 200 = 成功，401 = 需要认证（但服务器可达）
        return true;
      } else {
        _connectionError = '服务器响应异常：HTTP ${response.statusCode}';
        return false;
      }
    } catch (e) {
      print('[LoginScreen] 连接测试失败：$e');
      _connectionError = '无法连接到服务器：$e\n\n请检查：\n1. 服务器地址是否正确\n2. 是否需要添加端口号（如 :7891）\n3. 网络连接是否正常';
      return false;
    }
  }

  Future<void> _login() async {
    // 调试日志：登录按钮被点击
    print('[LoginScreen] 登录按钮被点击');
    print('[LoginScreen] 服务器地址：${_serverController.text}');
    print('[LoginScreen] Agent ID: ${_agentIdController.text}');
    print('[LoginScreen] Token: ${_tokenController.text.isEmpty ? "(空)" : "***"}');

    if (_serverController.text.isEmpty) {
      print('[LoginScreen] 验证失败：服务器地址为空');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请输入服务器地址')),
      );
      return;
    }

    if (_agentIdController.text.isEmpty) {
      print('[LoginScreen] 验证失败：Agent ID 为空');
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('请选择 Agent')),
      );
      return;
    }

    print('[LoginScreen] 验证通过，开始设置加载状态...');
    setState(() {
      _isLoading = true;
      _connectionError = null;
    });
    print('[LoginScreen] 加载状态已设置');

    try {
      // 先测试连接
      print('[LoginScreen] 正在测试服务器连接...');
      final connected = await _testConnection(_serverController.text);
      
      if (!connected) {
        print('[LoginScreen] 连接测试失败：$_connectionError');
        if (mounted) {
          setState(() => _isLoading = false);
          showDialog(
            context: context,
            builder: (context) => AlertDialog(
              title: const Text('连接失败'),
              content: SingleChildScrollView(
                child: SelectableText(
                  _connectionError ?? '未知错误',
                  style: const TextStyle(fontSize: 14),
                ),
              ),
              actions: [
                TextButton(
                  onPressed: () => Navigator.pop(context),
                  child: const Text('确定'),
                ),
              ],
            ),
          );
        }
        return;
      }
      
      print('[LoginScreen] 连接测试成功');

      // 保存配置
      print('[LoginScreen] 正在保存配置...');
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString('server_url', _serverController.text);
      await prefs.setString('agent_id', _agentIdController.text);
      if (_saveToken && _tokenController.text.isNotEmpty) {
        await prefs.setString('auth_token', _tokenController.text);
      }
      print('[LoginScreen] 配置保存成功');

      // 跳转到主页
      if (mounted) {
        print('[LoginScreen] 开始页面跳转...');
        await Navigator.of(context).pushReplacement(
          MaterialPageRoute(
            builder: (_) => HomeScreen(
              serverUrl: _serverController.text,
              agentId: _agentIdController.text,
              authToken: _tokenController.text,
            ),
          ),
        );
        print('[LoginScreen] 页面跳转完成');
      } else {
        print('[LoginScreen] 警告：widget 已卸载，无法跳转');
      }
    } catch (e, stackTrace) {
      print('[LoginScreen] 登录失败：$e');
      print('[LoginScreen] 堆栈跟踪：$stackTrace');
      if (mounted) {
        setState(() => _isLoading = false);
        showDialog(
          context: context,
          builder: (context) => AlertDialog(
            title: const Text('登录失败'),
            content: SingleChildScrollView(
              child: SelectableText(
                '错误详情：\n$e\n\n堆栈：\n$stackTrace',
                style: const TextStyle(fontSize: 12),
              ),
            ),
            actions: [
              TextButton(
                onPressed: () => Navigator.pop(context),
                child: const Text('确定'),
              ),
            ],
          ),
        );
      }
    } finally {
      print('[LoginScreen] 重置加载状态');
      if (mounted && !_isLoading) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  void dispose() {
    _serverController.dispose();
    _agentIdController.dispose();
    _tokenController.dispose();
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
                    helperText: '格式：http://地址：端口 或 https://地址：端口',
                    hintText: '例如：http://38.226.195.166:7891',
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
                const SizedBox(height: 16),

                // Token 输入框（可选）
                TextField(
                  controller: _tokenController,
                  decoration: InputDecoration(
                    labelText: '认证 Token（可选）',
                    prefixIcon: const Icon(Icons.vpn_key),
                    border: const OutlineInputBorder(),
                    helperText: '用于身份验证，支持复制粘贴',
                    suffixIcon: _tokenController.text.isNotEmpty
                        ? IconButton(
                            icon: const Icon(Icons.clear),
                            onPressed: () => _tokenController.clear(),
                          )
                        : IconButton(
                            icon: const Icon(Icons.content_paste),
                            onPressed: () async {
                              // 从剪贴板粘贴
                              // Flutter 默认支持长按粘贴，此按钮为快捷操作
                            },
                          ),
                  ),
                  obscureText: true,
                  enableSuggestions: false,
                  autocorrect: false,
                ),
                const SizedBox(height: 16),

                // 保存 Token 选项
                Row(
                  children: [
                    Checkbox(
                      value: _saveToken,
                      onChanged: (value) {
                        setState(() => _saveToken = value ?? true);
                      },
                    ),
                    const Text('记住 Token（自动登录）'),
                  ],
                ),
                const SizedBox(height: 8),

                // 登录按钮
                SizedBox(
                  width: double.infinity,
                  height: 48,
                  child: FilledButton(
                    onPressed: _isLoading ? null : _login,
                    child: _isLoading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              strokeWidth: 2,
                              valueColor: AlwaysStoppedAnimation<Color>(Colors.white),
                            ),
                          )
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
                          '1. 输入 OpenClaw 服务器地址（必须包含端口号，如 :7891）\n'
                          '2. 选择默认 Agent\n'
                          '3. 输入认证 Token（可选，用于身份验证）\n'
                          '4. 勾选"记住 Token"可自动登录\n'
                          '5. 点击"进入应用"（会先测试连接，约 5 秒）\n'
                          '6. 在聊天页面与 Agent 对话\n'
                          '7. 可随时切换 Agent\n\n'
                          '⚠️ 如连接失败，请检查：\n'
                          '- 地址格式是否正确（http://IP:端口）\n'
                          '- 服务器是否正常运行\n'
                          '- 网络连接是否通畅',
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
