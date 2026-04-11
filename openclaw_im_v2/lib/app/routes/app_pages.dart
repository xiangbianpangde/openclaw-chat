import 'package:get/get.dart';

import '../modules/login/login_view.dart';
import '../modules/chat/chat_list_view.dart';
import '../modules/chat/chat_view.dart';
import '../modules/remote_desktop/remote_desktop_view.dart';
import '../modules/settings/settings_view.dart';

abstract class Routes {
  static const login = '/login';
  static const chatList = '/chat-list';
  static const chat = '/chat';
  static const remoteDesktop = '/remote-desktop';
  static const settings = '/settings';
}

class AppPages {
  static const initial = Routes.login;

  static final routes = [
    GetPage(
      name: Routes.login,
      page: () => const LoginView(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: Routes.chatList,
      page: () => const ChatListView(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: Routes.chat,
      page: () => const ChatView(),
      transition: Transition.rightToLeft,
    ),
    GetPage(
      name: Routes.remoteDesktop,
      page: () => const RemoteDesktopView(),
      transition: Transition.fadeIn,
    ),
    GetPage(
      name: Routes.settings,
      page: () => const SettingsView(),
      transition: Transition.rightToLeft,
    ),
  ];
}