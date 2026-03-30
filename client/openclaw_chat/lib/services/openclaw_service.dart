import 'dart:convert';
import 'package:http/http.dart' as http;

/// 将 WebSocket URL 转换为 HTTP URL
/// - `ws://` → `http://`
/// - `wss://` → `https://`
String convertWsToHttp(String wsUrl) {
  return wsUrl
      .replaceFirst('ws://', 'http://')
      .replaceFirst('wss://', 'https://');
}

/// OpenClaw API 服务
class OpenClawService {
  String _serverUrl;
  String _agentId;

  OpenClawService({
    required String serverUrl,
    required String agentId,
  })  : _serverUrl = convertWsToHttp(serverUrl),
        _agentId = agentId;

  void updateConfig({String? serverUrl, String? agentId}) {
    if (serverUrl != null) _serverUrl = convertWsToHttp(serverUrl);
    if (agentId != null) _agentId = agentId;
  }

  String get serverUrl => _serverUrl;
  String get agentId => _agentId;

  /// 发送消息给 Agent
  Future<SendMessageResponse> sendMessage({
    required String message,
    String? agentId,
  }) async {
    final targetAgent = agentId ?? _agentId;
    
    // 调用 OpenClaw sessions_send API
    // 注意：这是模拟调用，实际 API 需要根据 OpenClaw 的具体实现调整
    final url = Uri.parse('$_serverUrl/api/send');
    
    try {
      final response = await http.post(
        url,
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'agentId': targetAgent,
          'message': message,
        }),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return SendMessageResponse(
          success: true,
          reply: data['reply'] ?? data['message'] ?? '',
        );
      } else {
        return SendMessageResponse(
          success: false,
          error: 'HTTP ${response.statusCode}: ${response.body}',
        );
      }
    } catch (e) {
      return SendMessageResponse(
        success: false,
        error: '网络错误：$e',
      );
    }
  }

  /// 获取历史消息
  Future<List<Message>> getHistory({
    String? agentId,
    int limit = 50,
  }) async {
    // 调用 OpenClaw sessions_history API
    final targetAgent = agentId ?? _agentId;
    final url = Uri.parse('$_serverUrl/api/history?agentId=$targetAgent&limit=$limit');
    
    try {
      final response = await http.get(url);
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final messages = data['messages'] as List? ?? [];
        return messages.map((m) => Message.fromJson(m)).toList();
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }

  /// 获取 Agent 列表
  Future<List<AgentInfo>> getAgents() async {
    // 返回预设的 Agent 列表
    return [
      AgentInfo(id: 'taizi', name: '太子', description: '皇上代理，消息分拣'),
      AgentInfo(id: 'zhongshu', name: '中书省', description: '起草诏令，研拟方案'),
      AgentInfo(id: 'shangshu', name: '尚书省', description: '执行诏令，工程项目'),
      AgentInfo(id: 'menxia', name: '门下省', description: '审核诏令，封驳审议'),
    ];
  }

  /// 切换 Agent
  void switchAgent(String agentId) {
    _agentId = agentId;
  }

  /// 测试连接
  Future<bool> testConnection() async {
    try {
      final response = await http.get(Uri.parse(_serverUrl)).timeout(
        const Duration(seconds: 5),
      );
      return response.statusCode == 200;
    } catch (e) {
      return false;
    }
  }
}

/// 发送消息响应
class SendMessageResponse {
  final bool success;
  final String reply;
  final String? error;

  SendMessageResponse({
    required this.success,
    this.reply = '',
    this.error,
  });
}

/// 消息模型
class Message {
  final String id;
  final String sender;
  final String content;
  final DateTime timestamp;
  final bool isSelf;

  Message({
    required this.id,
    required this.sender,
    required this.content,
    required this.timestamp,
    this.isSelf = false,
  });

  factory Message.fromJson(Map<String, dynamic> json) {
    return Message(
      id: json['id'] ?? '',
      sender: json['sender'] ?? '',
      content: json['content'] ?? '',
      timestamp: DateTime.tryParse(json['timestamp'] ?? '') ?? DateTime.now(),
      isSelf: json['isSelf'] ?? false,
    );
  }
}

/// Agent 信息
class AgentInfo {
  final String id;
  final String name;
  final String description;

  AgentInfo({
    required this.id,
    required this.name,
    required this.description,
  });
}
