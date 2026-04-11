import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';

/// OpenClaw Gateway WebSocket 服务
class OpenClawGatewayService {
  String _serverUrl;
  String _authToken;
  String _agentId;
  WebSocketChannel? _channel;
  bool _isConnected = false;
  String? _sessionId;
  
  // 事件回调
  Function(String)? onMessageReceived;
  Function(String)? onError;
  Function()? onConnected;
  Function()? onDisconnected;

  OpenClawGatewayService({
    required String serverUrl,
    String authToken = '',
    String agentId = 'taizi',
  })  : _serverUrl = serverUrl,
        _authToken = authToken,
        _agentId = agentId;

  /// 连接到 Gateway
  Future<bool> connect() async {
    try {
      // 将 HTTP URL 转换为 WebSocket URL
      String wsUrl = _serverUrl
          .replaceAll('http://', 'ws://')
          .replaceAll('https://', 'wss://');
      
      // 如果没有指定端口，使用默认 Gateway 端口 18789
      if (!wsUrl.contains(':')) {
        wsUrl = '$wsUrl:18789';
      }
      
      print('[WebSocket] 开始连接：$wsUrl');
      print('[WebSocket] 原始服务器地址：$_serverUrl');
      
      _channel = WebSocketChannel.connect(Uri.parse(wsUrl));
      
      // 连接完成标志
      bool connectionCompleted = false;
      
      // 监听消息
      _channel!.stream.listen(
        (message) {
          print('[WebSocket] 收到原始消息：$message');
          _handleMessage(message);
        },
        onError: (error) {
          print('[WebSocket] 连接错误：$error');
          _isConnected = false;
          if (!connectionCompleted) {
            onError?.call('WebSocket 连接失败：$error\n\n请检查：\n1. 服务器地址是否正确\n2. WebSocket 端口是否开放（默认 18789）\n3. 防火墙是否阻止连接');
          } else {
            onDisconnected?.call();
          }
        },
        onDone: () {
          print('[WebSocket] 连接关闭');
          _isConnected = false;
          _channel = null;
          if (!connectionCompleted) {
            onError?.call('WebSocket 连接已关闭');
          } else {
            onDisconnected?.call();
          }
        },
      );
      
      // 等待连接建立（增加到 5 秒）
      print('[WebSocket] 等待连接建立（最多 5 秒）...');
      await Future.delayed(const Duration(seconds: 5));
      
      // 发送 connect 请求
      print('[WebSocket] 发送 connect 请求...');
      await _sendConnectRequest();
      
      // 再等待 2 秒接收连接响应
      await Future.delayed(const Duration(seconds: 2));
      
      if (_isConnected) {
        print('[WebSocket] 连接成功！');
        connectionCompleted = true;
        return true;
      } else {
        print('[WebSocket] 连接超时：未收到 Gateway 响应');
        onError?.call('连接超时：服务器未在 7 秒内响应\n\n请检查：\n1. 服务器是否运行 OpenClaw Gateway\n2. WebSocket 端口是否正确（默认 18789）\n3. 地址格式：http://IP:端口');
        return false;
      }
    } catch (e, stackTrace) {
      print('[WebSocket] 连接异常：$e');
      print('[WebSocket] 堆栈：$stackTrace');
      onError?.call('连接失败：$e\n\n堆栈：\n$stackTrace');
      return false;
    }
  }

  /// 发送 connect 请求（Gateway 协议要求的第一帧）
  Future<void> _sendConnectRequest() async {
    final connectMessage = {
      'type': 'req',
      'id': _generateId(),
      'method': 'connect',
      'params': {
        'minProtocol': '1.0',
        'maxProtocol': '2.0',
        'client': {
          'id': 'openclaw-im-mobile',
          'displayName': 'OpenClaw IM Mobile',
          'version': '4.0.0',
          'platform': 'android',
          'mode': 'chat',
          'instanceId': DateTime.now().millisecondsSinceEpoch.toString(),
        },
        'caps': {
          'supportsPresence': true,
          'supportsAgent': true,
        },
        if (_authToken.isNotEmpty)
          'auth': {
            'token': _authToken,
          },
        'locale': 'zh-CN',
      },
    };
    
    _sendRawMessage(connectMessage);
  }

  /// 发送消息给 Agent
  Future<void> sendMessage(String message) async {
    if (!_isConnected) {
      onError?.call('未连接到 Gateway');
      return;
    }
    
    final agentMessage = {
      'type': 'req',
      'id': _generateId(),
      'method': 'agent',
      'params': {
        'agentId': _agentId,
        'prompt': message,
        'waitForCompletion': true,
      },
    };
    
    _sendRawMessage(agentMessage);
  }

  /// 切换 Agent
  void switchAgent(String agentId) {
    _agentId = agentId;
  }

  /// 发送原始消息
  void _sendRawMessage(Map<String, dynamic> message) {
    if (_channel != null) {
      _channel!.sink.add(jsonEncode(message));
    }
  }

  /// 处理接收到的消息
  void _handleMessage(dynamic message) {
    try {
      final data = jsonDecode(message as String);
      final type = data['type'] as String?;
      
      print('收到消息：$data');
      
      if (type == 'res') {
        // 响应消息
        final method = data['method'] as String?;
        final ok = data['ok'] as bool?;
        final payload = data['payload'];
        
        if (method == 'connect' && ok == true) {
          // 连接成功
          _isConnected = true;
          print('Gateway 连接成功！');
          onConnected?.call();
          
          // 保存会话 ID
          _sessionId = payload?['sessionId'] as String?;
        } else if (method == 'agent' && ok == true) {
          // Agent 响应
          final reply = payload?['reply'] as String? ?? payload?['text'] as String? ?? '';
          if (reply.isNotEmpty) {
            onMessageReceived?.call(reply);
          }
        } else if (ok == false) {
          // 错误响应
          final error = data['error'];
          onError?.call('错误：${error?['message'] ?? '未知错误'}');
        }
      } else if (type == 'event') {
        // 事件消息
        final event = data['event'] as String?;
        final payload = data['payload'];
        
        if (event == 'agent') {
          // Agent 流式事件
          final text = payload?['text'] as String? ?? '';
          if (text.isNotEmpty) {
            onMessageReceived?.call(text);
          }
        } else if (event == 'presence') {
          // Presence 更新
          print('Presence 更新：$payload');
        } else if (event == 'tick') {
          // 心跳
          print('收到心跳');
        }
      }
    } catch (e) {
      print('处理消息失败：$e');
    }
  }

  /// 生成唯一 ID
  String _generateId() {
    return '${DateTime.now().millisecondsSinceEpoch}_${(DateTime.now().microsecondsSinceEpoch % 10000).toString().padLeft(4, '0')}';
  }

  /// 断开连接
  void disconnect() {
    _channel?.sink.close();
    _channel = null;
    _isConnected = false;
    _sessionId = null;
  }

  /// 更新配置
  void updateConfig({String? serverUrl, String? authToken, String? agentId}) {
    if (serverUrl != null) _serverUrl = serverUrl;
    if (authToken != null) _authToken = authToken;
    if (agentId != null) _agentId = agentId;
  }

  bool get isConnected => _isConnected;
  String get agentId => _agentId;
}
