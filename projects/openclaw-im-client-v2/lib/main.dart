/// OpenClaw IM Client v2.0
/// 
/// 官方 Flutter 客户端 - 直连 OpenClaw Gateway WebSocket 协议
/// 
/// 核心功能：
/// - 登录认证（Token + Gateway 地址配置）
/// - WebSocket 聊天（消息收发、Agent 切换）
/// - 内置浏览器（WebView 集成）
/// - 远程桌面（noVNC 集成）
/// 
/// 技术栈：
/// - Flutter 3.x
/// - web_socket_channel
/// - flutter_bloc
/// - Hive (本地存储)

import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:hive_flutter/hive_flutter.dart';

import 'app/app.dart';
import 'core/storage/storage_service.dart';
import 'core/websocket/websocket_service.dart';
import 'features/auth/presentation/auth_bloc.dart';
import 'features/chat/presentation/chat_bloc.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  
  // 初始化 Hive
  await Hive.initFlutter();
  
  // 初始化存储
  await StorageService.getInstance().init();
  
  // 初始化 WebSocket 服务
  final websocketService = WebSocketService.getInstance();
  
  runApp(
    MultiBlocProvider(
      providers: [
        BlocProvider<AuthBloc>(
          create: (_) => AuthBloc(websocketService),
        ),
        BlocProvider<ChatBloc>(
          create: (_) => ChatBloc(websocketService),
        ),
      ],
      child: const OpenClawApp(),
    ),
  );
}
