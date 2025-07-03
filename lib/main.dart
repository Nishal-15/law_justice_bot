import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

void main() {
  runApp(const LawChatbotApp());
}

class LawChatbotApp extends StatelessWidget {
  const LawChatbotApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Law & Justice Chatbot',
      theme: ThemeData(
        primarySwatch: Colors.deepPurple,
      ),
      home: const WebViewHome(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class WebViewHome extends StatefulWidget {
  const WebViewHome({super.key});

  @override
  State<WebViewHome> createState() => _WebViewHomeState();
}

class _WebViewHomeState extends State<WebViewHome> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..loadRequest(Uri.parse('http://192.168.74.161/chat')) // Localhost for emulator
      ..setJavaScriptMode(JavaScriptMode.unrestricted);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('⚖️ Law & Justice Chatbot'),
      ),
      body: WebViewWidget(controller: _controller),
    );
  }
}
