import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:hive_flutter/hive_flutter.dart';
import 'package:provider/provider.dart';
import 'package:responsive_sizer/responsive_sizer.dart';

import 'package:ghorario/core/config/firebase_config.dart';
import 'package:ghorario/core/constants/app_strings.dart';
import 'package:ghorario/core/routes/app_router.dart';
import 'package:ghorario/core/themes/app_theme.dart';
import 'package:ghorario/multiproviders/multiproviders.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();

  // Initialize Hive for storage
  await Hive.initFlutter();
  final sessionBox = await Hive.openBox<String>('session');

  // Initialize Firebase
  await Firebase.initializeApp(options: firebaseOptions);

  runApp(App(sessionBox: sessionBox));
}

class App extends StatelessWidget {
  const App({super.key, required this.sessionBox});

  final Box<String> sessionBox;

  @override
  Widget build(BuildContext context) {
    return MultiProvider(
      providers: AppMultiProviders.getProviders(sessionBox),
      child: ResponsiveSizer(
        builder: (context, orientation, screenType) {
          return MaterialApp.router(
            title: AppStrings.appTitle,
            theme: appTheme(),
            debugShowCheckedModeBanner: false,
            routerConfig: appRouter,
          );
        },
      ),
    );
  }
}
