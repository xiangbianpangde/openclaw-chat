import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../services/storage_service.dart';

class RemoteDesktopController extends GetxController {
  late WebViewController webViewController;
  
  final RxString serverIP = ''.obs;
  final RxBool isLoading = true.obs;
  final RxString errorMessage = ''.obs;
  
  // noVNC 默认端口
  static const int novncPort = 6080;
  
  @override
  void onInit() {
    super.onInit();
    _initWebView();
  }
  
  void _initWebView() {
    serverIP.value = StorageService.getServerIP() ?? '';
    
    if (serverIP.isEmpty) {
      errorMessage.value = '未配置服务器地址';
      return;
    }
    
    final novncUrl = 'http://${serverIP.value}:$novncPort/vnc.html';
    
    webViewController = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onPageStarted: (_) => isLoading.value = true,
          onPageFinished: (_) => isLoading.value = false,
          onWebResourceError: (error) {
            errorMessage.value = '连接失败: ${error.description}';
            isLoading.value = false;
          },
        ),
      )
      ..loadRequest(Uri.parse(novncUrl));
  }
  
  void reload() {
    errorMessage.value = '';
    _initWebView();
  }
  
  // 快捷操作（发送到 OpenClaw）
  void sendCommand(String command) {
    // TODO: 通过 OpenIM 发送命令到 OpenClaw
    Get.snackbar('命令', '已发送: $command');
  }
}

class RemoteDesktopView extends StatelessWidget {
  const RemoteDesktopView({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(RemoteDesktopController());
    
    return Scaffold(
      appBar: AppBar(
        title: const Text('远程桌面'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: controller.reload,
            tooltip: '重新连接',
          ),
        ],
      ),
      body: Obx(() {
        if (controller.errorMessage.isNotEmpty) {
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.error_outline,
                  size: 64.sp,
                  color: Colors.red,
                ),
                SizedBox(height: 16.h),
                Text(
                  controller.errorMessage.value,
                  style: TextStyle(fontSize: 16.sp),
                  textAlign: TextAlign.center,
                ),
                SizedBox(height: 24.h),
                ElevatedButton.icon(
                  onPressed: controller.reload,
                  icon: const Icon(Icons.refresh),
                  label: const Text('重试'),
                ),
              ],
            ),
          );
        }
        
        return Stack(
          children: [
            WebViewWidget(controller: controller.webViewController),
            
            // 加载指示器
            if (controller.isLoading.value)
              const Center(child: CircularProgressIndicator()),
          ],
        );
      }),
      bottomNavigationBar: Container(
        padding: EdgeInsets.all(12.w),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceEvenly,
          children: [
            _QuickAction(
              icon: Icons.qr_code_scanner,
              label: '扫码登录',
              onTap: () => controller.sendCommand('/scan'),
            ),
            _QuickAction(
              icon: Icons.power_settings_new,
              label: '重启服务',
              onTap: () => controller.sendCommand('/restart'),
            ),
            _QuickAction(
              icon: Icons.terminal,
              label: '终端',
              onTap: () => controller.sendCommand('/terminal'),
            ),
            _QuickAction(
              icon: Icons.settings,
              label: '设置',
              onTap: () => Get.toNamed('/settings'),
            ),
          ],
        ),
      ),
    );
  }
}

class _QuickAction extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  
  const _QuickAction({
    required this.icon,
    required this.label,
    required this.onTap,
  });
  
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(8.r),
      child: Padding(
        padding: EdgeInsets.all(8.w),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 24.sp),
            SizedBox(height: 4.h),
            Text(label, style: TextStyle(fontSize: 12.sp)),
          ],
        ),
      ),
    );
  }
}