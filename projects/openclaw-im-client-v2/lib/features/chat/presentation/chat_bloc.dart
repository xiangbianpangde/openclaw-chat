import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';

import '../../../core/websocket/websocket_service.dart';
import '../../../core/storage/storage_service.dart';

// ========== Message Model ==========

class ChatMessage {
  final String id;
  final String sessionId;
  final String content;
  final bool isFromMe;
  final DateTime timestamp;
  final MessageStatus status;

  ChatMessage({
    required this.id,
    required this.sessionId,
    required this.content,
    required this.isFromMe,
    required this.timestamp,
    this.status = MessageStatus.sent,
  });

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'sessionId': sessionId,
      'content': content,
      'isFromMe': isFromMe,
      'timestamp': timestamp.millisecondsSinceEpoch,
      'status': status.name,
    };
  }

  factory ChatMessage.fromJson(Map<String, dynamic> json) {
    return ChatMessage(
      id: json['id'] ?? DateTime.now().millisecondsSinceEpoch.toString(),
      sessionId: json['sessionId'] ?? '',
      content: json['content'] ?? '',
      isFromMe: json['isFromMe'] ?? false,
      timestamp: DateTime.fromMillisecondsSinceEpoch(json['timestamp'] ?? DateTime.now().millisecondsSinceEpoch),
      status: MessageStatus.values.firstWhere(
        (e) => e.name == json['status'],
        orElse: () => MessageStatus.sent,
      ),
    );
  }
}

enum MessageStatus { sending, sent, delivered, read, failed }

// ========== Events ==========

abstract class ChatEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class InitializeChat extends ChatEvent {
  @override
  List<Object?> get props => [];
}

class SendMessage extends ChatEvent {
  final String sessionId;
  final String content;
  
  SendMessage({required this.sessionId, required this.content});
  
  @override
  List<Object?> get props => [sessionId, content];
}

class CreateSession extends ChatEvent {
  final String agent;
  
  CreateSession({required this.agent});
  
  @override
  List<Object?> get props => [agent];
}

class SwitchAgent extends ChatEvent {
  final String agent;
  
  SwitchAgent({required this.agent});
  
  @override
  List<Object?> get props => [agent];
}

class LoadMessages extends ChatEvent {
  final String sessionId;
  
  LoadMessages({required this.sessionId});
  
  @override
  List<Object?> get props => [sessionId];
}

class ClearChat extends ChatEvent {
  @override
  List<Object?> get props => [];
}

// ========== States ==========

abstract class ChatState extends Equatable {
  @override
  List<Object?> get props => [];
}

class ChatInitial extends ChatState {
  @override
  List<Object?> get props => [];
}

class ChatLoading extends ChatState {
  @override
  List<Object?> get props => [];
}

class ChatConnected extends ChatState {
  final String sessionId;
  final String agent;
  final List<ChatMessage> messages;
  final List<String> availableAgents;
  
  ChatConnected({
    required this.sessionId,
    required this.agent,
    this.messages = const [],
    this.availableAgents = const [],
  });
  
  @override
  List<Object?> get props => [sessionId, agent, messages, availableAgents];
}

class ChatDisconnected extends ChatState {
  final String? reason;
  
  ChatDisconnected({this.reason});
  
  @override
  List<Object?> get props => [reason];
}

class ChatError extends ChatState {
  final String message;
  
  ChatError({required this.message});
  
  @override
  List<Object?> get props => [message];
}

// ========== BLoC ==========

class ChatBloc extends Bloc<ChatEvent, ChatState> {
  final Logger _logger = Logger();
  final WebSocketService _websocketService;
  final StorageService _storage = StorageService.getInstance();

  String? _currentSessionId;
  String? _currentAgent;

  ChatBloc(this._websocketService) : super(ChatInitial()) {
    on<InitializeChat>(_onInitialize);
    on<SendMessage>(_onSendMessage);
    on<CreateSession>(_onCreateSession);
    on<SwitchAgent>(_onSwitchAgent);
    on<LoadMessages>(_onLoadMessages);
    on<ClearChat>(_onClearChat);
    
    // 监听 WebSocket 消息
    _websocketService.messageStream.listen(_onMessageReceived);
    _websocketService.statusStream.listen(_onConnectionStatusChanged);
  }

  Future<void> _onInitialize(InitializeChat event, Emitter<ChatState> emit) async {
    emit(ChatLoading());
    
    try {
      _currentAgent = _storage.getSelectedAgent();
      
      if (_currentAgent != null && _websocketService.isConnected) {
        // 创建会话
        _websocketService.createSession(agent: _currentAgent!);
      } else {
        emit(ChatDisconnected(reason: '未连接或无 Agent'));
      }
    } catch (e) {
      _logger.e('Chat initialization failed: $e');
      emit(ChatError(message: '初始化失败：$e'));
    }
  }

