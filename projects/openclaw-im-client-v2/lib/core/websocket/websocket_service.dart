import 'dart:async';
import 'dart:convert';
import 'package:web_socket_channel/web_socket_channel.dart';
import 'package:logger/logger.dart';

/// WebSocket 消息类型定义
class WebSocketMessage {
  final String type;
  final Map<String, dynamic>? payload;
  final String? sessionId;
  final String? content;

  WebSocketMessage({
    required this.type,
    this.payload,
    this.sessionId,
    this.content,
  });

  Map<String, dynamic> toJson() {
    final map = <String, dynamic>{'type': type};
    if (payload != null) map['payload'] = payload;
    if (sessionId != null) map['sessionId'] = sessionId;
    if (content != null) map['content'] = content;
    return map;
  }

  factory WebSocketMessage.fromJson(Map<String, dynamic> json) {
    return WebSocketMessage(
      type: json['type'] ?? '',
      payload: json['payload'] != null ? Map<String, dynamic>.from(json['payload']) : null,
      sessionId: json['sessionId'],
      content: json['content'],
    );
  }

  @override
  String toString() => 'WebSocketMessage(type: $type, payload: $payload)';
}

/// WebSocket 连接状态
enum ConnectionState {
  disconnected,
  connecting,
  connected,
  reconnecting,
}

/// WebSocket 服务 - 单例模式
class WebSocketService {
  static WebSocketService? _instance;
  static WebSocketService getInstance() => _instance ??= WebSocketService._internal();

  WebSocketService._internal();

  final Logger _logger = Logger();
  WebSocketChannel? _channel;
  StreamSubscription? _connectionSubscription;
  
  // 连接状态
  ConnectionStatus _connectionStatus = ConnectionStatus.disconnected;
  final StreamController<ConnectionStatus> _statusController = StreamController.broadcast();
  
  // 消息流
  final StreamController<WebSocketMessage> _messageController = StreamController.broadcast();
  
  // 重连策略
  int _reconnectAttempts = 0;
  static const int _maxReconnectAttempts = 10;
  static const Duration _initialReconnectDelay = Duration(seconds: 1);
  
  // Gateway 配置
  String? _gatewayUrl;
  String? _token;
  
  // 心跳
  Timer? _heartbeatTimer;
  static const Duration _heartbeatInterval = Duration(seconds: 30);
  
  // SLA 监控
  final WebSocketMonitor _monitor = WebSocketMonitor();

  /// 连接状态流
  Stream<ConnectionStatus> get statusStream => _statusController.stream;
  
  /// 消息流
  Stream<WebSocketMessage> get messageStream => _messageController.stream;
  
  /// 当前连接状态
  ConnectionStatus get connectionStatus => _connectionStatus;
  
  /// 是否已连接
  bool get isConnected => _connectionStatus == ConnectionStatus.connected;

  /// 初始化连接
  Future<void> connect({required String gatewayUrl, required String token}) async {
    if (_connectionStatus == ConnectionStatus.connected) {
      _logger.w('Already connected, ignoring connect request');
      return;
    }

    _gatewayUrl = gatewayUrl;
    _token = token;
    _connectionStatus = ConnectionStatus.connecting;
    _statusController.add(_connectionStatus);

    try {
      _logger.i('Connecting to Gateway: $gatewayUrl');
      
      // 验证 URL 格式
      final uri = Uri.parse(gatewayUrl);
      _logger.d('Parsed URI: scheme=${uri.scheme}, host=${uri.host}, port=${uri.port}, path=${uri.path}');
      
      if (uri.scheme != 'ws' && uri.scheme != 'wss') {
        throw Exception('无效的 WebSocket URL 格式：必须以 ws:// 或 wss:// 开头');
      }
      
      _channel = WebSocketChannel.connect(uri);
      
      // 监听连接
      _connectionSubscription = _channel!.stream.listen(
        (data) => _handleMessage(data),
        onError: (error) {
          _logger.e('WebSocket stream error: $error');
          _handleError(error);
        },
        onDone: () {
          _logger.w('WebSocket stream closed');
          _handleConnectionClosed();
        },
        cancelOnError: true,
      );
      
      // 等待连接建立（增加等待时间）
      await Future.delayed(const Duration(milliseconds: 1000));
      
      // 发送认证
      _logger.d('Sending authentication...');
      await _authenticate(token);
      
      _connectionStatus = ConnectionStatus.connected;
      _statusController.add(_connectionStatus);
      _reconnectAttempts = 0;
      
      _logger.i('Connected to Gateway successfully');
      _monitor.recordConnection(true, Duration.zero);
      
      // 启动心跳
      _startHeartbeat();
      
    } catch (e) {
      _logger.e('Connection failed: $e');
      _connectionStatus = ConnectionStatus.disconnected;
      _statusController.add(_connectionStatus);
      _monitor.recordConnection(false, Duration.zero);
      rethrow;
    }
  }

