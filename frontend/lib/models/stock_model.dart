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
  final StockGrade grade;
  final Map<String, double> targets;
  final DateTime timestamp; // 다시 추가

  StockModel({
    required this.code,
    required this.name,
    required this.market,
    required this.currentPrice,
    required this.volume,
    required this.sentimentScore,
    required this.newsSummary,
    required this.techReason,
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
      grade: _parseGrade(json['grade']),
      targets: (json['targets'] as Map<String, dynamic>).map(
        (key, value) => MapEntry(key, (value ?? 0.0).toDouble()),
      ),
      timestamp: _parseTimestamp(json['server_time']),
    );
  }

  static StockGrade _parseGrade(dynamic gradeStr) {
    if (gradeStr == 'S') return StockGrade.S;
    if (gradeStr == 'A') return StockGrade.A;
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
