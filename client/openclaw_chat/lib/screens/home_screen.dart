import 'package:flutter/material.dart';
import 'login_screen.dart';
import 'chat_screen.dart';
import 'browser_screen.dart';
import 'remote_desktop_screen.dart';

/// 主页面 - 底部导航
class HomeScreen extends StatefulWidget {
  final String serverUrl;
  final String agentId;

  const HomeScreen({
    super.key,
    required this.serverUrl,
    required this.agentId,
  });

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  final List<Widget> _screens = [];

  @override
  void initState() {
    super.initState();
    _screens.addAll([
      ChatScreen(serverUrl: widget.serverUrl, agentId: widget.agentId),
      const BrowserScreen(),
      const RemoteDesktopScreen(),
    ]);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: NavigationBar(
        selectedIndex: _selectedIndex,
        onDestinationSelected: (index) {
          setState(() => _selectedIndex = index);
        },
        destinations: const [
          NavigationDestination(
            icon: Icon(Icons.chat_bubble_outline),
            label: '聊天',
            selectedIcon: Icon(Icons.chat_bubble),
          ),
          NavigationDestination(
            icon: Icon(Icons.language),
            label: '浏览器',
            selectedIcon: Icon(Icons.language),
          ),
          NavigationDestination(
            icon: Icon(Icons.desktop_windows_outlined),
            label: '远程桌面',
            selectedIcon: Icon(Icons.desktop_windows),
          ),
        ],
      ),
    );
  }
}
