import 'package:flutter/material.dart';
import 'package:dartpy/dartpy.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Flutter Python Integration',
      home: MyHomePage(),
    );
  }
}

class MyHomePage extends StatefulWidget {
  @override
  _MyHomePageState createState() => _MyHomePageState();
}

class _MyHomePageState extends State<MyHomePage> {
  late String resultFromPython;

  @override
  void initState() {
    super.initState();
    // Call your Python function when the widget is initialized
    callPythonFunction();
  }

  Future<void> callPythonFunction() async {
    // Initializes the Python runtime
    pyStart();

    try {
      // Imports the Python module containing your function
      final pyModule = pyimport('./utility.py');

      // Replace 'get_radius' with the actual name of your Python function
      final pFunc = pyModule.getFunction('get_radius');

      // Call the Python function
      final result = pFunc();

      // Update the state with the result
      setState(() {
        resultFromPython = 'Result from Python function: $result';
      });
    } on DartPyException catch (e) {
      print(e);
      pyCleanup();
    }

    // Cleans up memory
    pyCleanup();
}


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Flutter Python Integration'),
      ),
      body: Center(
        child: Text(resultFromPython ?? 'Calling Python function...'),
      ),
    );
  }
}
