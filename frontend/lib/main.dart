// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/main.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'views/home_view.dart';

void main() {
  // 🔥 Flutter 위젯 바인딩 초기화
  WidgetsFlutterBinding.ensureInitialized();

  runApp(
    const ProviderScope(
      child: SwingApp(),
    ),
  );
}

class SwingApp extends StatelessWidget {
  const SwingApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Swing Trading AI',
      debugShowCheckedModeBanner: false,
      theme: ThemeData(
        brightness: Brightness.dark,
        scaffoldBackgroundColor: const Color(0xFF0A0A0A),
        textTheme: GoogleFonts.outfitTextTheme(
          ThemeData.dark().textTheme,
        ),
      ),
      home: const HomeView(),
    );
  }
}
