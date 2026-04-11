import 'package:flutter/material.dart';
import '../services/openclaw_service.dart';

/// 聊天页面 - 直接集成 OpenClaw API
class ChatScreen extends StatefulWidget {
  final String serverUrl;
  final String agentId;
  final String authToken;

  const ChatScreen({
    super.key,
    required this.serverUrl,
    required this.agentId,
    this.authToken = '',
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
  bool _isConnecting = true;  // 初始连接状态
  String _currentAgentId = '';
  String? _connectionError;

  @override
  void initState() {
    super.initState();
    print('[ChatScreen] 初始化 - serverUrl: ${widget.serverUrl}, agentId: ${widget.agentId}');
    _openclawService = OpenClawService(
      serverUrl: widget.serverUrl,
      agentId: widget.agentId,
      authToken: widget.authToken,
    );
    _currentAgentId = widget.agentId;
    _testConnectionAndLoad();
  }

  /// 测试连接并加载历史
  Future<void> _testConnectionAndLoad() async {
    print('[ChatScreen] 开始测试连接...');
    setState(() {
      _isConnecting = true;
      _connectionError = null;
    });
    
    try {
      final connected = await _openclawService.testConnection();
      
      if (connected) {
        print('[ChatScreen] 连接测试成功，加载历史消息...');
        setState(() => _isConnecting = false);
        await _loadHistory();
      } else {
        print('[ChatScreen] 连接测试失败');
        setState(() {
          _isConnecting = false;
          _connectionError = '无法连接到服务器：${widget.serverUrl}\n\n请检查：\n1. 服务器地址是否正确\n2. 服务器是否运行\n3. 网络连接是否正常';
        });
      }
    } catch (e, stackTrace) {
      print('[ChatScreen] 连接异常：$e');
      print('[ChatScreen] 堆栈：$stackTrace');
      setState(() {
        _isConnecting = false;
        _connectionError = '连接错误：$e';
      });
    }
  }

  Future<void> _loadHistory() async {
    print('[ChatScreen] 开始加载历史消息...');
    setState(() => _isLoading = true);
    try {
      final history = await _openclawService.getHistory();
      print('[ChatScreen] 历史消息加载成功，共 ${history.length} 条');
      setState(() {
        _messages = history;
        _isLoading = false;
      });
      _scrollToBottom();
    } catch (e, stackTrace) {
      print('[ChatScreen] 加载历史消息失败：$e');
      print('[ChatScreen] 堆栈跟踪：$stackTrace');
      setState(() => _isLoading = false);
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('加载历史消息失败：$e'),
            backgroundColor: Colors.orange,
          ),
        );
      }
    }
  }

  Future<void> _sendMessage() async {
    final content = _messageController.text.trim();
    if (content.isEmpty) {
      print('[ChatScreen] 发送消息：内容为空，忽略');
      return;
    }

    print('[ChatScreen] 发送消息："$content"');

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
    print('[ChatScreen] 正在调用 API 发送消息...');
    setState(() => _isLoading = true);
    try {
      final response = await _openclawService.sendMessage(message: content);
      print('[ChatScreen] API 响应：success=${response.success}, error=${response.error ?? "none"}');
      
      // 添加 Agent 回复
      if (response.success) {
        print('[ChatScreen] 收到 Agent 回复：${response.reply.substring(0, 50)}...');
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
        print('[ChatScreen] 发送失败：${response.error}');
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text('发送失败：${response.error}'),
              backgroundColor: Colors.red,
              duration: const Duration(seconds: 5),
            ),
          );
        }
      }
    } catch (e, stackTrace) {
      print('[ChatScreen] 发送消息异常：$e');
      print('[ChatScreen] 堆栈跟踪：$stackTrace');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('发送异常：$e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      setState(() => _isLoading = false);
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
            Row(
              children: [
                Text(_getAgentName(_currentAgentId)),
                const SizedBox(width: 8),
                // 连接状态指示器
                Container(
                  width: 8,
                  height: 8,
                  decoration: BoxDecoration(
                    color: _isConnecting 
                        ? Colors.orange 
                        : _connectionError != null 
                            ? Colors.red 
                            : Colors.green,
                    shape: BoxShape.circle,
                  ),
                ),
              ],
            ),
            Text(
              _isConnecting 
                  ? '连接中...' 
                  : _connectionError != null 
                      ? '连接失败' 
                      : '在线',
              style: TextStyle(fontSize: 12, color: Colors.white70),
            ),
          ],
        ),
        actions: [
          if (_connectionError != null)
            IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _testConnectionAndLoad,
              tooltip: '重新连接',
            ),
          IconButton(
            icon: const Icon(Icons.swap_horiz),
            onPressed: _switchAgent,
            tooltip: '切换 Agent',
          ),
        ],
      ),
      body: Column(
        children: [
          // 连接中状态
          if (_isConnecting)
            const Expanded(
              child: Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    CircularProgressIndicator(),
                    SizedBox(height: 16),
                    Text('正在连接服务器...', style: TextStyle(fontSize: 16)),
                    SizedBox(height: 8),
                    Text('请稍候，最多等待 30 秒', style: TextStyle(fontSize: 12, color: Colors.grey)),
                  ],
                ),
              ),
            )
          // 连接失败状态
          else if (_connectionError != null)
            Expanded(
              child: Center(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.error_outline, size: 64, color: Colors.red),
                      const SizedBox(height: 16),
                      const Text('连接失败', style: TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
                      const SizedBox(height: 16),
                      Text(
                        _connectionError!,
                        style: const TextStyle(fontSize: 14),
                        textAlign: TextAlign.center,
                      ),
                      const SizedBox(height: 24),
                      FilledButton.icon(
                        onPressed: _testConnectionAndLoad,
                        icon: const Icon(Icons.refresh),
                        label: const Text('重新连接'),
                      ),
                    ],
                  ),
                ),
              ),
            )
          // 正常聊天界面
          else
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
