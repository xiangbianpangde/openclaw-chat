import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';

import 'auth_bloc.dart';
import '../../../core/storage/storage_service.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final Logger _logger = Logger();
  final _storage = StorageService.getInstance();
  
  final _gatewayController = TextEditingController();
  final _tokenController = TextEditingController();
  final _formKey = GlobalKey<FormState>();
  
  bool _obscureToken = true;
  bool _autoLogin = false;

  @override
  void initState() {
    super.initState();
    _loadSavedConfig();
  }

  Future<void> _loadSavedConfig() async {
    final savedGateway = _storage.getGatewayUrl();
    final savedToken = await _storage.getToken();
    final savedAutoLogin = _storage.getAutoLogin();
    
    if (mounted) {
      setState(() {
        _gatewayController.text = savedGateway ?? 'ws://YOUR_SERVER_IP/ws';
        _autoLogin = savedAutoLogin;
      });
      
      // 如果有保存的 Token 且启用自动登录，自动登录
      if (savedToken != null && savedAutoLogin) {
        _tokenController.text = savedToken;
        _autoLogin = true;
        WidgetsBinding.instance.addPostFrameCallback((_) {
          _performLogin(savedToken);
        });
      }
    }
  }

  void _performLogin(String token) {
    _logger.d('Login button pressed, validating form...');
    
    if (_formKey.currentState!.validate()) {
      final gatewayUrl = _gatewayController.text.trim();
      
      _logger.i('Form validated, initiating login with gateway: $gatewayUrl');
      
      context.read<AuthBloc>().add(ConfigureGateway(gatewayUrl: gatewayUrl));
      context.read<AuthBloc>().add(LoginWithToken(token: token));
      
      _logger.i('Login events dispatched to AuthBloc');
    } else {
      _logger.w('Form validation failed - check Gateway URL and Token fields');
      
      // 显示表单验证错误提示
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: const Text('请检查输入：Gateway 地址和 Token 不能为空'),
          backgroundColor: Colors.orange,
          duration: const Duration(seconds: 3),
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Center(
          child: SingleChildScrollView(
            padding: const EdgeInsets.all(24.0),
            child: Form(
              key: _formKey,
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  // Logo
                  const Icon(
                    Icons.chat_bubble_outline,
                    size: 80,
                    color: Colors.blue,
                  ),
                  const SizedBox(height: 16),
                  
                  // Title
                  const Text(
                    'OpenClaw IM',
                    style: TextStyle(
                      fontSize: 32,
                      fontWeight: FontWeight.bold,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 8),
                  const Text(
                    'v2.0',
                    style: TextStyle(
                      fontSize: 16,
                      color: Colors.grey,
                    ),
                    textAlign: TextAlign.center,
                  ),
                  const SizedBox(height: 48),
                  
                  // Gateway URL
                  TextFormField(
                    controller: _gatewayController,
                    decoration: const InputDecoration(
                      labelText: 'Gateway 地址',
                      hintText: 'ws://YOUR_SERVER_IP/ws (通过 Nginx 代理)',
                      prefixIcon: Icon(Icons.dns),
                      border: OutlineInputBorder(),
                    ),
                    keyboardType: TextInputType.url,
                    validator: (value) {
                      if (value == null || value.trim().isEmpty) {
                        return '请输入 Gateway 地址';
                      }
                      if (!value.trim().startsWith('ws://') && 
                          !value.trim().startsWith('wss://')) {
                        return '地址必须以 ws:// 或 wss:// 开头';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  // Token
                  TextFormField(
                    controller: _tokenController,
                    decoration: InputDecoration(
                      labelText: 'Token',
                      hintText: '请输入认证 Token',
                      prefixIcon: const Icon(Icons.vpn_key),
                      border: const OutlineInputBorder(),
                      suffixIcon: IconButton(
                        icon: Icon(
                          _obscureToken ? Icons.visibility : Icons.visibility_off,
                        ),
                        onPressed: () {
                          setState(() {
                            _obscureToken = !_obscureToken;
                          });
                        },
                      ),
                    ),
                    obscureText: _obscureToken,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return '请输入 Token';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  // Auto login
                  Row(
                    children: [
                      Checkbox(
                        value: _autoLogin,
                        onChanged: (value) {
                          setState(() {
                            _autoLogin = value ?? false;
                          });
                          _storage.setAutoLogin(_autoLogin);
                        },
                      ),
                      const Text('自动登录'),
                    ],
                  ),
                  const SizedBox(height: 24),
                  
                  // Login button
                  BlocBuilder<AuthBloc, AuthState>(
                    builder: (context, state) {
                      final isLoading = state is AuthLoading;
                      
                      return ElevatedButton(
                        onPressed: isLoading ? null : () => _performLogin(_tokenController.text),
                        style: ElevatedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(
                            borderRadius: BorderRadius.circular(8),
                          ),
                        ),
                        child: isLoading
                            ? const SizedBox(
                                height: 20,
                                width: 20,
                                child: CircularProgressIndicator(strokeWidth: 2),
                              )
                            : const Text(
                                '登录',
                                style: TextStyle(fontSize: 16),
                              ),
                      );
                    },
                  ),
                  const SizedBox(height: 16),
                  
                  // Error message
                  BlocBuilder<AuthBloc, AuthState>(
                    builder: (context, state) {
                      if (state is AuthUnauthenticated && state.errorMessage != null) {
                        return Padding(
                          padding: const EdgeInsets.only(top: 16),
                          child: Text(
                            state.errorMessage!,
                            style: const TextStyle(color: Colors.red),
                            textAlign: TextAlign.center,
                          ),
                        );
                      }
                      return const SizedBox.shrink();
                    },
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  @override
  void dispose() {
    _gatewayController.dispose();
    _tokenController.dispose();
    super.dispose();
  }
}
