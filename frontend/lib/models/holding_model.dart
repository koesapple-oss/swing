// Project: Swing
// Agent 4: The Frontend Artist
// Path: frontend/lib/models/holding_model.dart

enum HoldingStatus { holding, sold }

class HoldingModel {
  final String code;
  final String name;
  final double buyPrice; // averagePrice에서 buyPrice로 변경
  final int quantity;
  final HoldingStatus status;
  final DateTime buyTimestamp;

  HoldingModel({
    required this.code,
    required this.name,
    required this.buyPrice,
    required this.quantity,
    required this.buyTimestamp,
    this.status = HoldingStatus.holding,
  });

  HoldingModel copyWith({
    HoldingStatus? status,
  }) {
    return HoldingModel(
      code: code,
      name: name,
      buyPrice: buyPrice,
      quantity: quantity,
      buyTimestamp: buyTimestamp,
      status: status ?? this.status,
    );
  }
}
