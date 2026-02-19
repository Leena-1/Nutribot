/// User model with extended profile information
class UserModel {
  final String uid;
  final String email;
  final String? displayName;
  final String? photoUrl;
  
  // Extended profile fields
  final String? phoneNumber;
  final int? age;
  final String? gender; // 'male', 'female', 'other'
  final bool hasDisease;
  final String? diseaseType; // e.g., 'diabetes', 'blood_pressure', 'heart_disease'

  UserModel({
    required this.uid,
    required this.email,
    this.displayName,
    this.photoUrl,
    this.phoneNumber,
    this.age,
    this.gender,
    this.hasDisease = false,
    this.diseaseType,
  });

  factory UserModel.fromMap(Map<String, dynamic> map) {
    return UserModel(
      uid: map['uid'] ?? '',
      email: map['email'] ?? '',
      displayName: map['displayName'],
      photoUrl: map['photoUrl'],
      phoneNumber: map['phoneNumber'],
      age: map['age'] != null ? int.tryParse(map['age'].toString()) : null,
      gender: map['gender'],
      hasDisease: map['hasDisease'] == true || map['hasDisease'] == 'true',
      diseaseType: map['diseaseType'],
    );
  }

  Map<String, dynamic> toMap() {
    return {
      'uid': uid,
      'email': email,
      'displayName': displayName,
      'photoUrl': photoUrl,
      'phoneNumber': phoneNumber,
      'age': age,
      'gender': gender,
      'hasDisease': hasDisease,
      'diseaseType': diseaseType,
    };
  }

  /// Get user context string for personalized chat responses
  String getContextString() {
    final parts = <String>[];
    if (displayName != null) parts.add('Name: $displayName');
    if (age != null) parts.add('Age: $age');
    if (gender != null) parts.add('Gender: $gender');
    if (hasDisease && diseaseType != null) {
      parts.add('Medical condition: $diseaseType');
    }
    return parts.join(', ');
  }
}
