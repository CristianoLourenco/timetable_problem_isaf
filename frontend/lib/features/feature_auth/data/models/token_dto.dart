/// DTO for the token responses returned by `/auth/login`, `/auth/login-google`
/// and `/auth/refresh` (`TokenResponseSchema`).
class TokenDto {
  const TokenDto({
    required this.idToken,
    required this.refreshToken,
    required this.expiresIn,
  });

  final String idToken;
  final String refreshToken;
  final int expiresIn;

  factory TokenDto.fromJson(Map<String, dynamic> json) {
    return TokenDto(
      idToken: json['id_token'] as String? ?? '',
      refreshToken: json['refresh_token'] as String? ?? '',
      expiresIn: json['expires_in'] as int? ?? 0,
    );
  }
}
