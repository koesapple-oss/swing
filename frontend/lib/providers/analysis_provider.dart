import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';
import '../services/gemma_service.dart';

// Riverpod 3.0의 AsyncNotifier를 사용하여 상태 관리 최신화
class StockAnalysisNotifier extends AutoDisposeAsyncNotifier<String> {
  @override
  FutureOr<String> build() {
    return ''; // 초기 상태는 빈 문자열
  }

  Future<void> analyzeStock(StockModel stock) async {
    // 로딩 상태 시작
    state = const AsyncLoading();
    
    final gemmaService = ref.read(gemmaServiceProvider.notifier);
    
    // 로컬 Gemma 모델용 프롬프트
    final prompt = """
주식 투자 전문가로서 아래 데이터를 분석하고 한국어로 답변하세요.
종목명: ${stock.name} (${stock.code})
현재가: ${stock.currentPrice}원
추세: ${stock.maTrend}
뉴스 요약: ${stock.newsSummary}

기존 분석 기반으로 투자 매력도와 리스크를 300자 이내로 제안하세요.
""";

    // 추론 수행 및 상태 업데이트
    state = await AsyncValue.guard(() async {
      return await gemmaService.getResponse(prompt);
    });
  }
}

// 프로바이더 정의 (Riverpod 3.0 NotifierProvider)
final stockAnalysisProvider = AsyncNotifierProvider.autoDispose<StockAnalysisNotifier, String>(() {
  return StockAnalysisNotifier();
});
