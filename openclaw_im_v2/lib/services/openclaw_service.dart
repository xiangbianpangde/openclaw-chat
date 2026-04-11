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
  String _authToken;

  OpenClawService({
    required String serverUrl,
    required String agentId,
    String authToken = '',
  })  : _serverUrl = convertWsToHttp(serverUrl),
        _agentId = agentId,
        _authToken = authToken;

  void updateConfig({String? serverUrl, String? agentId, String? authToken}) {
    if (serverUrl != null) _serverUrl = convertWsToHttp(serverUrl);
    if (agentId != null) _agentId = agentId;
    if (authToken != null) _authToken = authToken;
  }

  String get serverUrl => _serverUrl;
  String get agentId => _agentId;
  String get authToken => _authToken;

  /// 发送消息给 Agent
  Future<SendMessageResponse> sendMessage({
    required String message,
    String? agentId,
  }) async {
    final targetAgent = agentId ?? _agentId;
    
    // 调用 OpenClaw sessions_send API
    final url = Uri.parse('$_serverUrl/api/send');
    
    print('[OpenClawService] 发送消息到：$url');
    print('[OpenClawService] Agent: $targetAgent, Token: ${_authToken.isEmpty ? "(无)" : "***"}');
    
    try {
      final headers = <String, String>{'Content-Type': 'application/json'};
      if (_authToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $_authToken';
      }
      
      final requestBody = jsonEncode({
        'agentId': targetAgent,
        'message': message,
      });
      print('[OpenClawService] 请求体：$requestBody');
      
      final response = await http.post(
        url,
        headers: headers,
        body: requestBody,
      ).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          print('[OpenClawService] 请求超时（30 秒）');
          return http.Response('{"error": "timeout"}', 408);
        },
      );

      print('[OpenClawService] 响应状态码：${response.statusCode}');
      print('[OpenClawService] 响应体：${response.body}');

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final reply = data['reply'] ?? data['message'] ?? '';
        print('[OpenClawService] 回复：${reply.substring(0, 50)}...');
        return SendMessageResponse(
          success: true,
          reply: reply,
        );
      } else {
        return SendMessageResponse(
          success: false,
          error: 'HTTP ${response.statusCode}: ${response.body}',
        );
      }
    } catch (e) {
      print('[OpenClawService] 网络错误：$e');
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
    
    print('[OpenClawService] 获取历史消息：$url');
    
    try {
      final headers = <String, String>{};
      if (_authToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $_authToken';
      }
      
      final response = await http.get(url, headers: headers).timeout(
        const Duration(seconds: 30),
        onTimeout: () {
          print('[OpenClawService] 获取历史消息超时（30 秒）');
          return http.Response('{"error": "timeout"}', 408);
        },
      );
      
      print('[OpenClawService] 历史消息响应状态码：${response.statusCode}');
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final messages = data['messages'] as List? ?? [];
        print('[OpenClawService] 获取到 ${messages.length} 条历史消息');
        return messages.map((m) => Message.fromJson(m)).toList();
      } else {
        print('[OpenClawService] 获取历史消息失败：HTTP ${response.statusCode}');
        return [];
      }
    } catch (e) {
      print('[OpenClawService] 获取历史消息异常：$e');
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
    print('[OpenClawService] 测试连接：$_serverUrl');
    try {
      // 测试 API 端点连接
      final url = Uri.parse('$_serverUrl/api/history?agentId=taizi&limit=1');
      final headers = <String, String>{};
      if (_authToken.isNotEmpty) {
        headers['Authorization'] = 'Bearer $_authToken';
      }
      
      print('[OpenClawService] 请求 URL: $url');
      
      final response = await http.get(url, headers: headers).timeout(
        const Duration(seconds: 30),  // 增加到 30 秒
        onTimeout: () {
          print('[OpenClawService] 连接超时（30 秒）');
          return http.Response('{"error": "timeout"}', 408);
        },
      );
      
      print('[OpenClawService] 响应状态码：${response.statusCode}');
      
      // 200 = 成功，401 = 需要认证（但服务器可达）
      return response.statusCode == 200 || response.statusCode == 401;
    } catch (e) {
      print('[OpenClawService] 连接测试失败：$e');
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
