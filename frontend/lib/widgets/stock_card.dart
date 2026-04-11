// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/widgets/stock_card.dart

import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:intl/intl.dart';
import '../models/stock_model.dart';
import '../views/trade_view.dart';

class StockCard extends StatelessWidget {
  final StockModel stock;
  const StockCard({super.key, required this.stock});

  @override
  Widget build(BuildContext context) {
    bool isStrong = stock.grade == StockGrade.S;

    return Container(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        borderRadius: BorderRadius.circular(24),
        gradient: LinearGradient(
          colors: [
            const Color(0xFF1A1A1C),
            isStrong ? Colors.redAccent.withOpacity(0.05) : Colors.blueAccent.withOpacity(0.05),
          ],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          )
        ],
        border: Border.all(
          color: isStrong ? Colors.redAccent.withOpacity(0.3) : Colors.white.withOpacity(0.05),
          width: 1,
        ),
      ),
      child: ClipRRect(
        borderRadius: BorderRadius.circular(24),
        child: InkWell(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(builder: (context) => TradeView(stock: stock)),
            );
          },
          child: Padding(
            padding: const EdgeInsets.all(20),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                // 1. 헤더: 종목명 및 등급
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          stock.name,
                          style: GoogleFonts.outfit(fontSize: 20, fontWeight: FontWeight.bold, color: Colors.white),
                        ),
                        const SizedBox(height: 2),
                        Text(
                          "${stock.market} · ${stock.code}",
                          style: const TextStyle(color: Colors.grey, fontSize: 12, letterSpacing: 0.5),
                        ),
                      ],
                    ),
                    _buildGradeBadge(isStrong),
                  ],
                ),
                
                const Padding(
                  padding: EdgeInsets.symmetric(vertical: 16),
                  child: Divider(color: Colors.white12, height: 1),
                ),

                // 2. 핵심 지표
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    _dataPoint("현재가", "₩${NumberFormat('#,###').format(stock.currentPrice)}", Colors.white),
                    _dataPoint("거래대금", "${stock.volume.toInt()}억", Colors.white70),
                    _dataPoint("AI 점수", "${(stock.sentimentScore * 100).toInt()}점", isStrong ? Colors.redAccent : Colors.orangeAccent),
                  ],
                ),
                
                const SizedBox(height: 16),
                
                // 3. AI 인사이트 프리뷰 (초보자를 위한 핵심 요약)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.03),
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: Row(
                    children: [
                      const Icon(Icons.psychology, size: 14, color: Colors.orangeAccent),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          stock.newsSummary,
                          style: const TextStyle(color: Colors.white60, fontSize: 13, overflow: TextOverflow.ellipsis),
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildGradeBadge(bool isStrong) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: isStrong ? Colors.redAccent : Colors.blueAccent.withOpacity(0.2),
        borderRadius: BorderRadius.circular(12),
        boxShadow: isStrong ? [BoxShadow(color: Colors.redAccent.withOpacity(0.4), blurRadius: 10)] : [],
      ),
      child: Text(
        isStrong ? "🔥 강력추천" : "⭐ 추천",
        style: TextStyle(
          color: isStrong ? Colors.white : Colors.blueAccent,
          fontSize: 12,
          fontWeight: FontWeight.w900,
        ),
      ),
    );
  }

  Widget _dataPoint(String label, String value, Color valueColor) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(label, style: const TextStyle(color: Colors.grey, fontSize: 11)),
        const SizedBox(height: 4),
        Text(
          value,
          style: GoogleFonts.outfit(fontSize: 16, fontWeight: FontWeight.bold, color: valueColor),
        ),
      ],
    );
  }
}
