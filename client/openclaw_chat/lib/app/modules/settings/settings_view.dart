import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';

import '../../services/openim_service.dart';
import '../../services/storage_service.dart';

class SettingsController extends GetxController {
  final RxString serverIP = ''.obs;
  final RxString userId = ''.obs;
  final RxString nickname = ''.obs;
  
  @override
  void onInit() {
    super.onInit();
    loadUserInfo();
  }
  
  void loadUserInfo() {
    serverIP.value = StorageService.getServerIP() ?? '未设置';
    userId.value = StorageService.getUserId() ?? '未知';
    nickname.value = OpenIMService.to.currentUserNickname.value;
  }
  
  Future<void> logout() async {
    final confirm = await Get.dialog<bool>(
      AlertDialog(
        title: const Text('确认登出'),
        content: const Text('确定要退出登录吗？'),
        actions: [
          TextButton(
            onPressed: () => Get.back(result: false),
            child: const Text('取消'),
          ),
          TextButton(
            onPressed: () => Get.back(result: true),
            child: const Text('确定'),
          ),
        ],
      ),
    );
    
    if (confirm == true) {
      await OpenIMService.to.logout();
      Get.offAllNamed('/login');
    }
  }
  
  void showAbout() {
    showAboutDialog(
      context: Get.context!,
      applicationName: 'OpenClaw Chat',
      applicationVersion: '1.0.0',
      applicationLegalese: '© 2026 OpenClaw',
      children: [
        SizedBox(height: 16.h),
        const Text('基于 OpenIM 的智能助手聊天客户端'),
        SizedBox(height: 8.h),
        const Text('集成远程桌面管理功能'),
      ],
    );
  }
}

class SettingsView extends StatelessWidget {
  const SettingsView({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(SettingsController());
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('设置'),
      ),
      body: ListView(
        children: [
          // 用户信息
          Obx(() => ListTile(
            leading: CircleAvatar(
              child: Text(
                controller.nickname.value.isNotEmpty
                    ? controller.nickname.value[0].toUpperCase()
                    : '?',
              ),
            ),
            title: Text(controller.nickname.value),
            subtitle: Text('ID: ${controller.userId.value}'),
          )),
          
          const Divider(),
          
          // 服务器设置
          Obx(() => ListTile(
            leading: const Icon(Icons.dns_outlined),
            title: const Text('服务器地址'),
            subtitle: Text(controller.serverIP.value),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              // TODO: 编辑服务器地址
              Get.snackbar('提示', '服务器地址修改功能开发中');
            },
          )),
          
          const Divider(),
          
          // OpenClaw 设置
          ListTile(
            leading: const Icon(Icons.smart_toy_outlined),
            title: const Text('OpenClaw 设置'),
            subtitle: const Text('机器人配置、命令别名'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Get.snackbar('提示', 'OpenClaw 设置功能开发中');
            },
          ),
          
          ListTile(
            leading: const Icon(Icons.desktop_windows_outlined),
            title: const Text('远程桌面设置'),
            subtitle: const Text('noVNC 地址、端口配置'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Get.snackbar('提示', '远程桌面设置功能开发中');
            },
          ),
          
          const Divider(),
          
          // 通知设置
          ListTile(
            leading: const Icon(Icons.notifications_outlined),
            title: const Text('通知设置'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Get.snackbar('提示', '通知设置功能开发中');
            },
          ),
          
          // 外观设置
          ListTile(
            leading: const Icon(Icons.palette_outlined),
            title: const Text('外观'),
            subtitle: const Text('主题、字体大小'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Get.snackbar('提示', '外观设置功能开发中');
            },
          ),
          
          const Divider(),
          
          // 存储
          ListTile(
            leading: const Icon(Icons.storage_outlined),
            title: const Text('存储'),
            subtitle: const Text('缓存、聊天记录'),
            trailing: const Icon(Icons.chevron_right),
            onTap: () {
              Get.snackbar('提示', '存储设置功能开发中');
            },
          ),
          
          // 关于
          ListTile(
            leading: const Icon(Icons.info_outline),
            title: const Text('关于'),
            trailing: const Icon(Icons.chevron_right),
            onTap: controller.showAbout,
          ),
          
          const Divider(),
          
          // 登出
          Padding(
            padding: EdgeInsets.all(16.w),
            child: OutlinedButton.icon(
              onPressed: controller.logout,
              icon: const Icon(Icons.logout),
              label: const Text('退出登录'),
              style: OutlinedButton.styleFrom(
                foregroundColor: Colors.red,
                side: const BorderSide(color: Colors.red),
              ),
            ),
          ),
          
          // 版本信息
          Padding(
            padding: EdgeInsets.all(16.w),
            child: Text(
              'OpenClaw Chat v1.0.0\n基于 OpenIM SDK',
              style: TextStyle(
                fontSize: 12.sp,
                color: Colors.grey,
              ),
              textAlign: TextAlign.center,
            ),
          ),
        ],
      ),
    );
  }
}