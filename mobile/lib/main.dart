import 'package:contratista/pages/mother_layout/mother_layout.dart';
import 'package:contratista/services/worker_sinc_service.dart';
import 'package:flutter/material.dart';
import 'package:flutter/services.dart';
import 'package:contratista/utils/globals.dart';
import 'package:contratista/pages/login/login.dart';
import 'package:contratista/services/prod_sinc_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  SystemChrome.setPreferredOrientations([
    DeviceOrientation.portraitUp,
    DeviceOrientation.portraitDown,
    DeviceOrientation.landscapeLeft,
    DeviceOrientation.landscapeRight,
  ]).then((_) async {
    loadFonts();
    await ProductionSyncService.initialize();
    await WorkerSyncService.initialize();
    runApp(const MyApp());
  });
}

Future<void> loadFonts() async {
  await Future.wait([FontLoader("TimesNewRoman").load()]);
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      navigatorKey: globalnavigatorKey,
      initialRoute: '/Login',
      routes: {
        '/Login': (context) => const LoginScreen(),
        '/Mother_Layout': (context) => const MotherLayout(),
      },
    );
  }
}
