import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:image_picker/image_picker.dart';
import 'package:provider/provider.dart';
import 'package:flutter_animate/flutter_animate.dart';

import 'package:nutribot/services/api_service.dart';
import 'package:nutribot/services/image_service.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final ApiService _api = ApiService();
  final TextEditingController _controller = TextEditingController();
  final ScrollController _scrollController = ScrollController(); // 🔥 SCROLLING

  List<Map<String, dynamic>> messages = [];
  Uint8List? image;
  bool loading = false;

  @override
  void dispose() {
    _controller.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  // 🔥 AUTO-SCROLL HELPER
  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOutQuad,
        );
      }
    });
  }

  Future<void> pickImage() async {
    final picker = ImagePicker();
    final XFile? file = await picker.pickImage(source: ImageSource.gallery);

    if (file == null) return;

    setState(() => loading = true);

    final bytes = await ImageService.compressImage(file);

    setState(() {
      image = bytes;
      loading = false;
    });
  }

  void send() async {
    final text = _controller.text.trim();
    if (text.isEmpty && image == null) return;

    final auth = context.read<AuthProvider>();
    final usage = context.read<UsageProvider>();

    if (!auth.isAuthenticated) return;

    // 🔥 CHECK CREDITS
    final canUse = await usage.canUseChat();
    if (!canUse) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text("No daily chat queries remaining! Upgrade for more.", style: GoogleFonts.poppins()),
          backgroundColor: Colors.orange.shade700,
          behavior: SnackBarBehavior.floating,
        ),
      );
      return;
    }

    _controller.clear();

    setState(() {
      messages.add({"role": "user", "text": text, "image": image});
      loading = true;
    });
    _scrollToBottom();

    try {
      if (image != null) {
        final res = await _api.predictFood(
          imageBytes: image!, 
          userId: auth.user?.id
        );

        if (res.containsKey("error")) {
          setState(() {
            messages.add({"role": "bot", "text": "Something went wrong. Please try again."});
          });
        } else {
            // Extract numerical facts to give to the chat endpoint
            final n = res['nutrients'] ?? {};
            final scanData = "Calories: ${n['calories'] ?? 0}, Protein: ${n['protein'] ?? 0}, Carbs: ${n['carbs'] ?? 0}, Fat: ${n['fat'] ?? 0}, Sodium: ${n['sodium'] ?? 0}, Fiber: ${n['fiber'] ?? 0}";
            
            final scanChatRes = await _api.sendChatMessage(message: scanData, userId: auth.user?.id ?? "guest", intentHint: "scan_result");
            
            setState(() {
              messages.add({
                "role": "bot",
                "text": scanChatRes.reply
              });
            });
        }
        _scrollToBottom();
      }

      if (text.isNotEmpty) {
        final res = await _api.sendChatMessage(message: text, userId: auth.user?.id ?? "guest");
        
        String finalOutput = res.reply;
        if (finalOutput.trim() == "No response" || finalOutput.trim().isEmpty) {
            finalOutput = "Something went wrong. Please try again.";
        }

        setState(() {
          messages.add({
            "role": "bot",
            "text": finalOutput
          });
        });
        _scrollToBottom();
      }
      
      // Refresh usage to update calorie counts if needed
      await usage.useChat();
    } catch (e) {
      setState(() {
        messages.add({"role": "bot", "text": "Something went wrong. Please try again."});
      });
      _scrollToBottom();
    }

    setState(() {
      loading = false;
      image = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topCenter,
          end: Alignment.bottomCenter,
          colors: [
            Colors.green.shade50,
            Colors.white,
          ],
        ),
      ),
      child: Column(
        children: [
          // 🚀 CHAT AREA
          Expanded(
            child: messages.isEmpty
                ? _buildEmptyState()
                : ListView.builder(
                    controller: _scrollController,
                    padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
                    itemCount: messages.length,
                    itemBuilder: (context, i) {
                      return _buildChatBubble(messages[i]);
                    },
                  ),
          ),

          if (loading) 
            Padding(
              padding: const EdgeInsets.all(8.0),
              child: LinearProgressIndicator(
                backgroundColor: Colors.transparent,
                color: Colors.green.shade300,
              ),
            ),

          // 🏗️ MODENTIAL INPUT BAR
          _buildInputBar(),
        ],
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(Icons.chat_bubble_outline, size: 80, color: Colors.green.shade200),
          const SizedBox(height: 16),
          Text(
            "How can I help you today?",
            style: GoogleFonts.poppins(
              fontSize: 18,
              fontWeight: FontWeight.w600,
              color: Colors.green.shade600,
            ),
          ),
          const SizedBox(height: 8),
          Text(
            "Ask about nutritional risks or scan a photo.",
            style: GoogleFonts.poppins(color: Colors.grey.shade500),
          ),
        ],
      ),
    ).animate().fadeIn(duration: 600.ms).slideY(begin: 0.1, end: 0);
  }

  Widget _buildChatBubble(Map<String, dynamic> msg) {
    final isBot = msg["role"] == "bot";
    return Align(
      alignment: isBot ? Alignment.centerLeft : Alignment.centerRight,
      child: Container(
        margin: const EdgeInsets.symmetric(vertical: 6),
        padding: const EdgeInsets.all(14),
        constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.75),
        decoration: BoxDecoration(
          color: isBot ? Colors.white : Colors.green.shade600,
          borderRadius: BorderRadius.only(
            topLeft: const Radius.circular(16),
            topRight: const Radius.circular(16),
            bottomLeft: Radius.circular(isBot ? 4 : 16),
            bottomRight: Radius.circular(isBot ? 16 : 4),
          ),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, 4),
            )
          ],
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (msg["image"] != null)
              Padding(
                padding: const EdgeInsets.only(bottom: 8.0),
                child: ClipRRect(
                  borderRadius: BorderRadius.circular(12),
                  child: Image.memory(msg["image"] as Uint8List, fit: BoxFit.cover),
                ),
              ),
            Text(
              msg["text"] ?? "",
              style: GoogleFonts.poppins(
                color: isBot ? Colors.grey.shade800 : Colors.white,
                fontSize: 15,
                height: 1.4,
              ),
            ),
          ],
        ),
      ).animate().fadeIn(duration: 400.ms).slideX(begin: isBot ? -0.1 : 0.1, end: 0),
    );
  }

  Widget _buildInputBar() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white.withOpacity(0.9),
        borderRadius: const BorderRadius.only(
          topLeft: Radius.circular(24),
          topRight: Radius.circular(24),
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.04),
            blurRadius: 20,
            offset: const Offset(0, -10),
          )
        ],
      ),
      child: SafeArea(
        child: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (image != null)
              Container(
                margin: const EdgeInsets.only(bottom: 12),
                height: 70,
                width: double.infinity,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  children: [
                    Stack(
                      children: [
                        ClipRRect(
                          borderRadius: BorderRadius.circular(12),
                          child: Image.memory(image!, width: 70, height: 70, fit: BoxFit.cover),
                        ),
                        Positioned(
                          right: -2,
                          top: -2,
                          child: GestureDetector(
                            onTap: () => setState(() => image = null),
                            child: CircleAvatar(
                              radius: 12,
                              backgroundColor: Colors.red.shade400,
                              child: const Icon(Icons.close, size: 16, color: Colors.white),
                            ),
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            Row(
              children: [
                _buildInputIconButton(Icons.camera_alt_outlined, pickImage, Colors.green.shade600),
                const SizedBox(width: 8),
                Expanded(
                  child: Container(
                    decoration: BoxDecoration(
                      color: Colors.grey.shade100,
                      borderRadius: BorderRadius.circular(24),
                    ),
                    padding: const EdgeInsets.symmetric(horizontal: 16),
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: "Ask anything...",
                        hintStyle: GoogleFonts.poppins(color: Colors.grey.shade500),
                        border: InputBorder.none,
                      ),
                      style: GoogleFonts.poppins(fontSize: 15),
                      onSubmitted: (_) => send(),
                    ),
                  ),
                ),
                const SizedBox(width: 8),
                _buildInputIconButton(Icons.send_rounded, send, Colors.green.shade600, solid: true),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInputIconButton(IconData icon, VoidCallback onTap, Color color, {bool solid = false}) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: solid ? color : color.withOpacity(0.1),
          shape: BoxShape.circle,
        ),
        child: Icon(icon, color: solid ? Colors.white : color, size: 24),
      ),
    );
  }
}