  /// 认证
  Future<void> _authenticate(String token) async {
    if (_channel == null) return;
    
    final authMessage = WebSocketMessage(
      type: 'auth.token',
      payload: {'token': token},
    );
    
    _sendRaw(jsonEncode(authMessage.toJson()));
    _logger.d('Auth message sent');
  }

  /// 发送消息
  void sendMessage({required String sessionId, required String content}) {
    if (!isConnected) {
      _logger.w('Cannot send message: not connected');
      return;
    }
    
    final message = WebSocketMessage(
      type: 'session.message',
      sessionId: sessionId,
      content: content,
    );
    
    _sendRaw(jsonEncode(message.toJson()));
    _logger.d('Message sent to session $sessionId');
  }

  /// 创建会话
  void createSession({required String agent}) {
    if (!isConnected) {
      _logger.w('Cannot create session: not connected');
      return;
    }
    
    final message = WebSocketMessage(
      type: 'session.create',
      payload: {'agent': agent},
    );
    
    _sendRaw(jsonEncode(message.toJson()));
    _logger.d('Session create request sent for agent: $agent');
  }

  /// 获取 Agent 列表
  void requestNodeList() {
    if (!isConnected) {
      _logger.w('Cannot request node list: not connected');
      return;
    }
    
    final message = WebSocketMessage(type: 'node.list');
    _sendRaw(jsonEncode(message.toJson()));
    _logger.d('Node list requested');
  }

  /// 调用节点能力
  void invokeNode({required String nodeId, required String method, Map<String, dynamic>? params}) {
    if (!isConnected) {
      _logger.w('Cannot invoke node: not connected');
      return;
    }
    
    final message = WebSocketMessage(
      type: 'node.invoke',
      payload: {
        'nodeId': nodeId,
        'method': method,
        if (params != null) 'params': params,
      },
    );
    
    _sendRaw(jsonEncode(message.toJson()));
    _logger.d('Node invoked: $nodeId.$method');
  }

  /// 断开连接
  Future<void> disconnect() async {
    _stopHeartbeat();
    _connectionSubscription?.cancel();
    await _channel?.sink.close();
    _channel = null;
    _connectionStatus = ConnectionStatus.disconnected;
    _statusController.add(_connectionStatus);
    _logger.i('Disconnected from Gateway');
  }

  /// 发送原始数据
  void _sendRaw(String data) {
    _channel?.sink.add(data);
  }

  /// 处理接收消息
  void _handleMessage(dynamic data) {
    try {
      final json = jsonDecode(data as String);
      final message = WebSocketMessage.fromJson(json);
      
      _logger.d('Received: $message');
      _messageController.add(message);
      
      // 处理心跳响应
      if (message.type == 'pong') {
        _logger.d('Heartbeat ACK received');
      }
      
    } catch (e) {
      _logger.e('Failed to parse message: $e');
    }
  }

  /// 处理错误
  void _handleError(dynamic error) {
    _logger.e('WebSocket error: $error');
    _connectionStatus = ConnectionStatus.disconnected;
    _statusController.add(_connectionStatus);
    _attemptReconnect();
  }

  /// 处理连接关闭
  void _handleConnectionClosed() {
    _logger.w('WebSocket connection closed');
    _connectionStatus = ConnectionStatus.disconnected;
    _statusController.add(_connectionStatus);
    _stopHeartbeat();
    _attemptReconnect();
  }

  /// 尝试重连
  Future<void> _attemptReconnect() async {
    if (_reconnectAttempts >= _maxReconnectAttempts) {
      _logger.e('Max reconnect attempts reached, giving up');
      _connectionStatus = ConnectionStatus.disconnected;
      _statusController.add(_connectionStatus);
      return;
    }

    if (_gatewayUrl == null || _token == null) {
      _logger.w('Cannot reconnect: gateway URL or token not set');
      return;
    }

    _connectionStatus = ConnectionStatus.reconnecting;
    _statusController.add(_connectionStatus);
    
    final delay = _calculateReconnectDelay();
    _logger.i('Reconnecting in ${delay.inSeconds}s (attempt ${_reconnectAttempts + 1}/$_maxReconnectAttempts)');
    
    await Future.delayed(delay);
    _reconnectAttempts++;
    
    try {
      await connect(gatewayUrl: _gatewayUrl!, token: _token!);
    } catch (e) {
      _logger.e('Reconnect failed: $e');
      _attemptReconnect();
    }
  }

