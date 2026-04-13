// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/models/stock_model.dart

enum StockGrade { S, A, B }

class StockModel {
  final String code;
  final String name;
  final String market;
  final double currentPrice;
  final double volume; 
  final String maTrend;
  final double sentimentScore;
  final String newsSummary;
  final String techReason; 
  final String extReason;  
  final StockGrade grade;
  final Map<String, double> targets;
  final DateTime timestamp;

  StockModel({
    required this.code,
    required this.name,
    required this.market,
    required this.currentPrice,
    required this.volume,
    required this.maTrend,
    required this.sentimentScore,
    required this.newsSummary,
    required this.techReason,
    required this.extReason,
    required this.grade,
    required this.targets,
    required this.timestamp,
  });

  factory StockModel.fromMap(Map<String, dynamic> data) {
    return StockModel(
      code: (data['code'] ?? '').toString(),
      name: (data['name'] ?? '').toString(),
      market: (data['market'] ?? '').toString(),
      currentPrice: (data['current_price'] ?? 0).toDouble(),
      volume: (data['volume'] ?? 0).toDouble(),
      maTrend: (data['ma_trend'] ?? '').toString(),
      sentimentScore: (data['sentiment_score'] ?? 0).toDouble(),
      newsSummary: (data['news_summary'] ?? '').toString(),
      techReason: (data['tech_reason'] ?? '기술적 분석 중...').toString(),
      extReason: (data['ext_reason'] ?? '대외 전략 분석 중...').toString(),
      grade: _parseGrade(data['grade']?.toString()),
      targets: Map<String, dynamic>.from(data['targets'] ?? {}).map(
        (key, value) => MapEntry(key, (value ?? 0).toDouble())
      ),
      timestamp: _parseTimestamp(data['server_time']),
    );
  }

  static DateTime _parseTimestamp(dynamic timestamp) {
    if (timestamp == null) return DateTime.now();
    if (timestamp is num) {
      // 서버에서 온 유닉스 타임스탬프 (초 단위)
      return DateTime.fromMillisecondsSinceEpoch((timestamp * 1000).toInt());
    }
    if (timestamp is String) return DateTime.tryParse(timestamp) ?? DateTime.now();
    return DateTime.now();
  }


  static StockGrade _parseGrade(String? grade) {
    if (grade == null) return StockGrade.B;
    switch (grade) {
      case 'S': return StockGrade.S;
      case 'A': return StockGrade.A;
      default: return StockGrade.B;
    }
  }
}
