// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/views/portfolio_view.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../providers/portfolio_provider.dart';
import '../providers/stock_provider.dart';
import '../models/holding_model.dart';

class PortfolioView extends ConsumerWidget {
  const PortfolioView({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final portfolio = ref.watch(portfolioProvider);
    final stocksAsync = ref.watch(stockListProvider);
    final currencyFormat = NumberFormat('#,###');

    return Scaffold(
      backgroundColor: Colors.transparent, // HomeView의 배경을 유지
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
        title: Text('내 투자 자산', style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 22)),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded, color: Colors.white70),
            onPressed: () => ref.invalidate(stockListProvider),
          ),
          const SizedBox(width: 10),
        ],
      ),

      body: Column(
        children: [
          // 1. 자산 대시보드 (Premium Card)
          _buildAssetDashboard(portfolio, currencyFormat),
          
          const SizedBox(height: 20),
          
          // 2. 보유 종목 리스트
          Expanded(
            child: portfolio.holdings.isEmpty 
              ? _buildEmptyPortfolio()
              : stocksAsync.when(
                  data: (realtimeStocks) => ListView.builder(
                    padding: const EdgeInsets.symmetric(horizontal: 20),
                    itemCount: portfolio.holdings.length,
                    itemBuilder: (context, index) {
                      final holding = portfolio.holdings[index];
                      // 실시간 가격 매칭 (수익률 계산용)
                      final currentStock = realtimeStocks.firstWhere(
                        (s) => s.code == holding.code,
                        orElse: () => realtimeStocks.isNotEmpty ? realtimeStocks.first : null as dynamic
                      );
                      final currentPrice = currentStock?.currentPrice ?? holding.buyPrice;
                      
                      return _buildHoldingCard(context, ref, holding, currentPrice, currencyFormat);
                    },
                  ),
                  loading: () => const Center(child: CircularProgressIndicator(color: Colors.orangeAccent)),
                  error: (e, _) => const Center(child: Text("시세 데이터를 불러올 수 없습니다.")),
                ),
          ),
        ],
      ),
    );
  }

  Widget _buildAssetDashboard(PortfolioState portfolio, NumberFormat format) {
    return Container(
      margin: const EdgeInsets.all(20),
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF2C2C2E), Color(0xFF1C1C1E)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(30),
        boxShadow: [BoxShadow(color: Colors.black.withOpacity(0.5), blurRadius: 20, offset: const Offset(0, 10))],
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text("사용 가능 예수금", style: TextStyle(color: Colors.grey, fontSize: 13)),
                  const SizedBox(height: 4),
                  Text("₩${format.format(portfolio.totalCash)}", style: GoogleFonts.outfit(fontSize: 24, fontWeight: FontWeight.bold, color: Colors.white)),
                ],
              ),
              _profitBadge(portfolio.realizedProfit, format),
            ],
          ),
          const SizedBox(height: 20),
          const Divider(color: Colors.white10),
          const SizedBox(height: 10),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _assetQuickInfo("보유 종목", "${portfolio.holdings.length}개"),
              _assetQuickInfo("투자 원금", "₩${format.format(10000000)}"),
            ],
          )
        ],
      ),
    );
  }

  Widget _profitBadge(double profit, NumberFormat format) {
    final bool isPlus = profit >= 0;
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
      decoration: BoxDecoration(
        color: (isPlus ? Colors.redAccent : Colors.blueAccent).withOpacity(0.1),
        borderRadius: BorderRadius.circular(15),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          const Text("누적 실현 손익", style: TextStyle(color: Colors.grey, fontSize: 10)),
          Text("${isPlus ? '+' : ''}${format.format(profit)}원", 
            style: GoogleFonts.outfit(color: isPlus ? Colors.redAccent : Colors.blueAccent, fontWeight: FontWeight.bold, fontSize: 16)),
        ],
      ),
    );
  }

  Widget _assetQuickInfo(String label, String value) {
    return Column(
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 12)),
        const SizedBox(height: 4),
        Text(value, style: GoogleFonts.outfit(color: Colors.white70, fontWeight: FontWeight.bold, fontSize: 16)),
      ],
    );
  }

  Widget _buildHoldingCard(BuildContext context, WidgetRef ref, HoldingModel holding, double currentPrice, NumberFormat format) {
    final profit = (currentPrice - holding.buyPrice) * holding.quantity;
    final profitPercent = ((currentPrice - holding.buyPrice) / holding.buyPrice) * 100;
    final bool isPlus = profit >= 0;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: const Color(0xFF1C1C1E),
        borderRadius: BorderRadius.circular(24),
        border: Border.all(color: Colors.white.withOpacity(0.05)),
      ),
      child: Column(
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(holding.name, style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                  Text("${holding.quantity}주 보유", style: const TextStyle(color: Colors.grey, fontSize: 12)),
                ],
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Text("₩${format.format(currentPrice * holding.quantity)}", 
                    style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.white)),
                  Text("${isPlus ? '+' : ''}${profitPercent.toStringAsFixed(2)}%", 
                    style: TextStyle(color: isPlus ? Colors.redAccent : Colors.blueAccent, fontSize: 14, fontWeight: FontWeight.bold)),
                ],
              )
            ],
          ),
          const SizedBox(height: 20),
          Row(
            children: [
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text("평균 매수가", style: TextStyle(color: Colors.grey, fontSize: 11)),
                    Text("₩${format.format(holding.buyPrice)}", style: const TextStyle(color: Colors.white70, fontSize: 13)),
                  ],
                ),
              ),
              ElevatedButton(
                onPressed: () {
                  ref.read(portfolioProvider.notifier).sellStock(holding.code, currentPrice);
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(
                      backgroundColor: isPlus ? Colors.redAccent : Colors.blueAccent,
                      content: Text("${holding.name} 전량 매도 완료! (수익: ${format.format(profit)}원)", 
                        style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white)),
                    )
                  );
                },
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.white.withOpacity(0.05),
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                  elevation: 0,
                  padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                ),
                child: const Text("매도하기", style: TextStyle(fontWeight: FontWeight.bold)),
              ),
            ],
          )
        ],
      ),
    );
  }

  Widget _buildEmptyPortfolio() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.account_balance_wallet_outlined, size: 64, color: Colors.white10),
          const SizedBox(height: 16),
          const Text("보유 중인 종목이 없습니다.\n'Discovery' 탭에서 AI 추천주를 확인해 보세요.", 
            textAlign: TextAlign.center,
            style: TextStyle(color: Colors.grey, height: 1.5)),
        ],
      ),
    );
  }
}
