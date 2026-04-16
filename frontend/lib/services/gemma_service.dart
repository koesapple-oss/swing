import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_gemma/flutter_gemma.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart';

// Gemma의 상태를 관리하기 위한 클래스
class GemmaState {
  final bool isInitialized;
  final bool isDownloading;
  final double downloadProgress;
  final String? errorMessage;

  GemmaState({
    this.isInitialized = false,
    this.isDownloading = false,
    this.downloadProgress = 0,
    this.errorMessage,
  });

  GemmaState copyWith({
    bool? isInitialized,
    bool? isDownloading,
    double? downloadProgress,
    String? errorMessage,
  }) {
    return GemmaState(
      isInitialized: isInitialized ?? this.isInitialized,
      isDownloading: isDownloading ?? this.isDownloading,
      downloadProgress: downloadProgress ?? this.downloadProgress,
      errorMessage: errorMessage ?? this.errorMessage,
    );
  }
}

class GemmaNotifier extends Notifier<GemmaState> {
  // 🚀 Google LiteRT(공식)에서 배포하는 Gemma 4 E2B-it 모델 경로
  static const String _modelUrl = "http://192.168.199.107:8000/static/gemma-4-E2B-it-web.task";
  static const String _modelFileName = "gemma-4-E2B-it-web.task";
  
  InferenceModel? _model;

  @override
  GemmaState build() => GemmaState();

  /// 기기에 모델이 있는지 확인하고, 없으면 다운로드 후 초기화
  Future<void> initGemma() async {
    if (state.isInitialized) return;

    try {
      final directory = await getApplicationSupportDirectory();
      final modelPath = "${directory.path}/$_modelFileName";
      final modelFile = File(modelPath);

      // 1. 모델 파일이 없으면 다운로드
      if (!await modelFile.exists()) {
        print("📂 [Gemma] 모델 파일을 찾을 수 없습니다. 다운로드를 시작합니다...");
        await _downloadModel(modelPath);
      }

      // 2. 최신 API: getActiveModel 사용 (GPU 가속)
      print("🚀 [Gemma] GPU(PreferredBackend.gpu) 모드로 모델 로드 중...");
      _model = await FlutterGemma.getActiveModel(
        preferredBackend: PreferredBackend.gpu,
      );
      
      state = state.copyWith(isInitialized: true, errorMessage: null);
      print("✅ [Gemma] 로컬 모델 초기화 성공");
    } catch (e) {
      state = state.copyWith(errorMessage: "Gemma 초기화 실패: $e");
      print("❌ [Gemma] 초기화 오류: $e");
    }
  }

  Future<void> _downloadModel(String savePath) async {
    state = state.copyWith(isDownloading: true, downloadProgress: 0);
    
    final dio = Dio();
    try {
      await dio.download(
        _modelUrl,
        savePath,
        onReceiveProgress: (count, total) {
          if (total != -1) {
            state = state.copyWith(downloadProgress: count / total);
          }
        },
      );
    } catch (e) {
      state = state.copyWith(errorMessage: "모델 다운로드 중 오류 발생");
      rethrow;
    } finally {
      state = state.copyWith(isDownloading: false);
    }
  }

  /// 텍스트 프롬프트를 전달하여 로컬 추론 결과 반환 (세션 기반)
  Future<String> getResponse(String prompt) async {
    if (!state.isInitialized || _model == null) {
      await initGemma();
      if (!state.isInitialized) return "AI 모델이 초기화되지 않았습니다.";
    }
    
    try {
      print("🧠 [Gemma] 로컬 추론 시작...");
      
      // 최신 API: 채팅 세션 생성
      final session = await _model!.createChat();
      
      // 쿼리 추가
      await session.addQueryChunk(Message.text(text: prompt, isUser: true));
      
      // 응답 수집
      final responseBuffer = StringBuffer();
      await for (final token in session.generateChatResponseAsync()) {
        responseBuffer.write(token);
      }
      
      await session.close(); 
      return responseBuffer.toString();
    } catch (e) {
      return "로컬 분석 오류: $e";
    }
  }
}

final gemmaServiceProvider = NotifierProvider<GemmaNotifier, GemmaState>(() => GemmaNotifier());
