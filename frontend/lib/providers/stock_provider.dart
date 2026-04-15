// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/providers/stock_provider.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';

// 🚀 모든 통신의 기준 주소 (Proxmox 서버 IP)
const String baseUrl = "http://192.168.199.107:8000";

// 🚀 서버에 스캔 시작을 요청합니다. (On-Demand)
Future<void> triggerScan() async {
  try {
    print("🛰 [On-Demand] 스캔 요청 전송 중...");
    final response = await http.post(Uri.parse("$baseUrl/trigger-scan"));
    print("🛰 [On-Demand] 서버 응답: ${response.statusCode}");
  } catch (e) {
    print("❌ 스캔 요청 실패: $e");
  }
}

// 📡 실시간 종목 리스트 가져오기
final stockListProvider = FutureProvider<List<StockModel>>((ref) async {
  const String url = "$baseUrl/recommendations";
  
  try {
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      final list = data.map((json) => StockModel.fromJson(json as Map<String, dynamic>)).toList();
      
      // 정렬 로직: S급 우선 -> AI 점수 내림차순
      list.sort((a, b) {
        if (a.grade != b.grade) {
          if (a.grade == StockGrade.S) return -1;
          if (b.grade == StockGrade.S) return 1;
        }
        return b.sentimentScore.compareTo(a.sentimentScore);
      });
      
      return list;
    } else {
      throw Exception("서버 응답 오류: ${response.statusCode}");
    }
  } catch (e) {
    print("❌ 서버 연결 실패: $e");
    rethrow;
  }
});

// 🛰 서버의 현재 상태(스캔 중 여부 등) 모니터링
final scanStatusProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  yield* Stream.periodic(const Duration(seconds: 5), (_) async {
    try {
      final response = await http.get(Uri.parse(baseUrl));
      if (response.statusCode == 200) {
        return json.decode(response.body) as Map<String, dynamic>;
      }
    } catch (_) {}
    return {"is_scanning": false, "count": 0};
  }).asyncMap((event) => event);
});
