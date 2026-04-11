import 'package:flutter/material.dart';
import 'package:flutter_screenutil/flutter_screenutil.dart';
import 'package:get/get.dart';

import '../../services/openim_service.dart';
import '../../services/storage_service.dart';

class LoginController extends GetxController {
  final TextEditingController userIdController = TextEditingController();
  final TextEditingController tokenController = TextEditingController();
  final TextEditingController serverController = TextEditingController();
  
  final RxBool isLoading = false.obs;
  final RxBool obscureToken = true.obs;
  
  @override
  void onInit() {
    super.onInit();
    // 加载保存的服务器 IP
    serverController.text = StorageService.getServerIP() ?? '';
  }
  
  Future<void> login() async {
    final userId = userIdController.text.trim();
    final token = tokenController.text.trim();
    final serverIP = serverController.text.trim();
    
    if (userId.isEmpty || token.isEmpty || serverIP.isEmpty) {
      Get.snackbar('错误', '请填写所有字段');
      return;
    }
    
    isLoading.value = true;
    
    try {
      // 保存服务器 IP
      await StorageService.saveServerIP(serverIP);
      
      // 执行登录
      final success = await OpenIMService.to.login(
        userId: userId,
        token: token,
      );
      
      if (success) {
        Get.offAllNamed('/chat-list');
      } else {
        Get.snackbar('错误', '登录失败，请检查用户名和密码');
      }
    } catch (e) {
      Get.snackbar('错误', '登录失败: $e');
    } finally {
      isLoading.value = false;
    }
  }
  
  void toggleTokenVisibility() {
    obscureToken.value = !obscureToken.value;
  }
  
  @override
  void onClose() {
    userIdController.dispose();
    tokenController.dispose();
    serverController.dispose();
    super.onClose();
  }
}

class LoginView extends StatelessWidget {
  const LoginView({super.key});

  @override
  Widget build(BuildContext context) {
    final controller = Get.put(LoginController());
    
    return Scaffold(
      body: SafeArea(
        child: SingleChildScrollView(
          padding: EdgeInsets.symmetric(horizontal: 24.w),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              SizedBox(height: 80.h),
              
              // Logo
              Icon(
                Icons.chat_bubble_outline_rounded,
                size: 80.sp,
                color: Theme.of(context).colorScheme.primary,
              ),
              SizedBox(height: 16.h),
              
              // 标题
              Text(
                'OpenClaw Chat',
                style: TextStyle(
                  fontSize: 28.sp,
                  fontWeight: FontWeight.bold,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 8.h),
              
              Text(
                '智能助手聊天客户端',
                style: TextStyle(
                  fontSize: 14.sp,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
              SizedBox(height: 60.h),
              
              // 服务器地址
              TextField(
                controller: controller.serverController,
                decoration: InputDecoration(
                  labelText: '服务器地址',
                  hintText: '例如: 192.168.1.100',
                  prefixIcon: const Icon(Icons.dns_outlined),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                ),
                keyboardType: TextInputType.url,
              ),
              SizedBox(height: 20.h),
              
              // 用户 ID
              TextField(
                controller: controller.userIdController,
                decoration: InputDecoration(
                  labelText: '用户 ID',
                  hintText: '请输入用户 ID',
                  prefixIcon: const Icon(Icons.person_outline),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                ),
                keyboardType: TextInputType.text,
              ),
              SizedBox(height: 20.h),
              
              // Token
              Obx(() => TextField(
                controller: controller.tokenController,
                decoration: InputDecoration(
                  labelText: 'Token',
                  hintText: '请输入登录 Token',
                  prefixIcon: const Icon(Icons.key_outlined),
                  suffixIcon: IconButton(
                    icon: Icon(
                      controller.obscureToken.value
                          ? Icons.visibility_off_outlined
                          : Icons.visibility_outlined,
                    ),
                    onPressed: controller.toggleTokenVisibility,
                  ),
                  border: OutlineInputBorder(
                    borderRadius: BorderRadius.circular(12.r),
                  ),
                ),
                obscureText: controller.obscureToken.value,
              )),
              SizedBox(height: 40.h),
              
              // 登录按钮
              Obx(() => SizedBox(
                height: 50.h,
                child: ElevatedButton(
                  onPressed: controller.isLoading.value
                      ? null
                      : controller.login,
                  style: ElevatedButton.styleFrom(
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12.r),
                    ),
                  ),
                  child: controller.isLoading.value
                      ? const SizedBox(
                          width: 24,
                          height: 24,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        )
                      : Text(
                          '登录',
                          style: TextStyle(fontSize: 16.sp),
                        ),
                ),
              )),
              SizedBox(height: 20.h),
              
              // 提示
              Text(
                '提示：用户 ID 和 Token 需要从服务器管理后台获取',
                style: TextStyle(
                  fontSize: 12.sp,
                  color: Colors.grey,
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        ),
      ),
    );
  }
}