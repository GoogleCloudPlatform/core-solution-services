import '/components/logo_header/logo_header_widget.dart';
import '/components/query_result/query_result_widget.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/actions/actions.dart' as action_blocks;
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import 'package:provider/provider.dart';

class QueryModel extends FlutterFlowModel {
  ///  Local state fields for this page.

  dynamic queryDocumentEngineResult;

  ///  State fields for stateful widgets in this page.

  final unfocusNode = FocusNode();
  // Stores action output result for [Action Block - QueryDocumentEngine] action in Query widget.
  dynamic? documentEngineResultOnPageLoad;
  // Model for LogoHeader component.
  late LogoHeaderModel logoHeaderModel;
  // Model for QueryResult component.
  late QueryResultModel queryResultModel;
  // State field(s) for Prompt widget.
  TextEditingController? promptController;
  String? Function(BuildContext, String?)? promptControllerValidator;
  // Stores action output result for [Action Block - QueryDocumentEngine] action in Prompt widget.
  dynamic? queryDocumentEngineResultPromptSubmit;

  /// Initialization and disposal methods.

  void initState(BuildContext context) {
    logoHeaderModel = createModel(context, () => LogoHeaderModel());
    queryResultModel = createModel(context, () => QueryResultModel());
  }

  void dispose() {
    unfocusNode.dispose();
    logoHeaderModel.dispose();
    queryResultModel.dispose();
    promptController?.dispose();
  }

  /// Action blocks are added here.

  /// Additional helper methods are added here.
}
