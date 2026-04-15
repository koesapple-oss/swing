import 'dart:io';
import 'package:dio/dio.dart';
import 'package:flutter_gemma/flutter_gemma.dart';
import 'package:path_provider/path_provider.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter/foundation.dart';

class GemmaService extends ChangeNotifier {
  // Gemma 4 2B IT (Instruction Tuned) GPU 최적화 모델 URL (2026 최신)
  static const String _modelUrl = "https://huggingface.co/google/gemma-4-2b-it-gpu-int4/resolve/main/gemma-4-2b-it-gpu-int4.task";
  static const String _modelFileName = "gemma4_2b_it.task";
  
  bool _isInitialized = false;
  bool get isInitialized => _isInitialized;

  double _downloadProgress = 0;
  double get downloadProgress => _downloadProgress;

  bool _isDownloading = false;
  bool get isDownloading => _isDownloading;

  String? _errorMessage;
  String? get errorMessage => _errorMessage;

  /// 기기에 모델이 있는지 확인하고, 없으면 다운로드 후 초기화
  Future<void> initGemma() async {
    if (_isInitialized) return;

    try {
      final directory = await getApplicationSupportDirectory();
      final modelPath = "${directory.path}/$_modelFileName";
      final modelFile = File(modelPath);

      // 1. 모델 파일이 없으면 다운로드
      if (!await modelFile.exists()) {
        print("📂 [Gemma] 모델 파일을 찾을 수 없습니다. 다운로드를 시작합니다...");
        await _downloadModel(modelPath);
      } else {
        print("📂 [Gemma] 기존 모델 파일을 찾았습니다: $modelPath");
      }

      // 2. Gemma 초기화 (Z Flip 5 - GPU 가속 설정)
      print("🚀 [Gemma] GPU(PreferredBackend.gpu) 모드로 초기화 중...");
      await FlutterGemma.instance.init(
        modelPath: modelPath,
        preferredBackend: PreferredBackend.gpu,
      );
      
      _isInitialized = true;
      _errorMessage = null;
      print("✅ [Gemma] 로컬 모델 초기화 성공");
      notifyListeners();
    } catch (e) {
      _errorMessage = "Gemma 초기화 실패: $e";
      print("❌ [Gemma] 초기화 오류: $e");
      notifyListeners();
    }
  }

  /// DIO를 사용한 모델 파일 다운로드 로직
  Future<void> _downloadModel(String savePath) async {
    _isDownloading = true;
    _downloadProgress = 0;
    notifyListeners();
    
    final dio = Dio();
    try {
      await dio.download(
        _modelUrl,
        savePath,
        onReceiveProgress: (count, total) {
          if (total != -1) {
            _downloadProgress = count / total;
            notifyListeners();
          }
        },
      );
      print("✅ [Gemma] 다운로드 완료: $savePath");
    } catch (e) {
      print("❌ [Gemma] 다운로드 실패: $e");
      _errorMessage = "모델 다운로드 중 오류가 발생했습니다.";
      rethrow;
    } finally {
      _isDownloading = false;
      notifyListeners();
    }
  }

  /// 텍스트 프롬프트를 전달하여 로컬 추론 결과 반환
  Future<String> getResponse(String prompt) async {
    if (!_isInitialized) {
      await initGemma();
      if (!_isInitialized) return "AI 모델이 초기화되지 않았습니다.";
    }
    
    try {
      print("🧠 [Gemma] 로컬 추론 시작...");
      final startTime = DateTime.now();
      
      final response = await FlutterGemma.instance.getCompletion(prompt: prompt);
      
      final duration = DateTime.now().difference(startTime);
      print("⏱ [Gemma] 추론 완료 (${duration.inSeconds}초 소요)");
      
      return response ?? "분석 결과를 생성할 수 없습니다.";
    } catch (e) {
      print("❌ [Gemma] 추론 중 오류: $e");
      return "로컬 분석 오류: $e";
    }
  }
}

final gemmaServiceProvider = ChangeNotifierProvider((ref) => GemmaService());
