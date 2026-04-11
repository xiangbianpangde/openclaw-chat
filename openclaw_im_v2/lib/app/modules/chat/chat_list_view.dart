import 'package:flutter/material.dart';
import 'package:flutter_openim_sdk/flutter_openim_sdk.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';

import '../../services/openim_service.dart';

class ChatListController extends GetxController {
  final OpenIMService _service = OpenIMService.to;
  
  final RxList<ConversationInfo> conversations = <ConversationInfo>[].obs;
  final RxBool isLoading = false.obs;
  
  @override
  void onInit() {
    super.onInit();
    loadConversations();
  }
  
  Future<void> loadConversations() async {
    isLoading.value = true;
    try {
      final list = await _service.getConversationList();
      conversations.value = list;
    } finally {
      isLoading.value = false;
    }
  }
  
  Future<void> refresh() async {
    await loadConversations();
  }
  
  void openChat(ConversationInfo conversation) {
    Get.toNamed(
      '/chat',
      arguments: {
        'conversationID': conversation.conversationID,
        'name': conversation.showName,
        'faceURL': conversation.faceURL,
      },
    );
  }
  
  void openRemoteDesktop() {
    Get.toNamed('/remote-desktop');
  }
  
  void openSettings() {
    Get.toNamed('/settings');
  }
  
  Future<void> logout() async {
    final confirm = await Get.dialog<bool>(
      AlertDialog(
        title: const Text('确认登出'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: const Text('确定'),
          ),
        ],
      ),
    );
    
    if (confirm == true) {
      await _service.logout();
      Get.offAllNamed('/login');
    }
  }
}

class ChatListView extends StatelessWidget {
  const ChatListView({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ChatListController());
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('OpenClaw Chat'),
        actions: [
          IconButton(
            icon: const Icon(Icons.desktop_windows_outlined),
            tooltip: '远程桌面',
            onPressed: controller.openRemoteDesktop,
          ),
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            tooltip: '设置',
            onPressed: controller.openSettings,
          ),
        ],
      ),
      body: Obx(() {
        if (controller.isLoading.value) {
          return const Center(child: CircularProgressIndicator());
        }
        
        if (controller.conversations.isEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.chat_bubble_outline_rounded,
                  size: 64.sp,
                  color: Colors.grey,
                ),
                SizedBox(height: 16.h),
                Text(
                  '暂无会话',
                  style: TextStyle(
                    fontSize: 16.sp,
                    color: Colors.grey,
                  ),
                ),
                SizedBox(height: 8.h),
                Text(
                  '点击右下角按钮与 OpenClaw 对话',
                  style: TextStyle(
                    fontSize: 14.sp,
                    color: Colors.grey.shade400,
                  ),
                ),
              ],
            ),
          );
        }
        
        return RefreshIndicator(
          onRefresh: controller.refresh,
          child: ListView.builder(
            itemCount: controller.conversations.length,
            itemBuilder: (context, index) {
              final conv = controller.conversations[index];
              return _ConversationTile(
                conversation: conv,
                onTap: () => controller.openChat(conv),
              );
            },
          ),
        );
      }),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // 打开与 OpenClaw 的对话
          Get.toNamed('/chat', arguments: {
            'conversationID': 'openclaw_bot',
            'name': 'OpenClaw',
            'faceURL': null,
          });
        },
        child: const Icon(Icons.add_comment_outlined),
      ),
    );
  }
}

class _ConversationTile extends StatelessWidget {
  final ConversationInfo conversation;
  final VoidCallback onTap;
  
  const _ConversationTile({
    required this.conversation,
    required this.onTap,
  });
  
  @override
  Widget build(BuildContext context) {
    return ListTile(
      leading: CircleAvatar(
        radius: 24.r,
        backgroundImage: conversation.faceURL != null
            ? NetworkImage(conversation.faceURL!)
            : null,
        child: conversation.faceURL == null
            ? Text(
                (conversation.showName ?? '?')[0].toUpperCase(),
                style: TextStyle(fontSize: 20.sp),
              )
            : null,
      ),
      title: Text(
        conversation.showName ?? '未知',
        style: TextStyle(
          fontSize: 16.sp,
          fontWeight: FontWeight.w500,
        ),
      ),
      subtitle: Text(
        _getLastMessage(conversation),
        maxLines: 1,
        overflow: TextOverflow.ellipsis,
        style: TextStyle(
          fontSize: 14.sp,
          color: Colors.grey,
        ),
      ),
      trailing: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            _formatTime(conversation.latestMsg?.sendTime),
            style: TextStyle(
              fontSize: 12.sp,
              color: Colors.grey,
            ),
          ),
          if (conversation.unreadCount > 0) ...[
            SizedBox(height: 4.h),
            Container(
              padding: EdgeInsets.symmetric(horizontal: 6.w, vertical: 2.h),
              decoration: BoxDecoration(
                color: Theme.of(context).colorScheme.primary,
                borderRadius: BorderRadius.circular(10.r),
              ),
              child: Text(
                '${conversation.unreadCount}',
                style: TextStyle(
                  fontSize: 10.sp,
                  color: Colors.white,
                ),
              ),
            ),
          ],
        ],
      ),
      onTap: onTap,
    );
  }
  
  String _getLastMessage(ConversationInfo conv) {
    final msg = conv.latestMsg;
    if (msg == null) return '暂无消息';
    
    // 根据消息类型返回摘要
    switch (msg.contentType) {
      case MessageType.text:
        return msg.textElem?.content ?? '';
      case MessageType.picture:
        return '[图片]';
      case MessageType.video:
        return '[视频]';
      case MessageType.file:
        return '[文件]';
      default:
        return '[消息]';
    }
  }
  
  String _formatTime(int? timestamp) {
    if (timestamp == null) return '';
    final date = DateTime.fromMillisecondsSinceEpoch(timestamp);
    final now = DateTime.now();
    
    if (date.year == now.year &&
        date.month == now.month &&
        date.day == now.day) {
      return '${date.hour.toString().padLeft(2, '0')}:${date.minute.toString().padLeft(2, '0')}';
    }
    
    return '${date.month}/${date.day}';
  }
}