import 'package:flutter_openim_sdk/flutter_openim_sdk.dart';
import 'package:get/get.dart';
import 'package:logger/logger.dart';

import 'storage_service.dart';

/// OpenIM 服务封装
/// 负责与 OpenIM Server 的所有交互
class OpenIMService extends GetxService {
  static final Logger _logger = Logger();
  
  // 单例
  static OpenIMService get to => Get.find();
  
  // 当前用户状态
  final RxBool isLoggedIn = false.obs;
  final RxString currentUserId = ''.obs;
  final RxString currentUserNickname = ''.obs;
  final RxString currentUserFaceURL = ''.obs;
  
  // OpenClaw 机器人 ID（用于识别 OpenClaw 消息）
  static const String openclawBotId = 'openclaw_bot';
  
  // OpenIM 配置
  static const String serverIP = 'YOUR_SERVER_IP'; // 替换为实际服务器 IP
  static const int wsPort = 10001;
  static const int apiPort = 10002;
  
  /// 初始化 OpenIM SDK
  static Future<void> init() async {
    _logger.i('初始化 OpenIM SDK...');
    
    await OpenIMSDK.i.initSDK(
      platform: Platform.android, // 根据平台动态设置
      apiAddr: 'http://$serverIP:$apiPort',
      wsAddr: 'ws://$serverIP:$wsPort',
      dataDir: '', // 默认目录
      logLevel: 5, // 生产环境设为 1-3
      onConnectFailed: (code, msg) {
        _logger.e('连接失败: $code, $msg');
      },
      onConnectSuccess: () {
        _logger.i('连接成功');
      },
      onKickedOffline: () {
        _logger.w('被踢下线');
        Get.offAllNamed('/login');
      },
      onUserTokenExpired: () {
        _logger.w('Token 过期');
        Get.offAllNamed('/login');
      },
    );
    
    // 注册消息监听
    _setupListeners();
    
    _logger.i('OpenIM SDK 初始化完成');
  }
  
  /// 设置消息监听
  static void _setupListeners() {
    // 新消息监听
    OpenIMSDK.i.setConversationListener(
      onConversationChanged: (list) {
        _logger.d('会话变化: ${list.length}');
      },
      onNewConversation: (list) {
        _logger.d('新会话: ${list.length}');
      },
      onTotalUnreadMessageCountChanged: (count) {
        _logger.d('未读消息数: $count');
      },
    );
    
    // 消息监听
    OpenIMSDK.i.setAdvancedMsgListener(
      onMsgDeleted: (message) {
        _logger.d('消息已删除');
      },
      onNewMessage: (message) {
        _logger.i('新消息: ${message.clientMsgID}');
        _handleNewMessage(message);
      },
      onRecvC2CReadReceipt: (list) {
        _logger.d('已读回执');
      },
      onRecvGroupReadReceipt: (list) {
        _logger.d('群组已读回执');
      },
      onRecvMessageRevoked: (msgId) {
        _logger.d('消息被撤回: $msgId');
      },
    );
  }
  
  /// 处理新消息
  static void _handleNewMessage(Message message) {
    // 检查是否来自 OpenClaw 机器人
    if (message.sendID == openclawBotId) {
      _logger.i('收到 OpenClaw 消息: ${message.content}');
      // 触发 OpenClaw 消息处理逻辑
      Get.find<OpenIMController>()?.handleOpenClawMessage(message);
    }
  }
  
  /// 登录
  Future<bool> login({
    required String userId,
    required String token,
  }) async {
    try {
      _logger.i('登录中: $userId');
      
      final result = await OpenIMSDK.i.login(
        userID: userId,
        token: token,
      );
      
      if (result) {
        isLoggedIn.value = true;
        currentUserId.value = userId;
        
        // 保存登录状态
        await StorageService.saveLoginState(userId: userId, token: token);
        
        // 获取用户信息
        final userInfo = await OpenIMSDK.i.getUsersInfo(
          userIDList: [userId],
        );
        
        if (userInfo.isNotEmpty) {
          currentUserNickname.value = userInfo.first.nickname ?? userId;
          currentUserFaceURL.value = userInfo.first.faceURL ?? '';
        }
        
        _logger.i('登录成功');
        return true;
      }
    } catch (e) {
      _logger.e('登录失败: $e');
    }
    return false;
  }
  
  /// 登出
  Future<void> logout() async {
    try {
      await OpenIMSDK.i.logout();
      isLoggedIn.value = false;
      currentUserId.value = '';
      await StorageService.clearLoginState();
      _logger.i('已登出');
    } catch (e) {
      _logger.e('登出失败: $e');
    }
  }
  
  /// 发送文本消息
  Future<Message?> sendTextMessage({
    required String receiverID,
    String? groupID,
    required String text,
  }) async {
    try {
      final message = await OpenIMSDK.i.sendMessage(
        contentType: MessageType.text,
        receiverID: receiverID,
        groupID: groupID,
        content: text,
      );
      return message;
    } catch (e) {
      _logger.e('发送消息失败: $e');
      return null;
    }
  }
  
  /// 发送消息给 OpenClaw 机器人
  Future<Message?> sendToOpenClaw(String text) async {
    return await sendTextMessage(
      receiverID: openclawBotId,
      text: text,
    );
  }
  
  /// 获取会话列表
  Future<List<ConversationInfo>> getConversationList() async {
    try {
      final result = await OpenIMSDK.i.getConversationListSplit(
        offset: 0,
        count: 100,
      );
      return result;
    } catch (e) {
      _logger.e('获取会话列表失败: $e');
      return [];
    }
  }
  
  /// 获取历史消息
  Future<List<Message>> getHistoryMessages({
    required String conversationID,
    int count = 20,
    Message? startMsg,
  }) async {
    try {
      final result = await OpenIMSDK.i.getAdvancedHistoryMessageList(
        conversationID: conversationID,
        count: count,
        startMsg: startMsg,
      );
      return result;
    } catch (e) {
      _logger.e('获取历史消息失败: $e');
      return [];
    }
  }
}

/// OpenIM 控制器（用于 UI 绑定）
class OpenIMController extends GetxController {
  final OpenIMService _service = OpenIMService.to;
  
  final RxList<ConversationInfo> conversations = <ConversationInfo>[].obs;
  final RxMap<String, List<Message>> messages = <String, List<Message>>{}.obs;
  
  @override
  void onInit() {
    super.onInit();
    _loadConversations();
  }
  
  Future<void> _loadConversations() async {
    final list = await _service.getConversationList();
    conversations.value = list;
  }
  
  /// 处理 OpenClaw 消息
  void handleOpenClawMessage(Message message) {
    _logger.i('处理 OpenClaw 消息: ${message.content}');
    // 更新 UI 或触发其他操作
    // 例如：如果是控制指令，更新远程桌面状态
  }
  
  /// 发送消息给 OpenClaw
  Future<void> sendOpenClawCommand(String command) async {
    await _service.sendToOpenClaw(command);
  }
}