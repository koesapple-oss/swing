// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/providers/stock_provider.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';

// 🔥 로컬 API 서버(localhost:8000)를 실시간으로 폴링합니다.
final stockListProvider = StreamProvider<List<StockModel>>((ref) async* {
  const String url = "http://localhost:8000/recommendations";
  
  // 2초마다 로컬 서버에 새로운 시세를 물어봅니다. (비용 0원!)
  yield* Stream.periodic(const Duration(seconds: 2), (_) async {
    try {
      final response = await http.get(Uri.parse(url));
      if (response.statusCode == 200) {
        final List<dynamic> data = json.decode(response.body);
        
        final list = data.map((json) => StockModel.fromMap(json)).toList();
        
        // 정렬: S급 우선 -> AI 점수 내림차순
        list.sort((a, b) {
          if (a.grade != b.grade) {
            if (a.grade == StockGrade.S) return -1;
            if (b.grade == StockGrade.S) return 1;
          }
          return b.sentimentScore.compareTo(a.sentimentScore);
        });
        
        return list;
      }
    } catch (e) {
      print("❌ 로컬 API 연결 대기 중...: $e");
    }
    return <StockModel>[];
  }).asyncMap((event) => event);
});
