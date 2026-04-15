import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';
import '../services/gemma_service.dart';

class StockAnalysisNotifier extends StateNotifier<AsyncValue<String>> {
  final GemmaService _gemmaService;

  StockAnalysisNotifier(this._gemmaService) : super(const AsyncValue.data(''));

  Future<void> analyzeStock(StockModel stock) async {
    state = const AsyncValue.loading();
    
    // 로컬 Gemma 모델을 위한 정교한 프롬프트 구성
    final prompt = """
주식 투자 전문가로서 아래 데이터를 분석하고 투자 의견을 한국어로 작성하세요.

[종목 정보]
- 종목명: ${stock.name} (${stock.code})
- 현재가: ${stock.currentPrice}원
- 거래대금: ${stock.volume}억
- 현재 추세: ${stock.maTrend}
- AI 감성 점수: ${(stock.sentimentScore * 100).toInt()}점

[주요 뉴스 요약]
${stock.newsSummary}

[기존 기술적 분석]
${stock.techReason}

[타겟 가격 전략]
- 매수가: ${stock.targets['buy']}원
- 익절가: ${stock.targets['take_profit']}원
- 손절가: ${stock.targets['stop_loss']}원

분석 요청 사항:
1. 위 데이터들을 종합하여 현재 구간이 매수하기에 매력적인지 전문가적 관점에서 평가해주세요.
2. 향후 3일~일주일 내의 예상 흐름과 투자자가 구체적으로 취해야 할 행동 요령을 설명하세요.
3. 이 종목의 가장 큰 리스크 요인은 무엇인지 지적하세요.

답변 형식:
- 아주 전문적이고 설득력 있는 어조로 작성하세요.
- 불필요한 서론은 생략하고 바로 본론으로 들어가세요.
- 전체 답변은 300자 내외로 한국어로 작성하세요.
""";

    try {
      final response = await _gemmaService.getResponse(prompt);
      state = AsyncValue.data(response);
    } catch (e, stack) {
      state = AsyncValue.error(e, stack);
    }
  }
}

final stockAnalysisProvider = StateNotifierProvider<StockAnalysisNotifier, AsyncValue<String>>((ref) {
  final gemmaService = ref.watch(gemmaServiceProvider);
  return StockAnalysisNotifier(gemmaService);
});
