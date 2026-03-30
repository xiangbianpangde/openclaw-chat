import 'package:flutter/material.dart';

/// 远程桌面页面 - VNC/RDP 远程连接功能
class RemoteDesktopScreen extends StatefulWidget {
  const RemoteDesktopScreen({super.key});

  @override
  State<RemoteDesktopScreen> createState() => _RemoteDesktopScreenState();
}

class _RemoteDesktopScreenState extends State<RemoteDesktopScreen> {
  final List<Map<String, String>> _connections = [
    {
      'name': '开发服务器',
      'host': '38.226.195.166',
      'port': '5901',
      'protocol': 'VNC',
    },
    {
      'name': '家庭电脑',
      'host': '192.168.1.100',
      'port': '3389',
      'protocol': 'RDP',
    },
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('远程桌面'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: _addConnection,
            tooltip: '添加连接',
          ),
        ],
      ),
      body: _connections.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.desktop_windows_outlined,
                    size: 80,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    '暂无连接',
                    style: Theme.of(context).textTheme.titleLarge,
                  ),
                  const SizedBox(height: 8),
                  Text(
                    '点击右上角 + 添加远程桌面连接',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _connections.length,
              itemBuilder: (context, index) {
                final conn = _connections[index];
                return Card(
                  margin: const EdgeInsets.only(bottom: 12),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: conn['protocol'] == 'VNC'
                          ? Colors.blue
                          : Colors.green,
                      child: Icon(
                        Icons.computer,
                        color: Colors.white,
                      ),
                    ),
                    title: Text(conn['name']!),
                    subtitle: Text('${conn['host']}:${conn['port']}'),
                    trailing: Chip(
                      label: Text(
                        conn['protocol']!,
                        style: const TextStyle(
                          color: Colors.white,
                          fontSize: 12,
                        ),
                      ),
                      backgroundColor: conn['protocol'] == 'VNC'
                          ? Colors.blue
                          : Colors.green,
                    ),
                    onTap: () => _connect(conn),
                  ),
                );
              },
            ),
    );
  }

  void _addConnection() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('添加连接'),
        content: const Text('远程桌面连接功能开发中'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('确定'),
          ),
        ],
      ),
    );
  }

  void _connect(Map<String, String> connection) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('连接到 ${connection['name']}'),
        content: Text(
          '正在连接 ${connection['host']}:${connection['port']}...\n\n'
          'VNC/RDP 客户端集成开发中',
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('取消'),
          ),
        ],
      ),
    );
  }
}