  void _onSendMessage(SendMessage event, Emitter<ChatState> emit) {
    if (!_websocketService.isConnected) {
      emit(ChatDisconnected(reason: '未连接'));
      return;
    }
    
    // 添加本地消息
    final message = ChatMessage(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      sessionId: event.sessionId,
      content: event.content,
      isFromMe: true,
      timestamp: DateTime.now(),
      status: MessageStatus.sending,
    );
    
    // 保存到本地
    _storage.saveMessage(event.sessionId, message.toJson());
    
    // 发送
    _websocketService.sendMessage(sessionId: event.sessionId, content: event.content);
    
    _logger.d('Message sent: ${event.content}');
    
    // 更新状态
    if (state is ChatConnected) {
      final currentState = state as ChatConnected;
      emit(ChatConnected(
        sessionId: currentState.sessionId,
        agent: currentState.agent,
        messages: [...currentState.messages, message],
        availableAgents: currentState.availableAgents,
      ));
    }
  }

  void _onCreateSession(CreateSession event, Emitter<ChatState> emit) {
    if (!_websocketService.isConnected) {
      emit(ChatDisconnected(reason: '未连接'));
      return;
    }
    
    _websocketService.createSession(agent: event.agent);
    _currentAgent = event.agent;
    _storage.saveSelectedAgent(event.agent);
    
    _logger.i('Session created for agent: ${event.agent}');
  }

  void _onSwitchAgent(SwitchAgent event, Emitter<ChatState> emit) {
    _currentAgent = event.agent;
    _storage.saveSelectedAgent(event.agent);
    
    // 创建新会话
    _websocketService.createSession(agent: event.agent);
    
    _logger.i('Agent switched to: ${event.agent}');
  }

  void _onLoadMessages(LoadMessages event, Emitter<ChatState> emit) {
    final messages = _storage.getMessages(event.sessionId);
    final chatMessages = messages.map((m) => ChatMessage.fromJson(m)).toList();
    
    if (state is ChatConnected) {
      final currentState = state as ChatConnected;
      emit(ChatConnected(
        sessionId: currentState.sessionId,
        agent: currentState.agent,
        messages: chatMessages,
        availableAgents: currentState.availableAgents,
      ));
    }
    
    _logger.d('Loaded ${chatMessages.length} messages for session ${event.sessionId}');
  }

  void _onClearChat(ClearChat event, Emitter<ChatState> emit) {
    if (_currentSessionId != null) {
      _storage.clearMessages(_currentSessionId!);
    }
    
    if (state is ChatConnected) {
      final currentState = state as ChatConnected;
      emit(ChatConnected(
        sessionId: currentState.sessionId,
        agent: currentState.agent,
        messages: [],
        availableAgents: currentState.availableAgents,
      ));
    }
    
    _logger.d('Chat cleared');
  }

  void _onMessageReceived(WebSocketMessage message) {
    _logger.d('Chat message received: ${message.type}');
    
    // 处理会话创建响应
    if (message.type == 'session.create' && message.payload != null) {
      _currentSessionId = message.payload!['sessionId'];
      _logger.i('Session created: $_currentSessionId');
      
      // 加载历史消息
      if (_currentSessionId != null) {
        add(LoadMessages(sessionId: _currentSessionId!));
      }
      
      if (state is ChatConnected) {
        final currentState = state as ChatConnected;
        emit(ChatConnected(
          sessionId: _currentSessionId ?? currentState.sessionId,
          agent: _currentAgent ?? currentState.agent,
          messages: currentState.messages,
          availableAgents: currentState.availableAgents,
        ));
      } else {
        emit(ChatConnected(
          sessionId: _currentSessionId ?? '',
          agent: _currentAgent ?? '',
          messages: [],
          availableAgents: [],
        ));
      }
    }
    
    // 处理收到的消息
    if (message.type == 'session.message' && message.content != null) {
      final chatMessage = ChatMessage(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        sessionId: message.sessionId ?? _currentSessionId ?? '',
        content: message.content!,
        isFromMe: false,
        timestamp: DateTime.now(),
        status: MessageStatus.delivered,
      );
      
      // 保存到本地
      _storage.saveMessage(chatMessage.sessionId, chatMessage.toJson());
      
      // 更新状态
      if (state is ChatConnected) {
        final currentState = state as ChatConnected;
        emit(ChatConnected(
          sessionId: currentState.sessionId,
          agent: currentState.agent,
          messages: [...currentState.messages, chatMessage],
          availableAgents: currentState.availableAgents,
        ));
      }
      
      _logger.d('Message received: ${chatMessage.content}');
    }
    
    // 处理 Agent 列表
    if (message.type == 'node.list' && message.payload != null) {
      final agents = List<String>.from(message.payload!['nodes'] ?? []);
      
      if (state is ChatConnected) {
        final currentState = state as ChatConnected;
        emit(ChatConnected(
          sessionId: currentState.sessionId,
          agent: currentState.agent,
          messages: currentState.messages,
          availableAgents: agents,
        ));
      }
    }
  }

  void _onConnectionStatusChanged(ConnectionStatus status) {
    _logger.d('Connection status: $status');
    
    if (status == ConnectionStatus.disconnected) {
      emit(ChatDisconnected(reason: '连接已断开'));
    } else if (status == ConnectionStatus.connected && state is ChatDisconnected) {
      // 重连后重新初始化
      add(InitializeChat());
    }
  }

  String? get currentSessionId => _currentSessionId;
  String? get currentAgent => _currentAgent;
}
