// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/views/home_view.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'dart:ui'; // 상단 임포트 완료
import '../providers/stock_provider.dart';
import '../widgets/stock_card.dart';
import 'portfolio_view.dart';

class CurrentTabNotifier extends Notifier<int> {
  @override
  int build() => 0; 
  void updateTab(int index) => state = index;
}

final currentTabProvider = NotifierProvider<CurrentTabNotifier, int>(() => CurrentTabNotifier());

class HomeView extends ConsumerWidget {
  const HomeView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currentTab = ref.watch(currentTabProvider);
    final stocksAsync = ref.watch(stockListProvider);

    return Scaffold(
      backgroundColor: const Color(0xFF0D0D0E),
      body: Stack(
        children: [
          // 배경 글로우 (에러 수정: ImageFiltered 사용)
          Positioned(
            top: -50,
            left: -50,
            child: ImageFiltered(
              imageFilter: ImageFilter.blur(sigmaX: 50, sigmaY: 50),
              child: Container(
                width: 250,
                height: 250,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.orangeAccent.withOpacity(0.08),
                ),
              ),
            ),
          ),
          
          IndexedStack(
            index: currentTab,
            children: [
              _buildDiscoveryPage(stocksAsync, ref),
              const PortfolioView(),
            ],
          ),
        ],
      ),
      bottomNavigationBar: _buildBottomNav(currentTab, ref),
    );
  }

  Widget _buildDiscoveryPage(AsyncValue stocksAsync, WidgetRef ref) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: false,
        title: Padding(
          padding: const EdgeInsets.only(left: 8),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('SWING AI', style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.w900, letterSpacing: -1, color: Colors.white)),
              Text('실시간 시장 주도주 포착', style: TextStyle(fontSize: 12, color: Colors.grey.withOpacity(0.8), fontWeight: FontWeight.w500)),
            ],
          ),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Colors.white70),
            onPressed: () => ref.invalidate(stockListProvider),
          ),
          const SizedBox(width: 10),
        ],
      ),
      body: stocksAsync.when(
        data: (stocks) {
          if (stocks.isEmpty) {
            return _buildEmptyState();
          }
          return ListView.builder(
            padding: const EdgeInsets.only(top: 10, bottom: 40),
            itemCount: stocks.length,
            itemBuilder: (context, index) => StockCard(stock: stocks[index]),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator(color: Colors.orangeAccent, strokeWidth: 2)),
        error: (err, stack) => _buildErrorState(err),
      ),
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.search_off_rounded, size: 64, color: Colors.white.withOpacity(0.1)),
          const SizedBox(height: 16),
          const Text("현재 선별된 정예 종목이 없습니다.\n스캐너를 실행 중인지 확인해 주세요.", 
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey, height: 1.5)),
        ],
      ),
    );
  }

  Widget _buildErrorState(Object err) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.dns_outlined, color: Colors.redAccent, size: 48),
            const SizedBox(height: 16),
            Text("로컬 서버 연결 실패\n$err", textAlign: TextAlign.center, style: const TextStyle(color: Colors.grey)),
          ],
        ),
      ),
    );
  }

  Widget _buildBottomNav(int currentTab, WidgetRef ref) {
    return Container(
      decoration: BoxDecoration(
        border: Border(top: BorderSide(color: Colors.white.withOpacity(0.05), width: 1)),
      ),
      child: BottomNavigationBar(
        backgroundColor: const Color(0xFF0D0D0E),
        selectedItemColor: Colors.orangeAccent,
        unselectedItemColor: Colors.grey.withOpacity(0.5),
        currentIndex: currentTab,
        selectedLabelStyle: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 12),
        unselectedLabelStyle: GoogleFonts.outfit(fontSize: 12),
        type: BottomNavigationBarType.fixed,
        onTap: (index) => ref.read(currentTabProvider.notifier).updateTab(index),
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.explore_outlined), activeIcon: Icon(Icons.explore), label: 'Discovery'),
          BottomNavigationBarItem(icon: Icon(Icons.wallet_outlined), activeIcon: Icon(Icons.wallet), label: 'Portfolio'),
        ],
      ),
    );
  }
}
