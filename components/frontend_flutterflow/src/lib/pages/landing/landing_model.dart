import '/backend/api_requests/api_calls.dart';
import '/components/logo_header/logo_header_widget.dart';
import '/components/side_menu/side_menu_widget.dart';
import '/flutter_flow/flutter_flow_animations.dart';
import '/flutter_flow/flutter_flow_choice_chips.dart';
import '/flutter_flow/flutter_flow_drop_down.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/form_field_controller.dart';
import '/flutter_flow/upload_data.dart';
import 'package:aligned_tooltip/aligned_tooltip.dart';
import 'package:flutter/material.dart';
import 'package:flutter/scheduler.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:lottie/lottie.dart';
import 'package:provider/provider.dart';

class LandingModel extends FlutterFlowModel {
  ///  State fields for stateful widgets in this page.

  final unfocusNode = FocusNode();
  // Model for LogoHeader component.
  late LogoHeaderModel logoHeaderModel;
  // State field(s) for ChoiceChips widget.
  String? choiceChipsValue;
  FormFieldController<List<String>>? choiceChipsValueController;
  // State field(s) for PromptInitial widget.
  TextEditingController? promptInitialController;
  String? Function(BuildContext, String?)? promptInitialControllerValidator;
  // Stores action output result for [Backend Call - API (Create Chat)] action in PromptInitial widget.
  ApiCallResponse? newChatCLP;
  // Stores action output result for [Backend Call - API (Update Title)] action in PromptInitial widget.
  ApiCallResponse? apiResultcwe;
  bool isDataUploading = false;
  FFUploadedFile uploadedLocalFile =
      FFUploadedFile(bytes: Uint8List.fromList([]));

  // State field(s) for DropDown widget.
  String? dropDownValue;
  FormFieldController<String>? dropDownValueController;
  // State field(s) for ChatDropdown widget.
  String? chatDropdownValue;
  FormFieldController<String>? chatDropdownValueController;
  // State field(s) for DocumentDropdown widget.
  String? documentDropdownValue;
  FormFieldController<String>? documentDropdownValueController;
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
    promptInitialController?.dispose();
    sideMenuModel.dispose();
  }

  /// Action blocks are added here.

  /// Additional helper methods are added here.
}
