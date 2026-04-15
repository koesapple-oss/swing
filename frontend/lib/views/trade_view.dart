// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/views/trade_view.dart

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import 'package:syncfusion_flutter_charts/charts.dart';
import 'dart:ui';
import '../models/stock_model.dart';
import '../providers/portfolio_provider.dart';
import '../providers/analysis_provider.dart';
import '../services/gemma_service.dart';

class TradeView extends ConsumerWidget {
  final StockModel stock;
  const TradeView({super.key, required this.stock});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return _TradeViewContent(stock: stock);
  }
}

class _TradeViewContent extends ConsumerWidget {
  final StockModel stock;
  const _TradeViewContent({required this.stock});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final currencyFormat = NumberFormat('#,###');

    return Scaffold(
      backgroundColor: const Color(0xFF0D0D0E),
      extendBodyBehindAppBar: true,
      appBar: AppBar(
        title: Text(stock.name, style: GoogleFonts.outfit(fontWeight: FontWeight.bold, fontSize: 22)),
        backgroundColor: Colors.transparent,
        elevation: 0,
        centerTitle: true,
      ),
      body: Stack(
        children: [
          Positioned(
            top: -100,
            right: -50,
            child: ImageFiltered(
              imageFilter: ImageFilter.blur(sigmaX: 70, sigmaY: 70),
              child: Container(
                width: 300,
                height: 300,
                decoration: BoxDecoration(
                  shape: BoxShape.circle,
                  color: Colors.blueAccent.withOpacity(0.15),
                ),
              ),
            ),
          ),
          
          SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const SizedBox(height: 120),
                
                // 1. 차트 섹션 (가독성 강화 버전)
                _buildModernChart(currencyFormat),
                
                const SizedBox(height: 30),
                
                // 2. 현재 가격 강조 (가장 크게)
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 24),
                  child: Container(
                    padding: const EdgeInsets.all(20),
                    decoration: BoxDecoration(
                      color: Colors.blueAccent.withOpacity(0.05),
                      borderRadius: BorderRadius.circular(20),
                      border: Border.all(color: Colors.blueAccent.withOpacity(0.2)),
                    ),
                    child: Row(
                      mainAxisAlignment: MainAxisAlignment.spaceBetween,
                      children: [
                        Text("실시간 시세", style: GoogleFonts.outfit(color: Colors.grey, fontSize: 16, fontWeight: FontWeight.bold)),
                        Text("₩${currencyFormat.format(stock.currentPrice)}", 
                          style: GoogleFonts.outfit(fontSize: 34, fontWeight: FontWeight.w900, color: Colors.blueAccent, letterSpacing: -1)),
                      ],
                    ),
                  ),
                ),
                
                const SizedBox(height: 30),
                _buildGemmaAnalysisCard(ref),
                const SizedBox(height: 20),
                _buildBeginnerGuide(),
                const SizedBox(height: 120),
              ],
            ),
          ),
          _buildFloatingAction(context, ref),
        ],
      ),
    );
  }

  Widget _buildModernChart(NumberFormat format) {
    return Container(
      height: 340,
      margin: const EdgeInsets.symmetric(horizontal: 10),
      child: SfCartesianChart(
        plotAreaBorderWidth: 0,
        primaryXAxis: const CategoryAxis(
          isVisible: true,
          labelStyle: TextStyle(color: Colors.grey, fontWeight: FontWeight.bold),
          axisLine: AxisLine(width: 0),
          majorGridLines: MajorGridLines(width: 0),
        ),
        primaryYAxis: NumericAxis(
          isVisible: true,
          opposedPosition: true,
          labelStyle: const TextStyle(color: Colors.grey, fontSize: 11, fontWeight: FontWeight.bold),
          axisLine: const AxisLine(width: 0),
          majorGridLines: MajorGridLines(color: Colors.white.withOpacity(0.03)),
          // 🔥 K(Compact) 단위 제거, 실제 금액 표기
          numberFormat: NumberFormat('#,###'),
          // 상하 여백을 주어 라벨이 잘리지 않게 함
          rangePadding: ChartRangePadding.additional,
          plotBands: [
            _buildTargetLine(stock.targets['take_profit']!, Colors.greenAccent, "목표 ₩${format.format(stock.targets['take_profit'])}"),
            _buildTargetLine(stock.targets['buy']!, Colors.blueAccent, "매수 ₩${format.format(stock.targets['buy'])}"),
            _buildTargetLine(stock.targets['stop_loss']!, Colors.redAccent, "손절 ₩${format.format(stock.targets['stop_loss'])}"),
          ],
        ),
        series: <CartesianSeries>[
          AreaSeries<dynamic, String>(
            dataSource: [
              {'x': 'D-3', 'y': stock.currentPrice * 0.96},
              {'x': 'D-2', 'y': stock.currentPrice * 0.98},
              {'x': 'D-1', 'y': stock.currentPrice * 0.97},
              {'x': 'Now', 'y': stock.currentPrice},
            ],
            xValueMapper: (data, _) => data['x'],
            yValueMapper: (data, _) => data['y'],
            gradient: LinearGradient(
              colors: [Colors.blueAccent.withOpacity(0.3), Colors.transparent],
              begin: Alignment.topCenter,
              end: Alignment.bottomCenter,
            ),
            borderColor: Colors.blueAccent,
            borderWidth: 3,
            dataLabelSettings: const DataLabelSettings(
              isVisible: true,
              // 🔥 수치 가독성 대폭 강화
              textStyle: TextStyle(color: Colors.white, fontSize: 11, fontWeight: FontWeight.w900, shadows: [Shadow(blurRadius: 5, color: Colors.black)]),
              labelAlignment: ChartDataLabelAlignment.top,
              useSeriesColor: true,
            ),
            markerSettings: const MarkerSettings(isVisible: true, color: Colors.white, width: 6, height: 6, borderWidth: 2, borderColor: Colors.blueAccent),
          )
        ],
      ),
    );
  }

  PlotBand _buildTargetLine(double value, Color color, String label) {
    return PlotBand(
      isVisible: true,
      start: value, end: value,
      borderColor: color,
      borderWidth: 2,
      dashArray: const [5, 5],
      text: "  $label",
      // 🔥 타겟 라인 라벨 하이라이트
      textStyle: TextStyle(color: color, fontSize: 12, fontWeight: FontWeight.w900, backgroundColor: Colors.black.withOpacity(0.5)),
      horizontalTextAlignment: TextAnchor.start,
      verticalTextAlignment: TextAnchor.end, // 선 위로 배치하여 겹침 방지
    );
  }

  Widget _buildGemmaAnalysisCard(WidgetRef ref) {
    final gemmaService = ref.watch(gemmaServiceProvider);
    final analysisState = ref.watch(stockAnalysisProvider);

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 20),
      decoration: BoxDecoration(
        color: const Color(0xFF1A1A1C),
        borderRadius: BorderRadius.circular(28),
        border: Border.all(color: Colors.orangeAccent.withOpacity(0.1)),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(
            padding: const EdgeInsets.all(24),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Row(
                      children: [
                        Container(width: 4, height: 18, decoration: BoxDecoration(color: Colors.orangeAccent, borderRadius: BorderRadius.circular(2))),
                        const SizedBox(width: 12),
                        Text("🤖 Gemma 4 로컬 심층 분석", style: GoogleFonts.outfit(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white)),
                      ],
                    ),
                    if (!gemmaService.isInitialized && !gemmaService.isDownloading)
                      TextButton(
                        onPressed: () => ref.read(gemmaServiceProvider.notifier).initGemma(),
                        child: const Text("모델 준비", style: TextStyle(color: Colors.orangeAccent, fontSize: 12)),
                      ),
                  ],
                ),
                const SizedBox(height: 16),
                
                if (gemmaService.isDownloading)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          const Text("AI 모델 다운로드 중... (약 1.5GB)", style: TextStyle(color: Colors.grey, fontSize: 12)),
                          Text("${(gemmaService.downloadProgress * 100).toInt()}%", style: const TextStyle(color: Colors.orangeAccent, fontSize: 12, fontWeight: FontWeight.bold)),
                        ],
                      ),
                      const SizedBox(height: 8),
                      ClipRRect(
                        borderRadius: BorderRadius.circular(4),
                        child: LinearProgressIndicator(value: gemmaService.downloadProgress, backgroundColor: Colors.white10, color: Colors.orangeAccent, minHeight: 6),
                      ),
                    ],
                  )
                else if (gemmaService.errorMessage != null)
                  Text(
                    "⚠️ ${gemmaService.errorMessage}",
                    style: const TextStyle(color: Colors.redAccent, fontSize: 13),
                  )
                else if (analysisState is AsyncLoading)
                  const Center(
                    child: Padding(
                      padding: EdgeInsets.symmetric(vertical: 20),
                      child: Column(
                        children: [
                          CircularProgressIndicator(color: Colors.orangeAccent, strokeWidth: 2),
                          SizedBox(height: 12),
                          Text("Gemma 4가 차트를 분석 중입니다...", style: TextStyle(color: Colors.grey, fontSize: 12)),
                        ],
                      ),
                    ),
                  )
                else if (analysisState.hasValue && analysisState.requireValue.isNotEmpty)
                  Text(
                    analysisState.requireValue,
                    style: const TextStyle(fontSize: 15, color: Colors.white70, height: 1.6, letterSpacing: 0.3),
                  )
                else
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        "디바이스 내부에서 Gemma 4 모델이 직접 차트와 수급을 분석합니다. Z Flip 5의 GPU 가속을 통해 보안 걱정 없이 빠른 추론이 가능합니다.",
                        style: TextStyle(fontSize: 14, color: Colors.grey, height: 1.5),
                      ),
                      const SizedBox(height: 16),
                      ElevatedButton.icon(
                        onPressed: gemmaService.isInitialized 
                          ? () => ref.read(stockAnalysisProvider.notifier).analyzeStock(stock)
                          : () => ref.read(gemmaServiceProvider.notifier).initGemma(),
                        icon: Icon(gemmaService.isInitialized ? Icons.bolt_rounded : Icons.download_rounded, size: 18),
                        label: Text(gemmaService.isInitialized ? "로컬 AI 분석 실행" : "AI 모델 활성화 (GPU)"),
                        style: ElevatedButton.styleFrom(
                          backgroundColor: Colors.white10,
                          foregroundColor: Colors.orangeAccent,
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
                        ),
                      ),
                    ],
                  ),
              ],
            ),
          ),
          
          const Divider(height: 1, color: Colors.white12),
          _analysisSection("📊 서버 기술적 분석", stock.techReason, Colors.blueAccent),
        ],
      ),
    );
  }

  Widget _analysisSection(String title, String content, Color accent) {
    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(width: 4, height: 18, decoration: BoxDecoration(color: accent, borderRadius: BorderRadius.circular(2))),
              const SizedBox(width: 12),
              Text(title, style: GoogleFonts.outfit(fontSize: 17, fontWeight: FontWeight.bold, color: Colors.white)),
            ],
          ),
          const SizedBox(height: 12),
          Text(
            content.isEmpty ? "AI가 현재 차트 패턴과 거래량 추세를 정밀 분석 중입니다." : content,
            style: const TextStyle(fontSize: 15, color: Colors.white70, height: 1.6, letterSpacing: 0.3),
          ),
        ],
      ),
    );
  }

  Widget _buildBeginnerGuide() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 10),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text("💡 AI 전략 가이드", style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.white)),
          const SizedBox(height: 15),
          _guideItem(Icons.trending_up, "분할 매수 권장", "한 번에 모든 자금을 넣기보다, 매수 권장가 근처에서 2~3회 나누어 담는 것이 안전합니다."),
          _guideItem(Icons.timer_outlined, "스윙 투자 원칙", "해당 전략은 3일~2주 정도의 보유 기간을 산정한 '스윙' 매매입니다."),
        ],
      ),
    );
  }

  Widget _guideItem(IconData icon, String title, String desc) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 15),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Icon(icon, color: Colors.grey.withOpacity(0.6), size: 18),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(title, style: const TextStyle(fontWeight: FontWeight.bold, color: Colors.white, fontSize: 13)),
                const SizedBox(height: 4),
                Text(desc, style: const TextStyle(color: Colors.grey, fontSize: 12, height: 1.4)),
              ],
            ),
          )
        ],
      ),
    );
  }

  Widget _buildFloatingAction(BuildContext context, WidgetRef ref) {
    return Positioned(
      bottom: 30,
      left: 20,
      right: 20,
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          boxShadow: [BoxShadow(color: Colors.orangeAccent.withOpacity(0.3), blurRadius: 20, offset: const Offset(0, 10))],
        ),
        child: ElevatedButton(
          onPressed: () {
            ref.read(portfolioProvider.notifier).buyStock(stock.code, stock.name, stock.currentPrice, 10);
            ScaffoldMessenger.of(context).showSnackBar(
              const SnackBar(backgroundColor: Colors.orangeAccent, content: Text("매수 완료! '내 자산' 탭에서 확인하세요.", style: TextStyle(color: Colors.black, fontWeight: FontWeight.bold)))
            );
          },
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.orangeAccent,
            foregroundColor: Colors.black,
            minimumSize: const Size(double.infinity, 64),
            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
            elevation: 0,
          ),
          child: Text("AI 전략대로 매수하기", style: GoogleFonts.outfit(fontSize: 18, fontWeight: FontWeight.bold)),
        ),
      ),
    );
  }
}
