# 测试错误分析报告

**时间**: 2026-04-01 08:48 CST

## 错误现象

所有 24 个测试用例失败，错误信息：
```
Error executing adbExec. Original error: 'Command '/opt/android-sdk/platform-tools/adb -P 5037 -s emulator-5554 shell 'settings delete global hidden_api_policy_pre_p_apps;settings delete global hidden_api_policy_p_apps;settings delete global hidden_api_policy'' exited with code 20'; Command output: cmd: Can't find service: settings
```

## 根本原因

Android 模拟器的 `settings` 服务无法访问，导致 UiAutomator2 无法配置隐藏 API 策略。

## 解决方案

1. ✅ 已重启 Android 模拟器
2. ⏳ 等待模拟器完全启动
3. ⏳ 重新执行测试

## 下一步

- 模拟器重启后自动继续测试
- 测试结果将自动提交到 GitHub