  /// 计算重连延迟（指数退避 + 抖动）
  Duration _calculateReconnectDelay() {
    final baseDelay = _initialReconnectDelay * (1 << _reconnectAttempts);
    final maxDelay = const Duration(minutes: 5);
    final cappedDelay = baseDelay > maxDelay ? maxDelay : baseDelay;
    
    // 添加 ±20% 抖动
    final jitter = cappedDelay.inMilliseconds * 0.2 * (DateTime.now().millisecond / 500 - 1);
    return cappedDelay + Duration(milliseconds: jitter.toInt().abs());
  }

  /// 启动心跳
  void _startHeartbeat() {
    _stopHeartbeat();
    _heartbeatTimer = Timer.periodic(_heartbeatInterval, (_) {
      if (isConnected) {
        _sendPing();
      }
    });
    _logger.d('Heartbeat started');
  }

  /// 停止心跳
  void _stopHeartbeat() {
    _heartbeatTimer?.cancel();
    _heartbeatTimer = null;
  }

  /// 发送心跳
  void _sendPing() {
    final ping = WebSocketMessage(
      type: 'ping',
      payload: {'timestamp': DateTime.now().millisecondsSinceEpoch},
    );
    _sendRaw(jsonEncode(ping.toJson()));
    _logger.d('Ping sent');
  }

  /// 获取 SLA 报告
  SLAReport getSLAReport() => _monitor.generateReport();

  /// 重置重连计数
  void resetReconnectAttempts() {
    _reconnectAttempts = 0;
  }
}

/// 连接状态枚举
enum ConnectionStatus {
  disconnected,
  connecting,
  connected,
  reconnecting,
}

/// SLA 监控器
class WebSocketMonitor {
  final List<int> _connectionLatencies = [];
  final List<int> _messageLatencies = [];
  final List<int> _reconnectLatencies = [];
  
  int _connectionAttempts = 0;
  int _successfulConnections = 0;
  int _disconnections = 0;
  int _reconnectAttempts = 0;
  int _successfulReconnects = 0;
  double _totalConnectionHours = 0;

  void recordConnection(bool success, Duration latency) {
    _connectionAttempts++;
    if (success) _successfulConnections++;
    _connectionLatencies.add(latency.inMilliseconds);
  }

  void recordMessageLatency(Duration latency) {
    _messageLatencies.add(latency.inMilliseconds);
  }

  void recordDisconnection() {
    _disconnections++;
  }

  void recordReconnect(bool success, Duration latency) {
    _reconnectAttempts++;
    if (success) _successfulReconnects++;
    _reconnectLatencies.add(latency.inMilliseconds);
  }

  SLAReport generateReport() {
    return SLAReport(
      connectionSuccessRate: _connectionAttempts > 0 
          ? _successfulConnections / _connectionAttempts 
          : 1.0,
      messageLatencyP50: _percentile(_messageLatencies, 50),
      messageLatencyP95: _percentile(_messageLatencies, 95),
      messageLatencyP99: _percentile(_messageLatencies, 99),
      disconnectionRate: _totalConnectionHours > 0 
          ? _disconnections / _totalConnectionHours 
          : 0,
      reconnectSuccessRate: _reconnectAttempts > 0 
          ? _successfulReconnects / _reconnectAttempts 
          : 1.0,
      reconnectLatencyP95: _percentile(_reconnectLatencies, 95),
    );
  }

  double _percentile(List<int> values, double percentile) {
    if (values.isEmpty) return 0;
    final sorted = List<int>.from(values)..sort();
    final index = ((percentile / 100) * sorted.length).round();
    return sorted[index < sorted.length ? index : sorted.length - 1].toDouble();
  }
}

/// SLA 报告
class SLAReport {
  final double connectionSuccessRate;
  final double messageLatencyP50;
  final double messageLatencyP95;
  final double messageLatencyP99;
  final double disconnectionRate;
  final double reconnectSuccessRate;
  final double reconnectLatencyP95;

  SLAReport({
    required this.connectionSuccessRate,
    this.messageLatencyP50 = 0,
    this.messageLatencyP95 = 0,
    this.messageLatencyP99 = 0,
    this.disconnectionRate = 0,
    this.reconnectSuccessRate = 1.0,
    this.reconnectLatencyP95 = 0,
  });

  @override
  String toString() {
    return 'SLAReport('
        'connectionSuccessRate: ${(connectionSuccessRate * 100).toStringAsFixed(2)}%, '
        'messageLatencyP99: ${messageLatencyP99.toStringAsFixed(0)}ms, '
        'disconnectionRate: ${disconnectionRate.toStringAsFixed(3)}/h'
        ')';
  }
}
