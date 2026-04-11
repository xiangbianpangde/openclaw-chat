import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:openclaw_im_client/app/app.dart';

void main() {
  testWidgets('App smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const OpenClawApp());

    // Verify that the app shows the login screen title.
    expect(find.text('OpenClaw IM'), findsOneWidget);
    expect(find.text('v2.0'), findsOneWidget);
  });
}
