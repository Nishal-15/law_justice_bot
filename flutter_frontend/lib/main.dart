import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';
import 'package:speech_to_text/speech_to_text.dart' as stt;

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Law & Justice Chatbot', 
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: ChatPage(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class ChatPage extends StatefulWidget {
  @override
  _ChatPageState createState() => _ChatPageState();
}

class _ChatPageState extends State<ChatPage> {
  List<Map<String, String>> messages = [];
  final TextEditingController _controller = TextEditingController();
  late stt.SpeechToText _speech;
  bool isListening = false;

  @override
  void initState() {
    super.initState();
    _speech = stt.SpeechToText();
  }

  void sendMessage(String text) async {
    if (text.isEmpty) return;
    setState(() {
      messages.add({"role": "user", "text": text});
    });

    _controller.clear();
    final response = await http.post(
      Uri.parse("http://192.168.74.161/chat"), // localhost for emulator
      headers: {"Content-Type": "application/json"},
      body: jsonEncode({"message": text, "language": "en"}),
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      setState(() {
        messages.add({"role": "bot", "text": data["answer"]});
      });
    } else {
      setState(() {
        messages.add({"role": "bot", "text": "⚠️ Failed to get a response."});
      });
    }
  }

  void startListening() async {
    bool available = await _speech.initialize();
    if (available) {
      setState(() => isListening = true);
      _speech.listen(onResult: (result) {
        _controller.text = result.recognizedWords;
      });
    }
  }

  void stopListening() {
    setState(() => isListening = false);
    _speech.stop();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("⚖️ Law & Justice Chatbot")),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              itemCount: messages.length,
              itemBuilder: (context, index) {
                final msg = messages[index];
                return Align(
                  alignment: msg['role'] == 'user'
                      ? Alignment.centerRight
                      : Alignment.centerLeft,
                  child: Container(
                    margin: EdgeInsets.all(8),
                    padding: EdgeInsets.all(12),
                    decoration: BoxDecoration(
                      color: msg['role'] == 'user'
                          ? Colors.blue[100]
                          : Colors.grey[300],
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(msg['text'] ?? ''),
                  ),
                );
              },
            ),
          ),
          Row(
            children: [
              IconButton(
                icon: Icon(isListening ? Icons.mic_off : Icons.mic),
                onPressed: () {
                  isListening ? stopListening() : startListening();
                },
              ),
              Expanded(
                child: TextField(
                  controller: _controller,
                  onChanged: (value) {
                    if (value.trim().endsWith('.')) {
                      sendMessage(value.trim());
                    }
                  },
                  decoration: InputDecoration(
                    hintText: "Ask your legal query...",
                    contentPadding: EdgeInsets.symmetric(horizontal: 12),
                  ),
                ),
              ),
              IconButton(
                icon: Icon(Icons.send),
                onPressed: () => sendMessage(_controller.text.trim()),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
