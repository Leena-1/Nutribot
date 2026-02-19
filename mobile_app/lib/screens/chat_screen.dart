import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'package:nutribot/services/api_service.dart';
import 'package:nutribot/services/chat_history_service.dart';
import 'package:nutribot/providers/auth_provider.dart';
import 'package:nutribot/providers/usage_provider.dart';
import 'package:nutribot/widgets/auth_required_dialog.dart';
import 'package:nutribot/widgets/trial_limit_dialog.dart';
import 'package:nutribot/screens/chat_history_screen.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _api = ApiService();
  final _historyService = ChatHistoryService();
  final _controller = TextEditingController();
  final _scrollController = ScrollController();
  final List<Map<String, String>> _messages = [];
  bool _loading = false;

  @override
  void initState() {
    super.initState();
    _loadRecentHistory();
  }

  Future<void> _loadRecentHistory() async {
    final history = await _historyService.getRecentHistory(limit: 10);
    if (history.isNotEmpty && mounted) {
      setState(() {
        _messages.clear();
        for (var item in history) {
          _messages.add({'role': 'user', 'text': item['query'] ?? ''});
          _messages.add({'role': 'bot', 'text': item['response'] ?? ''});
        }
      });
      WidgetsBinding.instance.addPostFrameCallback((_) {
        if (_scrollController.hasClients) {
          _scrollController.animateTo(
            _scrollController.position.maxScrollExtent,
            duration: const Duration(milliseconds: 300),
            curve: Curves.easeOut,
          );
        }
      });
    }
  }

  void _send() async {
    final text = _controller.text.trim();
    if (text.isEmpty || _loading) return;

    final authProvider = context.read<AuthProvider>();
    final usageProvider = context.read<UsageProvider>();

    // Check authentication
    if (!authProvider.isAuthenticated) {
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => const AuthRequiredDialog(),
        );
      }
      return;
    }

    // Check usage limit
    final canUse = await usageProvider.canUseChat();
    if (!canUse) {
      if (mounted) {
        showDialog(
          context: context,
          builder: (context) => const TrialLimitDialog(),
        );
      }
      return;
    }

    final query = text;
    _controller.clear();
    setState(() {
      _messages.add({'role': 'user', 'text': query});
      _loading = true;
    });
    
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 200),
          curve: Curves.easeOut,
        );
      }
    });

    try {
      // Get user context for personalized responses
      final user = authProvider.user;
      final userContext = user?.getContextString();
      
      final result = await _api.chatQuery(query, userContext: userContext);
      final reply = (result['response'] ?? result['error'] ?? 'No response').toString();
      
      // Save to history
      if (!result.containsKey('error')) {
        await _historyService.saveMessage(
          query: query,
          response: reply,
          timestamp: DateTime.now(),
        );
        await usageProvider.useChat();
      }
      
      if (mounted) {
        setState(() {
          _messages.add({'role': 'bot', 'text': reply});
          _loading = false;
        });
        WidgetsBinding.instance.addPostFrameCallback((_) {
          if (_scrollController.hasClients) {
            _scrollController.animateTo(
              _scrollController.position.maxScrollExtent,
              duration: const Duration(milliseconds: 200),
              curve: Curves.easeOut,
            );
          }
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _messages.add({'role': 'bot', 'text': 'Error: $e'});
          _loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = context.watch<AuthProvider>();
    
    return Scaffold(
      appBar: AppBar(
        title: Text(
          'AI Nutrition Chat',
          style: GoogleFonts.poppins(fontWeight: FontWeight.w600),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.history),
            onPressed: () => Navigator.push(
              context,
              MaterialPageRoute(builder: (_) => const ChatHistoryScreen()),
            ),
            tooltip: 'Chat History',
          ),
        ],
      ),
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
            colors: [
              Colors.green.shade50,
              Colors.teal.shade50,
              Colors.blue.shade50,
            ],
          ),
        ),
        child: Column(
          children: [
            Expanded(
              child: _messages.isEmpty
                  ? Center(
                      child: Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Icon(
                            Icons.chat_bubble_outline,
                            size: 64,
                            color: Colors.grey.shade400,
                          ),
                          const SizedBox(height: 16),
                          Text(
                            'Start a conversation',
                            style: GoogleFonts.poppins(
                              fontSize: 18,
                              color: Colors.grey.shade600,
                            ),
                          ),
                          if (authProvider.user?.hasDisease == true)
                            Padding(
                              padding: const EdgeInsets.only(top: 8),
                              child: Text(
                                'Personalized for: ${authProvider.user?.diseaseType ?? ""}',
                                style: GoogleFonts.poppins(
                                  fontSize: 14,
                                  color: Colors.green.shade600,
                                  fontStyle: FontStyle.italic,
                                ),
                              ),
                            ),
                        ],
                      ),
                    )
                  : ListView.builder(
                      controller: _scrollController,
                      padding: const EdgeInsets.all(16),
                      itemCount: _messages.length,
                      itemBuilder: (_, i) {
                        final m = _messages[i];
                        final isUser = m['role'] == 'user';
                        return Align(
                          alignment: isUser ? Alignment.centerRight : Alignment.centerLeft,
                          child: Container(
                            margin: const EdgeInsets.only(bottom: 12),
                            constraints: BoxConstraints(
                              maxWidth: MediaQuery.of(context).size.width * 0.75,
                            ),
                            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                            decoration: BoxDecoration(
                              color: isUser
                                  ? Colors.green.shade600
                                  : Colors.white,
                              borderRadius: BorderRadius.circular(20),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                            child: Text(
                              m['text'] ?? '',
                              style: GoogleFonts.poppins(
                                color: isUser ? Colors.white : Colors.grey.shade800,
                                fontSize: 15,
                              ),
                            ),
                          ),
                        );
                      },
                    ),
            ),
            if (_loading)
              Padding(
                padding: const EdgeInsets.all(8),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    SizedBox(
                      width: 16,
                      height: 16,
                      child: CircularProgressIndicator(
                        strokeWidth: 2,
                        valueColor: AlwaysStoppedAnimation<Color>(Colors.green.shade600),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Text(
                      'AI is thinking...',
                      style: GoogleFonts.poppins(
                        color: Colors.grey.shade600,
                        fontSize: 14,
                      ),
                    ),
                  ],
                ),
              ),
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 10,
                    offset: const Offset(0, -2),
                  ),
                ],
              ),
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: 'Ask about food, nutrients...',
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(30),
                        ),
                        filled: true,
                        fillColor: Colors.grey.shade50,
                        contentPadding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                      ),
                      onSubmitted: (_) => _send(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.green.shade600,
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      onPressed: _send,
                      icon: const Icon(Icons.send, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
