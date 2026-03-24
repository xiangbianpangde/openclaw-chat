import 'package:flutter/material.dart';
import 'package:flutter_openim_sdk/flutter_openim_sdk.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';

import '../../services/openim_service.dart';

class ChatController extends GetxController {
  final OpenIMService _service = OpenIMService.to;
  
  late String conversationID;
  late String name;
  String? faceURL;
  
  final RxList<Message> messages = <Message>[].obs;
  final RxBool isLoading = false.obs;
  final TextEditingController inputController = TextEditingController();
  final ScrollController scrollController = ScrollController();
  
  // 是否为 OpenClaw 对话
  final RxBool isOpenClawChat = false.obs;
  
  @override
  void onInit() {
    super.onInit();
    
    // 获取参数
    final args = Get.arguments as Map<String, dynamic>;
    conversationID = args['conversationID'] ?? '';
    name = args['name'] ?? '未知';
    faceURL = args['faceURL'];
    
    // 检查是否为 OpenClaw 对话
    isOpenClawChat.value = conversationID.contains('openclaw');
    
    loadMessages();
  }
  
  Future<void> loadMessages() async {
    isLoading.value = true;
    try {
      final list = await _service.getHistoryMessages(
        conversationID: conversationID,
        count: 50,
      );
      messages.value = list.reversed.toList();
      _scrollToBottom();
    } finally {
      isLoading.value = false;
    }
  }
  
  Future<void> sendMessage() async {
    final text = inputController.text.trim();
    if (text.isEmpty) return;
    
    inputController.clear();
    
    // 发送消息
    await _service.sendTextMessage(
      receiverID: isOpenClawChat.value ? OpenIMService.openclawBotId : conversationID,
      text: text,
    );
    
    // 刷新消息列表
    await loadMessages();
  }
  
  void _scrollToBottom() {
    if (scrollController.hasClients) {
      scrollController.animateTo(
        scrollController.position.maxScrollExtent,
        duration: const Duration(milliseconds: 300),
        curve: Curves.easeOut,
      );
    }
  }
  
  // 快捷命令（OpenClaw 对话时显示）
  final List<String> quickCommands = [
    '/help - 显示帮助',
    '/status - 查看状态',
    '/scan - 扫码登录',
    '/desktop - 远程桌面',
  ];
  
  void sendQuickCommand(String command) {
    inputController.text = command.split(' - ')[0];
    sendMessage();
  }
  
  @override
  void onClose() {
    inputController.dispose();
    scrollController.dispose();
    super.onClose();
  }
}

class ChatView extends StatelessWidget {
  const ChatView({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(ChatController());
    
    return Scaffold(
      appBar: AppBar(
        title: Obx(() => Text(controller.name)),
        actions: [
          if (controller.isOpenClawChat.value)
            IconButton(
              icon: const Icon(Icons.desktop_windows_outlined),
              tooltip: '远程桌面',
              onPressed: () => Get.toNamed('/remote-desktop'),
            ),
        ],
      ),
      body: Column(
        children: [
          // 快捷命令（仅 OpenClaw 对话显示）
          Obx(() {
            if (!controller.isOpenClawChat.value) return const SizedBox.shrink();
            
            return Container(
              height: 40.h,
              padding: EdgeInsets.symmetric(horizontal: 12.w),
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                itemCount: controller.quickCommands.length,
                itemBuilder: (context, index) {
                  final cmd = controller.quickCommands[index];
                  return Padding(
                    padding: EdgeInsets.only(right: 8.w),
                    child: ActionChip(
                      label: Text(
                        cmd.split(' - ')[0],
                        style: TextStyle(fontSize: 12.sp),
                      ),
                      onPressed: () => controller.sendQuickCommand(cmd),
                    ),
                  );
                },
              ),
            );
          }),
          
          // 消息列表
          Expanded(
            child: Obx(() {
              if (controller.isLoading.value && controller.messages.isEmpty) {
                return const Center(child: CircularProgressIndicator());
              }
              
              return ListView.builder(
                controller: controller.scrollController,
                padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
                itemCount: controller.messages.length,
                itemBuilder: (context, index) {
                  final msg = controller.messages[index];
                  final isSelf = msg.sendID == OpenIMService.to.currentUserId.value;
                  return _MessageBubble(
                    message: msg,
                    isSelf: isSelf,
                  );
                },
              );
            }),
          ),
          
          // 输入框
          Container(
            padding: EdgeInsets.all(12.w),
            decoration: BoxDecoration(
              color: Theme.of(context).scaffoldBackgroundColor,
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, -1),
                ),
              ],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: controller.inputController,
                      decoration: InputDecoration(
                        hintText: '输入消息...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24.r),
                        ),
                        contentPadding: EdgeInsets.symmetric(
                          horizontal: 16.w,
                          vertical: 10.h,
                        ),
                      ),
                      maxLines: 4,
                      minLines: 1,
                      onSubmitted: (_) => controller.sendMessage(),
                    ),
                  ),
                  SizedBox(width: 8.w),
                  Obx(() => FloatingActionButton(
                    mini: true,
                    onPressed: controller.inputController.text.isEmpty
                        ? null
                        : controller.sendMessage,
                    child: const Icon(Icons.send),
                  )),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _MessageBubble extends StatelessWidget {
  final Message message;
  final bool isSelf;
  
  const _MessageBubble({
    required this.message,
    required this.isSelf,
  });
  
  @override
  Widget build(BuildContext context) {
    return Align(
      alignment: isSelf ? Alignment.centerRight : Alignment.centerLeft,
      child: Container(
        margin: EdgeInsets.symmetric(vertical: 4.h),
        padding: EdgeInsets.symmetric(horizontal: 12.w, vertical: 8.h),
        constraints: BoxConstraints(maxWidth: 0.7.sw),
        decoration: BoxDecoration(
          color: isSelf
              ? Theme.of(context).colorScheme.primary
              : Theme.of(context).colorScheme.surfaceContainerHighest,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(12),
            topRight: const Radius.circular(12),
            bottomLeft: Radius.circular(isSelf ? 12 : 4),
            bottomRight: Radius.circular(isSelf ? 4 : 12),
          ),
        ),
        child: _buildContent(context),
      ),
    );
  }
  
  Widget _buildContent(BuildContext context) {
    final textColor = isSelf ? Colors.white : null;
    
    switch (message.contentType) {
      case MessageType.text:
        return Text(
          message.textElem?.content ?? '',
          style: TextStyle(color: textColor),
        );
      case MessageType.picture:
        return ClipRRect(
          borderRadius: BorderRadius.circular(8.r),
          child: Image.network(
            message.pictureElem?.snapshotPicture?.sourcePicture?.url ?? '',
            fit: BoxFit.cover,
          ),
        );
      default:
        return Text(
          '[不支持的消息类型]',
          style: TextStyle(color: textColor),
        );
    }
  }
}