import 'dart:convert';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:http/http.dart' as http;

class OpenIMService {
  static const String _serverKey = 'openim_server';
  static const String _tokenKey = 'openim_token';
  static const String _userIdKey = 'openim_userid';

  static Future<String> getServerAddress() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_serverKey) ?? 'http://localhost:10002';
  }

  static Future<void> setServerAddress(String address) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_serverKey, address);
  }

  static Future<bool> isLoggedIn() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey) != null;
  }

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_tokenKey);
  }

  static Future<void> login(String userId, String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_tokenKey, token);
    await prefs.setString(_userIdKey, userId);
  }

  static Future<void> logout() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_tokenKey);
    await prefs.remove(_userIdKey);
  }

  static Future<String> getUserId() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_userIdKey) ?? '';
  }

  // 登录获取 Token
  static Future<Map<String, dynamic>> loginWithCredentials(
    String serverUrl,
    String userId,
    String secret,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$serverUrl/auth/user_token'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'userID': userId,
          'secret': secret,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        await setServerAddress(serverUrl);
        await login(userId, data['userToken'] ?? data['token']);
        return {'success': true, 'token': data['userToken']};
      } else {
        return {
          'success': false,
          'error': '登录失败：${response.statusCode}',
        };
      }
    } catch (e) {
      return {'success': false, 'error': '网络错误：$e'};
    }
  }

  // 发送消息
  static Future<Map<String, dynamic>> sendMessage(
    String serverUrl,
    String token,
    String receiverId,
    String content,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$serverUrl/msg/send_msg'),
        headers: {
          'Content-Type': 'application/json',
          'operationID': DateTime.now().millisecondsSinceEpoch.toString(),
          'token': token,
        },
        body: jsonEncode({
          'recvID': receiverId,
          'sendID': await getUserId(),
          'senderPlatformID': 1,
          'contentType': 101,
          'content': jsonEncode({'content': content}),
          'sessionType': 1,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return {'success': true};
      } else {
        return {'success': false, 'error': '发送失败'};
      }
    } catch (e) {
      return {'success': false, 'error': '网络错误：$e'};
    }
  }

  // 获取历史消息
  static Future<List<dynamic>> getHistoryMessages(
    String serverUrl,
    String token,
    String userId,
    int count,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$serverUrl/msg/get_history_msg'),
        headers: {
          'Content-Type': 'application/json',
          'operationID': DateTime.now().millisecondsSinceEpoch.toString(),
          'token': token,
        },
        body: jsonEncode({
          'userID': userId,
          'count': count,
        }),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['data'] ?? [];
      } else {
        return [];
      }
    } catch (e) {
      return [];
    }
  }
}
