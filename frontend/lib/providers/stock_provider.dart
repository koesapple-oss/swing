// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/providers/stock_provider.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';

// 🚀 Proxmox 서버(192.168.199.107:8000)에서 데이터를 한 번에 가져옵니다.
final stockListProvider = FutureProvider<List<StockModel>>((ref) async {
  // 사용자님의 Proxmox 컨테이너 IP 주소로 고정합니다.
  const String baseUrl = "http://192.168.199.107:8000";
  const String url = "$baseUrl/recommendations";
  
  try {
    final response = await http.get(Uri.parse(url));
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      final list = data.map((json) => StockModel.fromMap(json)).toList();
      
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
    print("❌ 서버 연결 실패 (인터넷/Wi-Fi 확인): $e");
    rethrow;
  }
});

// 🛰 서버의 현재 상태(스캔 중 여부 등)를 모니터링하는 프로바이더
final scanStatusProvider = StreamProvider<Map<String, dynamic>>((ref) async* {
  const String baseUrl = "http://192.168.199.107:8000";
  
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
