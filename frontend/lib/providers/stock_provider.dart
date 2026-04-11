// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/providers/stock_provider.dart

import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/stock_model.dart';

// 🔥 Proxmox 서버(192.168.199.107:8000)를 실시간으로 폴링합니다.
final stockListProvider = StreamProvider<List<StockModel>>((ref) async* {
  // 사용자님의 Proxmox 컨테이너 IP 주소로 고정합니다.
  const String baseUrl = "http://192.168.199.107:8000";
  const String url = "$baseUrl/recommendations";
  
  // 3초마다 서버에 새로운 인공지능 분석 결과를 물어봅니다.
  yield* Stream.periodic(const Duration(seconds: 3), (_) async {
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
      }
    } catch (e) {
      print("❌ 서버 연결 대기 중 (인터넷/Wi-Fi 확인): $e");
    }
    return <StockModel>[];
  }).asyncMap((event) => event);
});
