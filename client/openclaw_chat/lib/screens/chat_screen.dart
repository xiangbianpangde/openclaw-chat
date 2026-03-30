import 'package:flutter/material.dart';
import '../services/openclaw_service.dart';

/// 聊天页面 - 直接集成 OpenClaw API
class ChatScreen extends StatefulWidget {
  final String serverUrl;
  final String agentId;

  const ChatScreen({
    super.key,
    required this.serverUrl,
    required this.agentId,
  });

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();
  late OpenClawService _openclawService;
  List<Message> _messages = [];
  bool _isLoading = false;
  String _currentAgentId = '';

  @override
  void initState() {
    super.initState();
    _openclawService = OpenClawService(
      serverUrl: widget.serverUrl,
      agentId: widget.agentId,
    );
    _currentAgentId = widget.agentId;
    _loadHistory();
  }

  Future<void> _loadHistory() async {
    setState(() => _isLoading = true);
    final history = await _openclawService.getHistory();
    setState(() {
      _messages = history;
      _isLoading = false;
    });
    _scrollToBottom();
  }

  Future<void> _sendMessage() async {
    final content = _messageController.text.trim();
    if (content.isEmpty) return;

    // 添加用户消息到列表
    final userMessage = Message(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sender: 'user',
      content: content,
      timestamp: DateTime.now(),
      isSelf: true,
    );
    setState(() => _messages.add(userMessage));
    _messageController.clear();
    _scrollToBottom();

    // 发送消息给 Agent
    setState(() => _isLoading = true);
    final response = await _openclawService.sendMessage(message: content);
    setState(() => _isLoading = false);

    // 添加 Agent 回复
    if (response.success) {
      final agentMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sender: _currentAgentId,
        content: response.reply,
        timestamp: DateTime.now(),
        isSelf: false,
      );
      setState(() => _messages.add(agentMessage));
      _scrollToBottom();
    } else {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('发送失败：${response.error}')),
        );
      }
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

  void _switchAgent() async {
    final agents = await _openclawService.getAgents();
    final selectedAgent = await showDialog<String>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('选择 Agent'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: agents.map((agent) {
            return ListTile(
              leading: Icon(
                Icons.rocket,
                color: agent.id == _currentAgentId ? Colors.blue : Colors.grey,
              ),
              title: Text(agent.name),
              subtitle: Text(agent.description),
              trailing: agent.id == _currentAgentId
                  ? const Icon(Icons.check, color: Colors.blue)
                  : null,
              onTap: () => Navigator.pop(context, agent.id),
            );
          }).toList(),
        ),
      ),
    );

    if (selectedAgent != null && selectedAgent != _currentAgentId) {
      setState(() => _currentAgentId = selectedAgent);
      _openclawService.switchAgent(selectedAgent);
      _loadHistory();
      
      // 添加系统消息
      final systemMessage = Message(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sender: 'system',
        content: '已切换到 ${_getAgentName(selectedAgent)}',
        timestamp: DateTime.now(),
        isSelf: false,
      );
      setState(() => _messages.add(systemMessage));
    }
  }

  String _getAgentName(String agentId) {
    switch (agentId) {
      case 'taizi':
        return '太子';
      case 'zhongshu':
        return '中书省';
      case 'shangshu':
        return '尚书省';
      case 'menxia':
        return '门下省';
      default:
        return agentId;
    }
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(_getAgentName(_currentAgentId)),
            Text(
              '点击切换',
              style: TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.swap_horiz),
            onPressed: _switchAgent,
            tooltip: '切换 Agent',
          ),
        ],
      ),
      body: Column(
        children: [
          // 消息列表
          Expanded(
            child: _isLoading && _messages.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.all(16),
                    itemCount: _messages.length,
                    itemBuilder: (context, index) {
                      final message = _messages[index];
                      return _buildMessageBubble(message);
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
                      border: InputBorder.none,
                      contentPadding: EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 12,
                      ),
                    ),
                    maxLines: null,
                    textCapitalization: TextCapitalization.sentences,
                    onSubmitted: (_) => _sendMessage(),
                  ),
                ),
                const SizedBox(width: 8),
                CircleAvatar(
                  child: IconButton(
                    icon: const Icon(Icons.send),
                    onPressed: _isLoading ? null : _sendMessage,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMessageBubble(Message message) {
    if (message.sender == 'system') {
      return Padding(
        padding: const EdgeInsets.symmetric(vertical: 8),
        child: Center(
          child: Container(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 4),
            decoration: BoxDecoration(
              color: Colors.grey[300],
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              message.content,
              style: TextStyle(color: Colors.grey[700], fontSize: 12),
            ),
          ),
        ),
      );
    }

    final isSelf = message.isSelf;

    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: isSelf ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isSelf) ...[
            CircleAvatar(
              backgroundColor: Colors.blue,
              child: Text(_getAgentName(_currentAgentId)[0]),
            ),
            const SizedBox(width: 8),
          ],
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.7,
            ),
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: isSelf ? Colors.blue : Colors.grey[200],
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (!isSelf) ...[
                  Text(
                    _getAgentName(_currentAgentId),
                    style: TextStyle(
                      fontSize: 12,
                      color: isSelf ? Colors.white70 : Colors.blue,
                    ),
                  ),
                  const SizedBox(height: 4),
                ],
                Text(
                  message.content,
                  style: TextStyle(
                    color: isSelf ? Colors.white : Colors.black,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  _formatTime(message.timestamp),
                  style: TextStyle(
                    fontSize: 10,
                    color: isSelf ? Colors.white70 : Colors.grey[600],
                  ),
                ),
              ],
            ),
          ),
          if (isSelf) ...[
            const SizedBox(width: 8),
            CircleAvatar(
              backgroundColor: Colors.green,
              child: const Text('我'),
            ),
          ],
        ],
      ),
    );
  }

  String _formatTime(DateTime time) {
    return '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}';
  }
}
