import 'package:firebase_core/firebase_core.dart';

/// Firebase project configuration.
///
/// Holds the credentials required to initialise Firebase services.
/// In a future phase these may move to environment variables.
class FirebaseConfig {
  FirebaseConfig._();

  static const String apiKey = 'AIzaSyCcmvG_mtxbvyMQnIcFynm2WWv_SwS7wXI';
  static const String authDomain = 'g-horario-b00eb.firebaseapp.com';
  static const String databaseURL =
      'https://g-horario-b00eb-default-rtdb.firebaseio.com';
  static const String projectId = 'g-horario-b00eb';
  static const String storageBucket = 'g-horario-b00eb.appspot.com';
  static const String messagingSenderId = '560044972673';
  static const String appId = '1:560044972673:web:ea63cd048aad29d9e44b80';
  static const String measurementId = 'G-FV2BBBF3S2';
}

/// Pre-built [FirebaseOptions] for use in `Firebase.initializeApp`.
const FirebaseOptions firebaseOptions = FirebaseOptions(
  apiKey: FirebaseConfig.apiKey,
  appId: FirebaseConfig.appId,
  messagingSenderId: FirebaseConfig.messagingSenderId,
  projectId: FirebaseConfig.projectId,
);
