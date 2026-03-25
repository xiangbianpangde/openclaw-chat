import 'package:flutter/material.dart';
import '../services/openim_service.dart';
import 'chat_screen.dart';
import 'login_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  bool _isLoggedIn = false;
  String _serverAddress = '';

  @override
  void initState() {
    super.initState();
    _checkLoginStatus();
  }

  Future<void> _checkLoginStatus() async {
    final isLoggedIn = await OpenIMService.isLoggedIn();
    final serverAddress = await OpenIMService.getServerAddress();
    setState(() {
      _isLoggedIn = isLoggedIn;
      _serverAddress = serverAddress;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('OpenClaw Chat'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => _showSettings(),
          ),
        ],
      ),
      body: _isLoggedIn
          ? ChatScreen(serverAddress: _serverAddress)
          : const LoginScreen(),
    );
  }

  void _showSettings() {
    showModalBottomSheet(
      context: context,
      builder: (context) => ListView(
        shrinkWrap: true,
        children: [
          const ListTile(
            leading: Icon(Icons.person),
            title: Text('账户设置'),
          ),
          ListTile(
            leading: const Icon(Icons.logout, color: Colors.red),
            title: const Text('退出登录', style: TextStyle(color: Colors.red)),
            onTap: () async {
              await OpenIMService.logout();
              setState(() {
                _isLoggedIn = false;
              });
              Navigator.pop(context);
            },
          ),
        ],
      ),
    );
  }
}
