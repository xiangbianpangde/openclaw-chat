import 'package:hive_flutter/hive_flutter.dart';

/// 本地存储服务
class StorageService {
  static late Box _box;
  
  static const String _boxName = 'openclaw_chat';
  
  // 存储键
  static const String keyUserId = 'user_id';
  static const String keyToken = 'token';
  static const String keyServerIP = 'server_ip';
  static const String keyIsLoggedIn = 'is_logged_in';
  
  /// 初始化存储
  static Future<void> init() async {
    _box = await Hive.openBox(_boxName);
  }
  
  /// 保存登录状态
  static Future<void> saveLoginState({
    required String userId,
    required String token,
  }) async {
    await _box.put(keyUserId, userId);
    await _box.put(keyToken, token);
    await _box.put(keyIsLoggedIn, true);
  }
  
  /// 获取用户 ID
  static String? getUserId() => _box.get(keyUserId);
  
  /// 获取 Token
  static String? getToken() => _box.get(keyToken);
  
  /// 是否已登录
  static bool isLoggedIn() => _box.get(keyIsLoggedIn, defaultValue: false);
  
  /// 清除登录状态
  static Future<void> clearLoginState() async {
    await _box.delete(keyUserId);
    await _box.delete(keyToken);
    await _box.put(keyIsLoggedIn, false);
  }
  
  /// 保存服务器 IP
  static Future<void> saveServerIP(String ip) async {
    await _box.put(keyServerIP, ip);
  }
  
  /// 获取服务器 IP
  static String? getServerIP() => _box.get(keyServerIP);
  
  /// 通用存储
  static Future<void> put(String key, dynamic value) async {
    await _box.put(key, value);
  }
  
  /// 通用读取
  static T? get<T>(String key, {T? defaultValue}) {
    return _box.get(key, defaultValue: defaultValue);
  }
  
  /// 删除
  static Future<void> delete(String key) async {
    await _box.delete(key);
  }
  
  /// 清空所有
  static Future<void> clear() async {
    await _box.clear();
  }
}