import 'package:equatable/equatable.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:logger/logger.dart';

import '../../../core/websocket/websocket_service.dart';
import '../../../core/storage/storage_service.dart';

// ========== Events ==========

abstract class AuthEvent extends Equatable {
  @override
  List<Object?> get props => [];
}

class InitializeAuth extends AuthEvent {
  @override
  List<Object?> get props => [];
}

class ConfigureGateway extends AuthEvent {
  final String gatewayUrl;
  
  ConfigureGateway({required this.gatewayUrl});
  
  @override
  List<Object?> get props => [gatewayUrl];
}

class LoginWithToken extends AuthEvent {
  final String token;
  
  LoginWithToken({required this.token});
  
  @override
  List<Object?> get props => [token];
}

class Logout extends AuthEvent {
  @override
  List<Object?> get props => [];
}

class RequestAgentList extends AuthEvent {
  @override
  List<Object?> get props => [];
}

class SelectAgent extends AuthEvent {
  final String agent;
  
  SelectAgent({required this.agent});
  
  @override
  List<Object?> get props => [agent];
}

// ========== States ==========

abstract class AuthState extends Equatable {
  @override
  List<Object?> get props => [];
}

class AuthInitial extends AuthState {
  @override
  List<Object?> get props => [];
}

class AuthLoading extends AuthState {
  @override
  List<Object?> get props => [];
}

class AuthConfigured extends AuthState {
  final String gatewayUrl;
  
  AuthConfigured({required this.gatewayUrl});
  
  @override
  List<Object?> get props => [gatewayUrl];
}

class AuthAuthenticated extends AuthState {
  final String gatewayUrl;
  final String token;
  final List<String> availableAgents;
  final String? selectedAgent;
  
  AuthAuthenticated({
    required this.gatewayUrl,
    required this.token,
    this.availableAgents = const [],
    this.selectedAgent,
  });
  
  @override
  List<Object?> get props => [gatewayUrl, token, availableAgents, selectedAgent];
}

class AuthUnauthenticated extends AuthState {
  final String? errorMessage;
  
  AuthUnauthenticated({this.errorMessage});
  
  @override
  List<Object?> get props => [errorMessage];
}

class AuthError extends AuthState {
  final String message;
  
  AuthError({required this.message});
  
  @override
  List<Object?> get props => [message];
}

// ========== BLoC ==========

class AuthBloc extends Bloc<AuthEvent, AuthState> {
  final Logger _logger = Logger();
  final WebSocketService _websocketService;
  final StorageService _storage = StorageService.getInstance();

  AuthBloc(this._websocketService) : super(AuthInitial()) {
    on<InitializeAuth>(_onInitialize);
    on<ConfigureGateway>(_onConfigureGateway);
    on<LoginWithToken>(_onLoginWithToken);
    on<Logout>(_onLogout);
    on<RequestAgentList>(_onRequestAgentList);
    on<SelectAgent>(_onSelectAgent);
    
    // 监听 WebSocket 状态
    _websocketService.statusStream.listen(_onConnectionStatusChanged);
    _websocketService.messageStream.listen(_onMessageReceived);
  }

  Future<void> _onInitialize(InitializeAuth event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    
    try {
      final gatewayUrl = _storage.getGatewayUrl();
      final token = await _storage.getToken();
      final selectedAgent = _storage.getSelectedAgent();
      
      if (gatewayUrl != null && token != null) {
        emit(AuthAuthenticated(
          gatewayUrl: gatewayUrl,
          token: token,
          selectedAgent: selectedAgent,
        ));
        
        // 尝试自动连接
        await _websocketService.connect(gatewayUrl: gatewayUrl, token: token);
      } else {
        emit(AuthUnauthenticated());
      }
    } catch (e) {
      _logger.e('Initialization failed: $e');
      emit(AuthUnauthenticated(errorMessage: '初始化失败：$e'));
    }
  }

  Future<void> _onConfigureGateway(ConfigureGateway event, Emitter<AuthState> emit) async {
    try {
      await _storage.saveGatewayUrl(event.gatewayUrl);
      emit(AuthConfigured(gatewayUrl: event.gatewayUrl));
      _logger.i('Gateway configured: ${event.gatewayUrl}');
    } catch (e) {
      emit(AuthError(message: '配置失败：$e'));
    }
  }

  Future<void> _onLoginWithToken(LoginWithToken event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    
    try {
      final gatewayUrl = _storage.getGatewayUrl();
      if (gatewayUrl == null) {
        _logger.e('Gateway URL not configured');
        emit(AuthUnauthenticated(errorMessage: '请先配置 Gateway 地址'));
        return;
      }
      
      _logger.i('Saving token and connecting to WebSocket: $gatewayUrl');
      
      // 保存 Token
      await _storage.saveToken(event.token);
      
      // 连接 WebSocket
      await _websocketService.connect(gatewayUrl: gatewayUrl, token: event.token);
      
      _logger.i('WebSocket connection established successfully');
      
      // 状态会在 _onConnectionStatusChanged 中更新
    } catch (e) {
      _logger.e('Login failed: $e');
      final errorMsg = '登录失败：$e\n\n请检查:\n1. Gateway 地址是否正确\n2. 网络连接是否正常\n3. Gateway 服务是否运行';
      emit(AuthUnauthenticated(errorMessage: errorMsg));
    }
  }

  Future<void> _onLogout(Logout event, Emitter<AuthState> emit) async {
    try {
      await _websocketService.disconnect();
      await _storage.deleteToken();
      emit(AuthUnauthenticated());
      _logger.i('Logged out');
    } catch (e) {
      emit(AuthError(message: '登出失败：$e'));
    }
  }

  void _onRequestAgentList(RequestAgentList event, Emitter<AuthState> emit) {
    if (_websocketService.isConnected) {
      _websocketService.requestNodeList();
      _logger.d('Agent list requested');
    }
  }

  void _onSelectAgent(SelectAgent event, Emitter<AuthState> emit) {
    _storage.saveSelectedAgent(event.agent);
    
    if (state is AuthAuthenticated) {
      final currentState = state as AuthAuthenticated;
      emit(AuthAuthenticated(
        gatewayUrl: currentState.gatewayUrl,
        token: currentState.token,
        availableAgents: currentState.availableAgents,
        selectedAgent: event.agent,
      ));
    }
    
    _logger.i('Agent selected: ${event.agent}');
  }

  void _onConnectionStatusChanged(ConnectionStatus status) {
    _logger.d('Connection status changed: $status');
    
    if (state is AuthAuthenticated) {
      final currentState = state as AuthAuthenticated;
      
      if (status == ConnectionStatus.disconnected) {
        emit(AuthUnauthenticated(errorMessage: '连接已断开'));
      }
    }
  }

  void _onMessageReceived(WebSocketMessage message) {
    _logger.d('Message received: ${message.type}');
    
    // 处理 Agent 列表响应
    if (message.type == 'node.list' && message.payload != null) {
      final agents = List<String>.from(message.payload!['nodes'] ?? []);
      
      if (state is AuthAuthenticated) {
        final currentState = state as AuthAuthenticated;
        emit(AuthAuthenticated(
          gatewayUrl: currentState.gatewayUrl,
          token: currentState.token,
          availableAgents: agents,
          selectedAgent: currentState.selectedAgent,
        ));
        _logger.i('Agent list received: $agents');
      }
    }
  }
}
