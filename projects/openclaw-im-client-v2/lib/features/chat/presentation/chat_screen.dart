import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:intl/intl.dart';

import 'chat_bloc.dart';
import '../../browser/browser_screen.dart';
import '../../remote_desktop/remote_desktop_screen.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    context.read<ChatBloc>().add(InitializeChat());
  }

  void _sendMessage() {
    final content = _messageController.text.trim();
    if (content.isEmpty) return;
    
    final state = context.read<ChatBloc>().state;
    if (state is ChatConnected) {
      context.read<ChatBloc>().add(
        SendMessage(sessionId: state.sessionId, content: content),
      );
      _messageController.clear();
      _scrollToBottom();
    }
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  void _showAgentSelector() {
    final state = context.read<ChatBloc>().state;
    if (state is! ChatConnected) return;

    showModalBottomSheet(
      context: context,
      builder: (context) => Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          const Padding(
            padding: EdgeInsets.all(16),
            child: Text(
              '选择 Agent',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
          ),
          if (state.availableAgents.isEmpty)
            const Padding(
              padding: EdgeInsets.all(16),
              child: Text('暂无可用 Agent'),
            )
          else
            ListView.builder(
              shrinkWrap: true,
              itemCount: state.availableAgents.length,
              itemBuilder: (context, index) {
                final agent = state.availableAgents[index];
                final isSelected = agent == state.agent;
                
                return ListTile(
                  leading: Icon(
                    Icons.smart_toy,
                    color: isSelected ? Colors.blue : null,
                  ),
                  title: Text(agent),
                  trailing: isSelected ? const Icon(Icons.check, color: Colors.blue) : null,
                  onTap: () {
                    context.read<ChatBloc>().add(SwitchAgent(agent: agent));
                    Navigator.pop(context);
                  },
                );
              },
            ),
          const SizedBox(height: 16),
        ],
      ),
    );
  }

  void _showMenu() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            ListTile(
              leading: const Icon(Icons.public),
              title: const Text('内置浏览器'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const BrowserScreen()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.desktop_windows),
              title: const Text('远程桌面'),
              onTap: () {
                Navigator.pop(context);
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const RemoteDesktopScreen()),
                );
              },
            ),
            ListTile(
              leading: const Icon(Icons.logout, color: Colors.red),
              title: const Text('退出登录', style: TextStyle(color: Colors.red)),
              onTap: () {
                Navigator.pop(context);
                context.read<ChatBloc>().add(ClearChat());
                Navigator.pop(context); // 返回登录页
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: BlocBuilder<ChatBloc, ChatState>(
          builder: (context, state) {
            if (state is ChatConnected) {
              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Agent: ${state.agent}'),
                  Text(
                    state.sessionId.isEmpty ? '未连接' : '已连接',
                    style: TextStyle(
                      fontSize: 12,
                      color: state.sessionId.isEmpty ? Colors.red : Colors.green,
                    ),
                  ),
                ],
              );
            }
            return const Text('OpenClaw IM');
          },
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.people),
            onPressed: _showAgentSelector,
          ),
          IconButton(
            icon: const Icon(Icons.menu),
            onPressed: _showMenu,
          ),
        ],
      ),
      body: BlocBuilder<ChatBloc, ChatState>(
        builder: (context, state) {
          if (state is ChatLoading) {
            return const Center(child: CircularProgressIndicator());
          }
          
          if (state is ChatDisconnected) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.cloud_off, size: 64, color: Colors.grey),
                  const SizedBox(height: 16),
                  Text('连接已断开${state.reason != null ? ': ${state.reason}' : ''}'),
                  const SizedBox(height: 16),
                  ElevatedButton(
                    onPressed: () {
                      context.read<ChatBloc>().add(InitializeChat());
                    },
                    child: const Text('重新连接'),
                  ),
                ],
              ),
            );
          }
          
          if (state is ChatError) {
            return Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const Icon(Icons.error, size: 64, color: Colors.red),
                  const SizedBox(height: 16),
                  Text('错误：${state.message}'),
                ],
              ),
            );
          }
          
          if (state is ChatConnected) {
            return Column(
              children: [
                // 消息列表
                Expanded(
                  child: state.messages.isEmpty
                      ? const Center(
                          child: Text(
                            '开始聊天吧！\n发送消息与 Agent 互动',
                            textAlign: TextAlign.center,
                            style: TextStyle(color: Colors.grey),
                          ),
                        )
                      : ListView.builder(
                          controller: _scrollController,
                          padding: const EdgeInsets.all(16),
                          itemCount: state.messages.length,
                          itemBuilder: (context, index) {
                            final message = state.messages[index];
                            return _MessageBubble(message: message);
                          },
                        ),
                ),
                
                // 输入框
                Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Theme.of(context).cardColor,
                    boxShadow: [
                      BoxShadow(
                        color: Colors.black.withOpacity(0.1),
                        blurRadius: 4,
                        offset: const Offset(0, -2),
                      ),
                    ],
                  ),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _messageController,
                          decoration: const InputDecoration(
                            hintText: '输入消息...',
                            border: OutlineInputBorder(),
                            contentPadding: EdgeInsets.symmetric(
                              horizontal: 16,
                              vertical: 8,
                            ),
                          ),
                          maxLines: null,
                          textCapitalization: TextCapitalization.sentences,
                          onSubmitted: (_) => _sendMessage(),
                        ),
                      ),
                      const SizedBox(width: 8),
                      IconButton(
                        icon: const Icon(Icons.send),
                        color: Theme.of(context).primaryColor,
                        onPressed: _sendMessage,
                      ),
                    ],
                  ),
                ),
              ],
            );
          }
          
          return const Center(child: Text('未知状态'));
        },
      ),
    );
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }
}

class _MessageBubble extends StatelessWidget {
  final ChatMessage message;

  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    final isFromMe = message.isFromMe;
    final timeFormat = DateFormat('HH:mm');

    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Row(
        mainAxisAlignment:
            isFromMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          if (!isFromMe) ...[
            const CircleAvatar(
              backgroundColor: Colors.blue,
              child: Icon(Icons.smart_toy, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 8),
          ],
          Flexible(
            child: Column(
              crossAxisAlignment:
                  isFromMe ? CrossAxisAlignment.end : CrossAxisAlignment.start,
              children: [
                Container(
                  padding: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 10,
                  ),
                  decoration: BoxDecoration(
                    color: isFromMe ? Colors.blue : Colors.grey[800],
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: Text(
                    message.content,
                    style: const TextStyle(fontSize: 15),
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  timeFormat.format(message.timestamp),
                  style: TextStyle(
                    fontSize: 12,
                    color: Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          if (isFromMe) ...[
            const SizedBox(width: 8),
            _StatusIcon(status: message.status),
          ],
        ],
      ),
    );
  }
}

class _StatusIcon extends StatelessWidget {
  final MessageStatus status;

  const _StatusIcon({required this.status});

  @override
  Widget build(BuildContext context) {
    IconData icon;
    Color color;

    switch (status) {
      case MessageStatus.sending:
        icon = Icons.access_time;
        color = Colors.grey;
        break;
      case MessageStatus.sent:
        icon = Icons.check;
        color = Colors.grey;
        break;
      case MessageStatus.delivered:
        icon = Icons.done_all;
        color = Colors.grey;
        break;
      case MessageStatus.read:
        icon = Icons.done_all;
        color = Colors.blue;
        break;
      case MessageStatus.failed:
        icon = Icons.error;
        color = Colors.red;
        break;
    }

    return Icon(icon, size: 16, color: color);
  }
}
