import 'package:flutter/material.dart';
import 'backend/api_requests/api_manager.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'flutter_flow/flutter_flow_util.dart';

class FFAppState extends ChangeNotifier {
  static final FFAppState _instance = FFAppState._internal();

  factory FFAppState() {
    return _instance;
  }

  FFAppState._internal();

  Future initializePersistedState() async {
    prefs = await SharedPreferences.getInstance();
    _safeInit(() {
      _token = prefs.getString('ff_token') ?? _token;
    });
    _safeInit(() {
      _refreshToken = prefs.getString('ff_refreshToken') ?? _refreshToken;
    });
  }

  void update(VoidCallback callback) {
    callback();
    notifyListeners();
  }

  late SharedPreferences prefs;

  String _token = '';
  String get token => _token;
  set token(String _value) {
    _token = _value;
    prefs.setString('ff_token', _value);
  }

  String _refreshToken = '';
  String get refreshToken => _refreshToken;
  set refreshToken(String _value) {
    _refreshToken = _value;
    prefs.setString('ff_refreshToken', _value);
  }

  int _pageSelected = 0;
  int get pageSelected => _pageSelected;
  set pageSelected(int _value) {
    _pageSelected = _value;
  }

  bool _awaitingReply = false;
  bool get awaitingReply => _awaitingReply;
  set awaitingReply(bool _value) {
    _awaitingReply = _value;
  }

  String _promptText = '';
  String get promptText => _promptText;
  set promptText(String _value) {
    _promptText = _value;
  }

  String _modelType = '';
  String get modelType => _modelType;
  set modelType(String _value) {
    _modelType = _value;
  }

  String _modelID = '';
  String get modelID => _modelID;
  set modelID(String _value) {
    _modelID = _value;
  }
}

LatLng? _latLngFromString(String? val) {
  if (val == null) {
    return null;
  }
  final split = val.split(',');
  final lat = double.parse(split.first);
  final lng = double.parse(split.last);
  return LatLng(lat, lng);
}

void _safeInit(Function() initializeField) {
  try {
    initializeField();
  } catch (_) {}
}

Future _safeInitAsync(Function() initializeField) async {
  try {
    await initializeField();
  } catch (_) {}
}
