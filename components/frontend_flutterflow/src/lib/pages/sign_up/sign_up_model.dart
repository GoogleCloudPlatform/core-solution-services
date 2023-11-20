import '/backend/api_requests/api_calls.dart';
import '/components/logo_header/logo_header_widget.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/flutter_flow_widgets.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';

class SignUpModel extends FlutterFlowModel {
  ///  State fields for stateful widgets in this page.

  final unfocusNode = FocusNode();
  final formKey = GlobalKey<FormState>();
  // Model for LogoHeader component.
  late LogoHeaderModel logoHeaderModel;
  // State field(s) for first_name widget.
  TextEditingController? firstNameController;
  String? Function(BuildContext, String?)? firstNameControllerValidator;
  String? _firstNameControllerValidator(BuildContext context, String? val) {
    if (val == null || val.isEmpty) {
      return 'Field is required';
    }

    return null;
  }

  // State field(s) for last_name widget.
  TextEditingController? lastNameController;
  String? Function(BuildContext, String?)? lastNameControllerValidator;
  String? _lastNameControllerValidator(BuildContext context, String? val) {
    if (val == null || val.isEmpty) {
      return 'Field is required';
    }

    return null;
  }

  // State field(s) for email widget.
  TextEditingController? emailController;
  String? Function(BuildContext, String?)? emailControllerValidator;
  String? _emailControllerValidator(BuildContext context, String? val) {
    if (val == null || val.isEmpty) {
      return 'Field is required';
    }

    if (!RegExp(kTextValidatorEmailRegex).hasMatch(val)) {
      return 'Has to be a valid email address.';
    }
    return null;
  }

  // State field(s) for password widget.
  TextEditingController? passwordController;
  late bool passwordVisibility;
  String? Function(BuildContext, String?)? passwordControllerValidator;
  String? _passwordControllerValidator(BuildContext context, String? val) {
    if (val == null || val.isEmpty) {
      return 'Field is required';
    }

    return null;
  }

  // State field(s) for password2 widget.
  TextEditingController? password2Controller;
  late bool password2Visibility;
  String? Function(BuildContext, String?)? password2ControllerValidator;
  String? _password2ControllerValidator(BuildContext context, String? val) {
    if (val == null || val.isEmpty) {
      return 'Field is required';
    }

    return null;
  }

  // Stores action output result for [Backend Call - API (Sign In)] action in Button widget.
  ApiCallResponse? generateToken;
  // Stores action output result for [Backend Call - API (Create User)] action in Button widget.
  ApiCallResponse? createUser;
  // Stores action output result for [Backend Call - API (Sign Up)] action in Button widget.
  ApiCallResponse? createAccount;
  // Stores action output result for [Backend Call - API (Sign In)] action in Button widget.
  ApiCallResponse? signIn;

  /// Initialization and disposal methods.

  void initState(BuildContext context) {
    logoHeaderModel = createModel(context, () => LogoHeaderModel());
    firstNameControllerValidator = _firstNameControllerValidator;
    lastNameControllerValidator = _lastNameControllerValidator;
    emailControllerValidator = _emailControllerValidator;
    passwordVisibility = false;
    passwordControllerValidator = _passwordControllerValidator;
    password2Visibility = false;
    password2ControllerValidator = _password2ControllerValidator;
  }

  void dispose() {
    unfocusNode.dispose();
    logoHeaderModel.dispose();
    firstNameController?.dispose();
    lastNameController?.dispose();
    emailController?.dispose();
    passwordController?.dispose();
    password2Controller?.dispose();
  }

  /// Action blocks are added here.

  /// Additional helper methods are added here.
}
