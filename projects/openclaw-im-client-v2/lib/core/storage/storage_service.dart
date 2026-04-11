import 'package:hive_flutter/hive_flutter.dart';
import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:logger/logger.dart';

/// 存储服务 - 统一管理本地数据
class StorageService {
  static StorageService? _instance;
  static StorageService getInstance() => _instance ??= StorageService._internal();

  StorageService._internal();

  final Logger _logger = Logger();
  
  // Hive 盒子
  Box? _settingsBox;
  Box? _messagesBox;
  
  // 安全存储（加密）
  final FlutterSecureStorage _secureStorage = const FlutterSecureStorage();

  /// 初始化
  Future<void> init() async {
    try {
      // 打开 Hive 盒子
      _settingsBox = await Hive.openBox('settings');
      _messagesBox = await Hive.openBox('messages');
      
      _logger.i('Storage initialized');
    } catch (e) {
      _logger.e('Failed to initialize storage: $e');
      rethrow;
    }
  }

  // ========== Gateway 配置 ==========
  
  Future<void> saveGatewayUrl(String url) async {
    await _settingsBox?.put('gateway_url', url);
    _logger.d('Gateway URL saved: $url');
  }

  String? getGatewayUrl() {
    return _settingsBox?.get('gateway_url');
  }

  // ========== Token 管理（加密存储） ==========
  
  Future<void> saveToken(String token) async {
    await _secureStorage.write(key: 'auth_token', value: token);
    _logger.d('Token saved (encrypted)');
  }

  Future<String?> getToken() async {
    return await _secureStorage.read(key: 'auth_token');
  }

  Future<void> deleteToken() async {
    await _secureStorage.delete(key: 'auth_token');
    _logger.d('Token deleted');
  }

  // ========== Agent 选择 ==========
  
  Future<void> saveSelectedAgent(String agent) async {
    await _settingsBox?.put('selected_agent', agent);
    _logger.d('Selected agent saved: $agent');
  }

  String? getSelectedAgent() {
    return _settingsBox?.get('selected_agent');
  }

  // ========== 消息缓存 ==========
  
  Future<void> saveMessage(String sessionId, Map<String, dynamic> message) async {
    final key = '${sessionId}_${message['timestamp'] ?? DateTime.now().millisecondsSinceEpoch}';
    await _messagesBox?.put(key, message);
  }

  List<Map<String, dynamic>> getMessages(String sessionId) {
    final messages = <Map<String, dynamic>>[];
    final keys = _messagesBox?.keys ?? [];
    
    for (final key in keys) {
      final message = _messagesBox?.get(key);
      if (message != null && message['sessionId'] == sessionId) {
        messages.add(Map<String, dynamic>.from(message));
      }
    }
    
    // 按时间排序
    messages.sort((a, b) => 
      (a['timestamp'] ?? 0).compareTo(b['timestamp'] ?? 0)
    );
    
    return messages;
  }

  Future<void> clearMessages(String sessionId) async {
    final keys = _messagesBox?.keys ?? [];
    for (final key in keys) {
      final message = _messagesBox?.get(key);
      if (message != null && message['sessionId'] == sessionId) {
        await _messagesBox?.delete(key);
      }
    }
    _logger.d('Messages cleared for session: $sessionId');
  }

  // ========== 自动登录状态 ==========
  
  Future<void> setAutoLogin(bool enabled) async {
    await _settingsBox?.put('auto_login', enabled);
  }

  bool getAutoLogin() {
    return _settingsBox?.get('auto_login', defaultValue: false) ?? false;
  }

  // ========== 清除所有数据 ==========
  
  Future<void> clearAll() async {
    await _settingsBox?.clear();
    await _messagesBox?.clear();
    await _secureStorage.deleteAll();
    _logger.w('All storage cleared');
  }
}
