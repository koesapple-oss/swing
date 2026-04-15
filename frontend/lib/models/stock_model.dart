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
  final double sentimentScore;
  final String newsSummary;
  final String techReason;
  final String maTrend; 
  final StockGrade grade;
  final Map<String, double> targets;
  final DateTime timestamp;

  StockModel({
    required this.code,
    required this.name,
    required this.market,
    required this.currentPrice,
    required this.volume,
    required this.sentimentScore,
    required this.newsSummary,
    required this.techReason,
    required this.maTrend,
    required this.grade,
    required this.targets,
    required this.timestamp,
  });

  factory StockModel.fromJson(Map<String, dynamic> json) {
    return StockModel(
      code: json['code'] ?? '',
      name: json['name'] ?? '',
      market: json['market'] ?? '',
      currentPrice: (json['current_price'] ?? 0.0).toDouble(),
      volume: (json['volume'] ?? 0.0).toDouble(),
      sentimentScore: (json['sentiment_score'] ?? 0.0).toDouble(),
      newsSummary: json['news_summary'] ?? '',
      techReason: json['tech_reason'] ?? json['ext_reason'] ?? '',
      maTrend: json['ma_trend'] ?? '데이터 없음',
      grade: _parseGrade(json['grade']),
      targets: (json['targets'] as Map<String, dynamic>? ?? {}).map(
        (key, value) => MapEntry(key, (value ?? 0.0).toDouble()),
      ),
      timestamp: _parseTimestamp(json['server_time']),
    );
  }

  static StockGrade _parseGrade(dynamic gradeStr) {
    if (gradeStr is String) {
      switch (gradeStr) {
        case 'S': return StockGrade.S;
        case 'A': return StockGrade.A;
        default: return StockGrade.B;
      }
    }
    return StockGrade.B;
  }

  static DateTime _parseTimestamp(dynamic time) {
    if (time == null) return DateTime.now();
    if (time is num) {
      return DateTime.fromMillisecondsSinceEpoch((time * 1000).toInt());
    }
    return DateTime.now();
  }
}
