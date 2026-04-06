/// User model aligned with FastAPI + Firestore
class UserModel {
  final String id; // 🔥 matches backend user_id
  final String email;

  // Optional profile fields
  final String? displayName;
  final String? photoUrl;
  final String? phoneNumber;
  final int? age;
  final double? weight;
  final String? gender;

  final bool hasDisease;
  final String? diseaseType;
  final String? medicalCondition;

  // New fields for Exercise & Nutrition logic
  final double? bmi;
  final String? bmiGroup;
  final String? activityLevel;
  final double? calorieRemaining;

  UserModel({
    required this.id,
    required this.email,
    this.displayName,
    this.photoUrl,
    this.phoneNumber,
    this.age,
    this.weight,
    this.gender,
    this.hasDisease = false,
    this.diseaseType,
    this.medicalCondition,
    this.bmi,
    this.bmiGroup,
    this.activityLevel,
    this.calorieRemaining,
  });

  /// 🔥 Create from backend response
  factory UserModel.fromMap(Map<String, dynamic> map) {
    return UserModel(
      id: map['user_id'] ?? map['_id'] ?? '',
      email: map['email'] ?? '',

      displayName: map['displayName'],
      photoUrl: map['photoUrl'],
      phoneNumber: map['phoneNumber'],

      age: map['age'] is int
          ? map['age']
          : int.tryParse(map['age']?.toString() ?? ''),

      weight: map['weight'] is double
          ? map['weight']
          : double.tryParse(map['weight']?.toString() ?? ''),

      gender: map['gender'],

      hasDisease: map['hasDisease'] == true ||
          map['hasDisease']?.toString().toLowerCase() == 'true',

      diseaseType: map['diseaseType'],
      medicalCondition: map['medical_condition'] ?? map['medicalCondition'],
      bmi: map['bmi'] is double
          ? map['bmi']
          : double.tryParse(map['bmi']?.toString() ?? ''),
      bmiGroup: map['bmi_group'] ?? map['bmiGroup'],
      activityLevel: map['activity_level'] ?? map['activityLevel'],
      calorieRemaining: map['calorie_remaining'] is double
          ? map['calorie_remaining']
          : double.tryParse(map['calorie_remaining']?.toString() ?? ''),
    );
  }

  /// 🔥 Convert to map
  Map<String, dynamic> toMap() {
    return {
      "user_id": id,
      "email": email,
      "displayName": displayName,
      "photoUrl": photoUrl,
      "phoneNumber": phoneNumber,
      "age": age,
      "weight": weight,
      "gender": gender,
      "hasDisease": hasDisease,
      "diseaseType": diseaseType,
      "medical_condition": medicalCondition,
      "bmi": bmi,
      "bmi_group": bmiGroup,
      "activity_level": activityLevel,
      "calorie_remaining": calorieRemaining,
    };
  }

  @override
  String toString() {
    return "UserModel(id: $id, email: $email)";
  }

  /// 🔥 Context for AI / decision engine
  String getContextString() {
    final parts = <String>[];

    if (displayName != null && displayName!.isNotEmpty) {
      parts.add('Name: $displayName');
    }

    if (age != null) {
      parts.add('Age: $age');
    }

    if (weight != null) {
      parts.add('Weight: $weight kg');
    }

    if (gender != null && gender!.isNotEmpty) {
      parts.add('Gender: $gender');
    }

    if (hasDisease && diseaseType != null && diseaseType!.isNotEmpty) {
      parts.add('Medical condition: $diseaseType');
    }

    return parts.join(', ');
  }
}
