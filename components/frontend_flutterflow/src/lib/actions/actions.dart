import '/backend/api_requests/api_calls.dart';
import '/backend/api_requests/api_manager.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';

Future<dynamic> queryDocumentEngine(BuildContext context) async {
  ApiCallResponse? queryDocumentResult;

  queryDocumentResult = await GoogleCLPDocumentQueryGroup.makeQueryCall.call(
    token: FFAppState().token,
    prompt: FFAppState().promptText,
    qEngineId: FFAppState().modelType,
  );
  if ((queryDocumentResult?.succeeded ?? true)) {
    FFAppState().update(() {
      FFAppState().awaitingReply = false;
    });
  } else {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(
          'API call failed. Please try again.',
          style: FlutterFlowTheme.of(context).bodyMedium,
        ),
        duration: Duration(milliseconds: 3000),
        backgroundColor: FlutterFlowTheme.of(context).error,
      ),
    );
    FFAppState().update(() {
      FFAppState().awaitingReply = false;
    });
  }

  return (queryDocumentResult?.jsonBody ?? '');
}
