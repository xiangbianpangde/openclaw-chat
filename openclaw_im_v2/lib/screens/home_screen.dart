import 'package:flutter/material.dart';
import 'chat_screen.dart';

/// 主页面 - 仅聊天
class HomeScreen extends StatelessWidget {
  final String serverUrl;
  final String agentId;
  final String authToken;

  const HomeScreen({
    super.key,
    required this.serverUrl,
    required this.agentId,
    this.authToken = '',
  });

  @override
  Widget build(BuildContext context) {
    return ChatScreen(
      serverUrl: serverUrl,
      agentId: agentId,
      authToken: authToken,
    );
  }
}
