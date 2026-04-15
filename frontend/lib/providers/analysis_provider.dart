import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';
import '../services/gemma_service.dart';

// Riverpod 3.0의 AsyncNotifier를 사용하여 상태 관리 최신화
class StockAnalysisNotifier extends AsyncNotifier<String> {
  @override
  FutureOr<String> build() {
    return ''; // 초기 상태
  }

  Future<void> analyzeStock(StockModel stock) async {
    state = const AsyncLoading();
    
    final gemmaState = ref.read(gemmaServiceProvider);
    if (!gemmaState.isInitialized) {
      state = const AsyncData("사용 전 AI 모델 활성화가 필요합니다.");
      return;
    }

    final gemmaNotifier = ref.read(gemmaServiceProvider.notifier);
    
    final prompt = """
주식 투자 전문가로서 아래 데이터를 분석하고 한국어로 답변하세요.
종목명: ${stock.name} (${stock.code})
현재가: ${stock.currentPrice}원
추세: ${stock.maTrend}
뉴스 요약: ${stock.newsSummary}

전문가적 투자 매력도를 300자 이내로 제안하세요.
""";

    state = await AsyncValue.guard(() async {
      return await gemmaNotifier.getResponse(prompt);
    });
  }
}

// 프로바이더 정의
final stockAnalysisProvider = AsyncNotifierProvider.autoDispose<StockAnalysisNotifier, String>(() {
  return StockAnalysisNotifier();
});
