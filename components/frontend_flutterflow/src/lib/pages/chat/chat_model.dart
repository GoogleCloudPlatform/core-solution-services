import '/backend/api_requests/api_calls.dart';
import '/components/chat_bubbles/chat_bubbles_widget.dart';
import '/components/edit_chat_modal/edit_chat_modal_widget.dart';
import '/components/logo_header/logo_header_widget.dart';
import '/components/side_menu/side_menu_widget.dart';
import '/flutter_flow/flutter_flow_animations.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/custom_functions.dart' as functions;
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:font_awesome_flutter/font_awesome_flutter.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import 'package:provider/provider.dart';

class ChatModel extends FlutterFlowModel {
  ///  State fields for stateful widgets in this page.

  final unfocusNode = FocusNode();
  // Model for LogoHeader component.
  late LogoHeaderModel logoHeaderModel;
  // State field(s) for Prompt widget.
  TextEditingController? promptController;
  String? Function(BuildContext, String?)? promptControllerValidator;
  // Stores action output result for [Backend Call - API (Generate Response)] action in Prompt widget.
  ApiCallResponse? chatContinue;
  // Model for sideMenu component.
  late SideMenuModel sideMenuModel;

  /// Initialization and disposal methods.

  void initState(BuildContext context) {
    logoHeaderModel = createModel(context, () => LogoHeaderModel());
    sideMenuModel = createModel(context, () => SideMenuModel());
  }

  void dispose() {
    unfocusNode.dispose();
    logoHeaderModel.dispose();
    promptController?.dispose();
    sideMenuModel.dispose();
  }

  /// Action blocks are added here.

  /// Additional helper methods are added here.
}
