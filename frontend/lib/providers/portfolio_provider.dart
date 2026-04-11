// Project: Swing
// Agent 1: The Architect
// Path: frontend/lib/providers/portfolio_provider.dart

import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/holding_model.dart';

class PortfolioState {
  final List<HoldingModel> holdings;
  final double totalCash;      // 사용 가능 현금
  final double realizedProfit; // 확정된 누적 수익금

  PortfolioState({
    required this.holdings,
    required this.totalCash,
    required this.realizedProfit,
  });

  PortfolioState copyWith({
    List<HoldingModel>? holdings,
    double? totalCash,
    double? realizedProfit,
  }) {
    return PortfolioState(
      holdings: holdings ?? this.holdings,
      totalCash: totalCash ?? this.totalCash,
      realizedProfit: realizedProfit ?? this.realizedProfit,
    );
  }
}

class PortfolioNotifier extends Notifier<PortfolioState> {
  @override
  PortfolioState build() {
    return PortfolioState(
      holdings: [],
      totalCash: 10000000, // 초기 자본 1,000만원
      realizedProfit: 0,
    );
  }

  // 📈 주식 매수 로직
  void buyStock(String code, String name, double price, int quantity) {
    final cost = price * quantity;
    if (state.totalCash < cost) return;

    final newHolding = HoldingModel(
      code: code,
      name: name,
      buyPrice: price,
      quantity: quantity,
      buyTimestamp: DateTime.now(),
    );

    state = state.copyWith(
      holdings: [...state.holdings, newHolding],
      totalCash: state.totalCash - cost,
    );
  }

  // 📉 주식 매도 로직 (전량 매도)
  void sellStock(String code, double currentPrice) {
    // 해당 종목 찾기
    final holdingIndex = state.holdings.indexWhere((h) => h.code == code);
    if (holdingIndex == -1) return;

    final holding = state.holdings[holdingIndex];
    final sellValue = currentPrice * holding.quantity;
    final profit = (currentPrice - holding.buyPrice) * holding.quantity;

    // 리스트에서 제거
    final newList = [...state.holdings];
    newList.removeAt(holdingIndex);

    state = state.copyWith(
      holdings: newList,
      totalCash: state.totalCash + sellValue,
      realizedProfit: state.realizedProfit + profit,
    );
  }
}

final portfolioProvider = NotifierProvider<PortfolioNotifier, PortfolioState>(() => PortfolioNotifier());
