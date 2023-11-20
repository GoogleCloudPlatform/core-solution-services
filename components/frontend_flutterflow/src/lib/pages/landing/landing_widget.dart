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
import 'landing_model.dart';
export 'landing_model.dart';

class LandingWidget extends StatefulWidget {
  const LandingWidget({Key? key}) : super(key: key);

  @override
  _LandingWidgetState createState() => _LandingWidgetState();
}

class _LandingWidgetState extends State<LandingWidget>
    with TickerProviderStateMixin {
  late LandingModel _model;

  final scaffoldKey = GlobalKey<ScaffoldState>();

  final animationsMap = {
    'logoHeaderOnPageLoadAnimation': AnimationInfo(
      trigger: AnimationTrigger.onPageLoad,
      effects: [
        FadeEffect(
          curve: Curves.easeInOut,
          delay: 0.ms,
          duration: 600.ms,
          begin: 0.0,
          end: 1.0,
        ),
        MoveEffect(
          curve: Curves.easeInOut,
          delay: 0.ms,
          duration: 600.ms,
          begin: Offset(0.0, 6.0),
          end: Offset(0.0, 0.0),
        ),
      ],
    ),
    'choiceChipsOnPageLoadAnimation': AnimationInfo(
      trigger: AnimationTrigger.onPageLoad,
      effects: [
        FadeEffect(
          curve: Curves.easeInOut,
          delay: 40.ms,
          duration: 550.ms,
          begin: 0.0,
          end: 1.0,
        ),
        MoveEffect(
          curve: Curves.easeInOut,
          delay: 40.ms,
          duration: 550.ms,
          begin: Offset(0.0, 12.000000000000014),
          end: Offset(0.0, 0.0),
        ),
      ],
    ),
    'containerOnPageLoadAnimation': AnimationInfo(
      trigger: AnimationTrigger.onPageLoad,
      effects: [
        FadeEffect(
          curve: Curves.easeInOut,
          delay: 70.ms,
          duration: 490.ms,
          begin: 0.0,
          end: 1.0,
        ),
        MoveEffect(
          curve: Curves.easeInOut,
          delay: 70.ms,
          duration: 490.ms,
          begin: Offset(0.0, 12.000000000000014),
          end: Offset(0.0, 0.0),
        ),
      ],
    ),
    'rowOnPageLoadAnimation': AnimationInfo(
      trigger: AnimationTrigger.onPageLoad,
      effects: [
        FadeEffect(
          curve: Curves.easeInOut,
          delay: 190.ms,
          duration: 650.ms,
          begin: 0.0,
          end: 1.0,
        ),
        MoveEffect(
          curve: Curves.easeInOut,
          delay: 190.ms,
          duration: 650.ms,
          begin: Offset(0.0, 12.000000000000014),
          end: Offset(0.0, 0.0),
        ),
      ],
    ),
  };

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => LandingModel());

    // On page load action.
    SchedulerBinding.instance.addPostFrameCallback((_) async {
      FFAppState().update(() {
        FFAppState().pageSelected = 1;
      });
    });

    _model.promptInitialController ??= TextEditingController();

    WidgetsBinding.instance.addPostFrameCallback((_) => setState(() {}));
  }

  @override
  void dispose() {
    _model.dispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    context.watch<FFAppState>();

    return FutureBuilder<ApiCallResponse>(
      future: GoogleCLPChatGroup.getAllChatsCall.call(
        token: FFAppState().token,
      ),
      builder: (context, snapshot) {
        // Customize what your widget looks like when it's loading.
        if (!snapshot.hasData) {
          return Scaffold(
            backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
            body: Center(
              child: SizedBox(
                width: 50.0,
                height: 50.0,
                child: CircularProgressIndicator(
                  color: FlutterFlowTheme.of(context).primary,
                ),
              ),
            ),
          );
        }
        final landingGetAllChatsResponse = snapshot.data!;
        return GestureDetector(
          onTap: () => FocusScope.of(context).requestFocus(_model.unfocusNode),
          child: Scaffold(
            key: scaffoldKey,
            backgroundColor: FlutterFlowTheme.of(context).primaryBackground,
            drawer: Container(
              width: 275.0,
              child: Drawer(
                elevation: 16.0,
                child: Container(
                  width: double.infinity,
                  height: double.infinity,
                  decoration: BoxDecoration(
                    color: Color(0x2D4490DB),
                  ),
                  child: wrapWithModel(
                    model: _model.sideMenuModel,
                    updateCallback: () => setState(() {}),
                    child: SideMenuWidget(),
                  ),
                ),
              ),
            ),
            body: SafeArea(
              top: true,
              child: Container(
                width: double.infinity,
                height: double.infinity,
                decoration: BoxDecoration(
                  gradient: LinearGradient(
                    colors: [Color(0xFFD7CAE5), Color(0xFFA8B9E6)],
                    stops: [0.0, 1.0],
                    begin: AlignmentDirectional(-0.64, 1.0),
                    end: AlignmentDirectional(0.64, -1.0),
                  ),
                ),
                child: Row(
                  mainAxisSize: MainAxisSize.min,
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Expanded(
                      child: Align(
                        alignment: AlignmentDirectional(0.0, 0.0),
                        child: Container(
                          width: double.infinity,
                          height: double.infinity,
                          constraints: BoxConstraints(
                            maxWidth: 1200.0,
                          ),
                          decoration: BoxDecoration(),
                          child: Padding(
                            padding: EdgeInsetsDirectional.fromSTEB(
                                15.0, 0.0, 15.0, 0.0),
                            child: Row(
                              mainAxisSize: MainAxisSize.max,
                              children: [
                                Expanded(
                                  child: Padding(
                                    padding: EdgeInsetsDirectional.fromSTEB(
                                        0.0, 30.0, 0.0, 30.0),
                                    child: Container(
                                      width: double.infinity,
                                      height: double.infinity,
                                      decoration: BoxDecoration(),
                                      child: Column(
                                        mainAxisSize: MainAxisSize.min,
                                        children: [
                                          Expanded(
                                            child: Row(
                                              mainAxisSize: MainAxisSize.max,
                                              children: [
                                                Expanded(
                                                  child: Container(
                                                    width: double.infinity,
                                                    height: double.infinity,
                                                    decoration: BoxDecoration(
                                                      boxShadow: [
                                                        BoxShadow(
                                                          blurRadius: 5.0,
                                                          color:
                                                              Color(0x00FFFFFF),
                                                          offset:
                                                              Offset(1.0, 2.0),
                                                        )
                                                      ],
                                                      gradient: LinearGradient(
                                                        colors: [
                                                          Color(0x9EFFFFFF),
                                                          Color(0x97DDE4F0)
                                                        ],
                                                        stops: [0.0, 1.0],
                                                        begin:
                                                            AlignmentDirectional(
                                                                -0.64, 1.0),
                                                        end:
                                                            AlignmentDirectional(
                                                                0.64, -1.0),
                                                      ),
                                                      borderRadius:
                                                          BorderRadius.circular(
                                                              15.0),
                                                      border: Border.all(
                                                        color:
                                                            Color(0x37FFFFFF),
                                                      ),
                                                    ),
                                                    child: Column(
                                                      mainAxisSize:
                                                          MainAxisSize.max,
                                                      mainAxisAlignment:
                                                          MainAxisAlignment
                                                              .center,
                                                      children: [
                                                        Padding(
                                                          padding:
                                                              EdgeInsetsDirectional
                                                                  .fromSTEB(
                                                                      0.0,
                                                                      0.0,
                                                                      0.0,
                                                                      12.0),
                                                          child: wrapWithModel(
                                                            model: _model
                                                                .logoHeaderModel,
                                                            updateCallback:
                                                                () => setState(
                                                                    () {}),
                                                            child:
                                                                LogoHeaderWidget(),
                                                          ).animateOnPageLoad(
                                                              animationsMap[
                                                                  'logoHeaderOnPageLoadAnimation']!),
                                                        ),
                                                        FlutterFlowChoiceChips(
                                                          options: [
                                                            ChipData('Chat',
                                                                Icons.chat),
                                                            ChipData(
                                                                'Query',
                                                                Icons
                                                                    .file_copy_rounded)
                                                          ],
                                                          onChanged: (val) =>
                                                              setState(() => _model
                                                                      .choiceChipsValue =
                                                                  val?.first),
                                                          selectedChipStyle:
                                                              ChipStyle(
                                                            backgroundColor:
                                                                FlutterFlowTheme.of(
                                                                        context)
                                                                    .primary,
                                                            textStyle:
                                                                FlutterFlowTheme.of(
                                                                        context)
                                                                    .bodyMedium
                                                                    .override(
                                                                      fontFamily:
                                                                          'Poppins',
                                                                      color: FlutterFlowTheme.of(
                                                                              context)
                                                                          .primaryText,
                                                                    ),
                                                            iconColor:
                                                                FlutterFlowTheme.of(
                                                                        context)
                                                                    .primaryText,
                                                            iconSize: 18.0,
                                                            elevation: 4.0,
                                                            borderRadius:
                                                                BorderRadius
                                                                    .circular(
                                                                        8.0),
                                                          ),
                                                          unselectedChipStyle:
                                                              ChipStyle(
                                                            backgroundColor:
                                                                FlutterFlowTheme.of(
                                                                        context)
                                                                    .secondaryBackground,
                                                            textStyle:
                                                                FlutterFlowTheme.of(
                                                                        context)
                                                                    .bodyMedium
                                                                    .override(
                                                                      fontFamily:
                                                                          'Poppins',
                                                                      color: FlutterFlowTheme.of(
                                                                              context)
                                                                          .secondaryText,
                                                                    ),
                                                            iconColor:
                                                                FlutterFlowTheme.of(
                                                                        context)
                                                                    .secondaryText,
                                                            iconSize: 18.0,
                                                            elevation: 0.0,
                                                            borderRadius:
                                                                BorderRadius
                                                                    .circular(
                                                                        8.0),
                                                          ),
                                                          chipSpacing: 12.0,
                                                          rowSpacing: 12.0,
                                                          multiselect: false,
                                                          initialized: _model
                                                                  .choiceChipsValue !=
                                                              null,
                                                          alignment:
                                                              WrapAlignment
                                                                  .start,
                                                          controller: _model
                                                                  .choiceChipsValueController ??=
                                                              FormFieldController<
                                                                  List<String>>(
                                                            ['Chat'],
                                                          ),
                                                        ).animateOnPageLoad(
                                                            animationsMap[
                                                                'choiceChipsOnPageLoadAnimation']!),
                                                        Padding(
                                                          padding:
                                                              EdgeInsetsDirectional
                                                                  .fromSTEB(
                                                                      0.0,
                                                                      12.0,
                                                                      0.0,
                                                                      5.0),
                                                          child: Container(
                                                            width:
                                                                double.infinity,
                                                            constraints:
                                                                BoxConstraints(
                                                              maxWidth: 750.0,
                                                            ),
                                                            decoration:
                                                                BoxDecoration(
                                                              color: Color(
                                                                  0x69FFFFFF),
                                                              borderRadius:
                                                                  BorderRadius
                                                                      .circular(
                                                                          30.0),
                                                              border:
                                                                  Border.all(
                                                                color: FlutterFlowTheme.of(
                                                                        context)
                                                                    .secondaryText,
                                                                width: 0.25,
                                                              ),
                                                            ),
                                                            child: Row(
                                                              mainAxisSize:
                                                                  MainAxisSize
                                                                      .max,
                                                              mainAxisAlignment:
                                                                  MainAxisAlignment
                                                                      .center,
                                                              children: [
                                                                Expanded(
                                                                  flex: 3,
                                                                  child:
                                                                      Container(
                                                                    width: double
                                                                        .infinity,
                                                                    decoration:
                                                                        BoxDecoration(),
                                                                    child:
                                                                        Padding(
                                                                      padding: EdgeInsetsDirectional.fromSTEB(
                                                                          0.0,
                                                                          0.0,
                                                                          8.0,
                                                                          0.0),
                                                                      child:
                                                                          Container(
                                                                        width: double
                                                                            .infinity,
                                                                        child:
                                                                            TextFormField(
                                                                          controller:
                                                                              _model.promptInitialController,
                                                                          onFieldSubmitted:
                                                                              (_) async {
                                                                            var _shouldSetState =
                                                                                false;
                                                                            FFAppState().update(() {
                                                                              FFAppState().awaitingReply = true;
                                                                              FFAppState().promptText = valueOrDefault<String>(
                                                                                _model.promptInitialController.text,
                                                                                'Prompt Text',
                                                                              );
                                                                            });
                                                                            if (_model.choiceChipsValue ==
                                                                                'Chat') {
                                                                              _model.newChatCLP = await GoogleCLPChatGroup.createChatCall.call(
                                                                                token: FFAppState().token,
                                                                                model: _model.chatDropdownValue,
                                                                                prompt: valueOrDefault<String>(
                                                                                  FFAppState().promptText,
                                                                                  'Prompt Text',
                                                                                ),
                                                                              );
                                                                              _shouldSetState = true;

                                                                              context.goNamed(
                                                                                'Chat',
                                                                                queryParameters: {
                                                                                  'chatRef': serializeParam(
                                                                                    GoogleCLPChatGroup.createChatCall
                                                                                        .id(
                                                                                          (_model.newChatCLP?.jsonBody ?? ''),
                                                                                        )
                                                                                        .toString(),
                                                                                    ParamType.String,
                                                                                  ),
                                                                                }.withoutNulls,
                                                                                extra: <String, dynamic>{
                                                                                  kTransitionInfoKey: TransitionInfo(
                                                                                    hasTransition: true,
                                                                                    transitionType: PageTransitionType.fade,
                                                                                  ),
                                                                                },
                                                                              );

                                                                              if ((_model.newChatCLP?.succeeded ?? true)) {
                                                                                FFAppState().update(() {
                                                                                  FFAppState().awaitingReply = false;
                                                                                });
                                                                                setState(() {
                                                                                  _model.promptInitialController?.clear();
                                                                                });
                                                                                _model.apiResultcwe = await GoogleCLPChatGroup.updateTitleCall.call(
                                                                                  token: FFAppState().token,
                                                                                  title: 'New Chat ',
                                                                                  chatID: GoogleCLPChatGroup.createChatCall
                                                                                      .id(
                                                                                        (_model.newChatCLP?.jsonBody ?? ''),
                                                                                      )
                                                                                      .toString(),
                                                                                );
                                                                                _shouldSetState = true;
                                                                                if ((_model.apiResultcwe?.succeeded ?? true)) {
                                                                                  if (_shouldSetState) setState(() {});
                                                                                  return;
                                                                                }
                                                                              } else {
                                                                                ScaffoldMessenger.of(context).showSnackBar(
                                                                                  SnackBar(
                                                                                    content: Text(
                                                                                      GoogleCLPChatGroup.createChatCall
                                                                                          .apiMessage(
                                                                                            (_model.newChatCLP?.jsonBody ?? ''),
                                                                                          )
                                                                                          .toString(),
                                                                                      style: TextStyle(
                                                                                        color: FlutterFlowTheme.of(context).primaryText,
                                                                                      ),
                                                                                    ),
                                                                                    duration: Duration(milliseconds: 4000),
                                                                                    backgroundColor: FlutterFlowTheme.of(context).secondary,
                                                                                  ),
                                                                                );
                                                                                FFAppState().update(() {
                                                                                  FFAppState().awaitingReply = false;
                                                                                });
                                                                              }
                                                                            } else {
                                                                              setState(() {
                                                                                FFAppState().promptText = _model.promptInitialController.text;
                                                                                FFAppState().modelType = _model.documentDropdownValue!;
                                                                              });
                                                                              setState(() {
                                                                                _model.promptInitialController?.clear();
                                                                              });

                                                                              context.pushNamed(
                                                                                'Query',
                                                                                extra: <String, dynamic>{
                                                                                  kTransitionInfoKey: TransitionInfo(
                                                                                    hasTransition: true,
                                                                                    transitionType: PageTransitionType.fade,
                                                                                  ),
                                                                                },
                                                                              );
                                                                            }

                                                                            if (_shouldSetState)
                                                                              setState(() {});
                                                                          },
                                                                          autofocus:
                                                                              true,
                                                                          obscureText:
                                                                              false,
                                                                          decoration:
                                                                              InputDecoration(
                                                                            isDense:
                                                                                true,
                                                                            labelStyle: FlutterFlowTheme.of(context).labelMedium.override(
                                                                                  fontFamily: 'Poppins',
                                                                                  fontSize: 12.0,
                                                                                ),
                                                                            hintText:
                                                                                'Let\'s talk about learning...',
                                                                            hintStyle: FlutterFlowTheme.of(context).labelMedium.override(
                                                                                  fontFamily: 'Poppins',
                                                                                  fontSize: 12.0,
                                                                                ),
                                                                            enabledBorder:
                                                                                InputBorder.none,
                                                                            focusedBorder:
                                                                                InputBorder.none,
                                                                            errorBorder:
                                                                                InputBorder.none,
                                                                            focusedErrorBorder:
                                                                                InputBorder.none,
                                                                            contentPadding: EdgeInsetsDirectional.fromSTEB(
                                                                                20.0,
                                                                                15.0,
                                                                                20.0,
                                                                                15.0),
                                                                            prefixIcon:
                                                                                Icon(
                                                                              Icons.auto_awesome,
                                                                              color: Color(0xFF9DA2A9),
                                                                              size: 14.0,
                                                                            ),
                                                                          ),
                                                                          style: FlutterFlowTheme.of(context)
                                                                              .bodyMedium
                                                                              .override(
                                                                                fontFamily: 'Poppins',
                                                                                fontSize: 12.0,
                                                                              ),
                                                                          validator: _model
                                                                              .promptInitialControllerValidator
                                                                              .asValidator(context),
                                                                        ),
                                                                      ),
                                                                    ),
                                                                  ),
                                                                ),
                                                                if (false)
                                                                  AlignedTooltip(
                                                                    content:
                                                                        Padding(
                                                                            padding: EdgeInsetsDirectional.fromSTEB(
                                                                                4.0,
                                                                                4.0,
                                                                                4.0,
                                                                                4.0),
                                                                            child:
                                                                                Text(
                                                                              'Upload Reference Document',
                                                                              style: FlutterFlowTheme.of(context).bodyLarge.override(
                                                                                    fontFamily: 'Poppins',
                                                                                    fontSize: 11.0,
                                                                                  ),
                                                                            )),
                                                                    offset: 4.0,
                                                                    preferredDirection:
                                                                        AxisDirection
                                                                            .down,
                                                                    borderRadius:
                                                                        BorderRadius.circular(
                                                                            8.0),
                                                                    backgroundColor:
                                                                        FlutterFlowTheme.of(context)
                                                                            .secondaryBackground,
                                                                    elevation:
                                                                        4.0,
                                                                    tailBaseWidth:
                                                                        24.0,
                                                                    tailLength:
                                                                        12.0,
                                                                    waitDuration:
                                                                        Duration(
                                                                            milliseconds:
                                                                                100),
                                                                    showDuration:
                                                                        Duration(
                                                                            milliseconds:
                                                                                1500),
                                                                    triggerMode:
                                                                        TooltipTriggerMode
                                                                            .tap,
                                                                    child:
                                                                        FlutterFlowIconButton(
                                                                      borderColor:
                                                                          Color(
                                                                              0x00FFFFFF),
                                                                      borderRadius:
                                                                          8.0,
                                                                      borderWidth:
                                                                          0.0,
                                                                      buttonSize:
                                                                          35.0,
                                                                      hoverIconColor:
                                                                          FlutterFlowTheme.of(context)
                                                                              .primaryText,
                                                                      icon:
                                                                          Icon(
                                                                        Icons
                                                                            .cloud_upload_outlined,
                                                                        color: Color(
                                                                            0xFF9DA2A9),
                                                                        size:
                                                                            17.0,
                                                                      ),
                                                                      onPressed: _model.uploadedLocalFile != null &&
                                                                              (_model.uploadedLocalFile.bytes?.isNotEmpty ?? false)
                                                                          ? null
                                                                          : () async {
                                                                              final selectedFiles = await selectFiles(
                                                                                allowedExtensions: [
                                                                                  'pdf'
                                                                                ],
                                                                                multiFile: false,
                                                                              );
                                                                              if (selectedFiles != null) {
                                                                                setState(() => _model.isDataUploading = true);
                                                                                var selectedUploadedFiles = <FFUploadedFile>[];

                                                                                try {
                                                                                  showUploadMessage(
                                                                                    context,
                                                                                    'Uploading file...',
                                                                                    showLoading: true,
                                                                                  );
                                                                                  selectedUploadedFiles = selectedFiles
                                                                                      .map((m) => FFUploadedFile(
                                                                                            name: m.storagePath.split('/').last,
                                                                                            bytes: m.bytes,
                                                                                          ))
                                                                                      .toList();
                                                                                } finally {
                                                                                  ScaffoldMessenger.of(context).hideCurrentSnackBar();
                                                                                  _model.isDataUploading = false;
                                                                                }
                                                                                if (selectedUploadedFiles.length == selectedFiles.length) {
                                                                                  setState(() {
                                                                                    _model.uploadedLocalFile = selectedUploadedFiles.first;
                                                                                  });
                                                                                  showUploadMessage(
                                                                                    context,
                                                                                    'Success!',
                                                                                  );
                                                                                } else {
                                                                                  setState(() {});
                                                                                  showUploadMessage(
                                                                                    context,
                                                                                    'Failed to upload file',
                                                                                  );
                                                                                  return;
                                                                                }
                                                                              }
                                                                            },
                                                                    ),
                                                                  ),
                                                                if (false)
                                                                  SizedBox(
                                                                    height:
                                                                        40.0,
                                                                    child:
                                                                        VerticalDivider(
                                                                      thickness:
                                                                          0.25,
                                                                      color: FlutterFlowTheme.of(
                                                                              context)
                                                                          .secondaryText,
                                                                    ),
                                                                  ),
                                                                if (false)
                                                                  Expanded(
                                                                    flex: 1,
                                                                    child: FlutterFlowDropDown<
                                                                        String>(
                                                                      controller: _model
                                                                              .dropDownValueController ??=
                                                                          FormFieldController<
                                                                              String>(
                                                                        _model.dropDownValue ??=
                                                                            'Chat',
                                                                      ),
                                                                      options: [
                                                                        'Chat',
                                                                        'Document'
                                                                      ],
                                                                      onChanged:
                                                                          (val) =>
                                                                              setState(() => _model.dropDownValue = val),
                                                                      height:
                                                                          40.0,
                                                                      textStyle: FlutterFlowTheme.of(
                                                                              context)
                                                                          .bodyMedium
                                                                          .override(
                                                                            fontFamily:
                                                                                'Poppins',
                                                                            color:
                                                                                FlutterFlowTheme.of(context).secondaryText,
                                                                            fontSize:
                                                                                12.0,
                                                                          ),
                                                                      hintText:
                                                                          'Type',
                                                                      icon:
                                                                          Icon(
                                                                        Icons
                                                                            .keyboard_arrow_down_rounded,
                                                                        color: Color(
                                                                            0xFF9DA2A9),
                                                                        size:
                                                                            20.0,
                                                                      ),
                                                                      elevation:
                                                                          0.0,
                                                                      borderColor:
                                                                          Colors
                                                                              .transparent,
                                                                      borderWidth:
                                                                          0.0,
                                                                      borderRadius:
                                                                          30.0,
                                                                      margin: EdgeInsetsDirectional.fromSTEB(
                                                                          16.0,
                                                                          4.0,
                                                                          16.0,
                                                                          4.0),
                                                                      hidesUnderline:
                                                                          true,
                                                                      isSearchable:
                                                                          false,
                                                                    ),
                                                                  ),
                                                                SizedBox(
                                                                  height: 40.0,
                                                                  child:
                                                                      VerticalDivider(
                                                                    thickness:
                                                                        0.25,
                                                                    color: FlutterFlowTheme.of(
                                                                            context)
                                                                        .secondaryText,
                                                                  ),
                                                                ),
                                                                Expanded(
                                                                  flex: 2,
                                                                  child:
                                                                      Builder(
                                                                    builder:
                                                                        (context) {
                                                                      if (_model
                                                                              .choiceChipsValue ==
                                                                          'Chat') {
                                                                        return FutureBuilder<
                                                                            ApiCallResponse>(
                                                                          future: GoogleCLPChatGroup
                                                                              .getModelsCall
                                                                              .call(
                                                                            token:
                                                                                FFAppState().token,
                                                                          ),
                                                                          builder:
                                                                              (context, snapshot) {
                                                                            // Customize what your widget looks like when it's loading.
                                                                            if (!snapshot.hasData) {
                                                                              return Center(
                                                                                child: SizedBox(
                                                                                  width: 50.0,
                                                                                  height: 50.0,
                                                                                  child: CircularProgressIndicator(
                                                                                    color: FlutterFlowTheme.of(context).primary,
                                                                                  ),
                                                                                ),
                                                                              );
                                                                            }
                                                                            final chatDropdownGetModelsResponse =
                                                                                snapshot.data!;
                                                                            return FlutterFlowDropDown<String>(
                                                                              controller: _model.chatDropdownValueController ??= FormFieldController<String>(
                                                                                _model.chatDropdownValue ??= 'VertexAI-Chat',
                                                                              ),
                                                                              options: (GoogleCLPChatGroup.getModelsCall.models(
                                                                                chatDropdownGetModelsResponse.jsonBody,
                                                                              ) as List)
                                                                                  .map<String>((s) => s.toString())
                                                                                  .toList()!,
                                                                              onChanged: (val) => setState(() => _model.chatDropdownValue = val),
                                                                              height: 40.0,
                                                                              textStyle: FlutterFlowTheme.of(context).bodyMedium.override(
                                                                                    fontFamily: 'Poppins',
                                                                                    color: FlutterFlowTheme.of(context).secondaryText,
                                                                                    fontSize: 12.0,
                                                                                  ),
                                                                              hintText: 'Model',
                                                                              icon: Icon(
                                                                                Icons.keyboard_arrow_down_rounded,
                                                                                color: Color(0xFF9DA2A9),
                                                                                size: 20.0,
                                                                              ),
                                                                              elevation: 0.0,
                                                                              borderColor: Colors.transparent,
                                                                              borderWidth: 0.0,
                                                                              borderRadius: 30.0,
                                                                              margin: EdgeInsetsDirectional.fromSTEB(16.0, 4.0, 16.0, 4.0),
                                                                              hidesUnderline: true,
                                                                              isSearchable: false,
                                                                            );
                                                                          },
                                                                        );
                                                                      } else {
                                                                        return FutureBuilder<
                                                                            ApiCallResponse>(
                                                                          future: GoogleCLPDocumentQueryGroup
                                                                              .getEnginesCall
                                                                              .call(
                                                                            token:
                                                                                FFAppState().token,
                                                                          ),
                                                                          builder:
                                                                              (context, snapshot) {
                                                                            // Customize what your widget looks like when it's loading.
                                                                            if (!snapshot.hasData) {
                                                                              return Center(
                                                                                child: SizedBox(
                                                                                  width: 50.0,
                                                                                  height: 50.0,
                                                                                  child: CircularProgressIndicator(
                                                                                    color: FlutterFlowTheme.of(context).primary,
                                                                                  ),
                                                                                ),
                                                                              );
                                                                            }
                                                                            final documentDropdownGetEnginesResponse =
                                                                                snapshot.data!;
                                                                            return FlutterFlowDropDown<String>(
                                                                              controller: _model.documentDropdownValueController ??= FormFieldController<String>(null),
                                                                              options: (GoogleCLPDocumentQueryGroup.getEnginesCall.engineIds(
                                                                                documentDropdownGetEnginesResponse.jsonBody,
                                                                              ) as List)
                                                                                  .map<String>((s) => s.toString())
                                                                                  .toList()!
                                                                                  .map((e) => e.toString())
                                                                                  .toList(),
                                                                              optionLabels: (GoogleCLPDocumentQueryGroup.getEnginesCall.engines(
                                                                                documentDropdownGetEnginesResponse.jsonBody,
                                                                              ) as List)
                                                                                  .map<String>((s) => s.toString())
                                                                                  .toList()!
                                                                                  .map((e) => e.toString())
                                                                                  .toList(),
                                                                              onChanged: (val) => setState(() => _model.documentDropdownValue = val),
                                                                              height: 40.0,
                                                                              textStyle: FlutterFlowTheme.of(context).bodyMedium.override(
                                                                                    fontFamily: 'Poppins',
                                                                                    color: FlutterFlowTheme.of(context).secondaryText,
                                                                                    fontSize: 12.0,
                                                                                  ),
                                                                              hintText: 'Engine',
                                                                              icon: Icon(
                                                                                Icons.keyboard_arrow_down_rounded,
                                                                                color: Color(0xFF9DA2A9),
                                                                                size: 20.0,
                                                                              ),
                                                                              elevation: 0.0,
                                                                              borderColor: Colors.transparent,
                                                                              borderWidth: 0.0,
                                                                              borderRadius: 30.0,
                                                                              margin: EdgeInsetsDirectional.fromSTEB(16.0, 4.0, 16.0, 4.0),
                                                                              hidesUnderline: true,
                                                                              isSearchable: false,
                                                                            );
                                                                          },
                                                                        );
                                                                      }
                                                                    },
                                                                  ),
                                                                ),
                                                              ],
                                                            ),
                                                          ).animateOnPageLoad(
                                                              animationsMap[
                                                                  'containerOnPageLoadAnimation']!),
                                                        ),
                                                        if (!FFAppState()
                                                            .awaitingReply)
                                                          Padding(
                                                            padding:
                                                                EdgeInsetsDirectional
                                                                    .fromSTEB(
                                                                        0.0,
                                                                        30.0,
                                                                        0.0,
                                                                        0.0),
                                                            child: Row(
                                                              mainAxisSize:
                                                                  MainAxisSize
                                                                      .max,
                                                              mainAxisAlignment:
                                                                  MainAxisAlignment
                                                                      .center,
                                                              children: [
                                                                Text(
                                                                  'Or continue a chat',
                                                                  style: FlutterFlowTheme.of(
                                                                          context)
                                                                      .bodyMedium
                                                                      .override(
                                                                        fontFamily:
                                                                            'Poppins',
                                                                        color: FlutterFlowTheme.of(context)
                                                                            .secondaryText,
                                                                        fontSize:
                                                                            12.0,
                                                                      ),
                                                                ),
                                                                Padding(
                                                                  padding: EdgeInsetsDirectional
                                                                      .fromSTEB(
                                                                          10.0,
                                                                          0.0,
                                                                          0.0,
                                                                          0.0),
                                                                  child:
                                                                      FlutterFlowIconButton(
                                                                    borderColor:
                                                                        Color(
                                                                            0x8D4490DB),
                                                                    borderRadius:
                                                                        20.0,
                                                                    borderWidth:
                                                                        0.1,
                                                                    buttonSize:
                                                                        35.0,
                                                                    fillColor:
                                                                        Color(
                                                                            0x8D4490DB),
                                                                    hoverColor:
                                                                        FlutterFlowTheme.of(context)
                                                                            .primary,
                                                                    hoverIconColor:
                                                                        Colors
                                                                            .white,
                                                                    icon: Icon(
                                                                      Icons
                                                                          .arrow_forward,
                                                                      color: Colors
                                                                          .white,
                                                                      size:
                                                                          16.0,
                                                                    ),
                                                                    onPressed:
                                                                        () async {
                                                                      scaffoldKey
                                                                          .currentState!
                                                                          .openDrawer();
                                                                    },
                                                                  ),
                                                                ),
                                                              ],
                                                            ).animateOnPageLoad(
                                                                animationsMap[
                                                                    'rowOnPageLoadAnimation']!),
                                                          ),
                                                        if (FFAppState()
                                                            .awaitingReply)
                                                          Padding(
                                                            padding:
                                                                EdgeInsetsDirectional
                                                                    .fromSTEB(
                                                                        10.0,
                                                                        5.0,
                                                                        10.0,
                                                                        0.0),
                                                            child: Container(
                                                              width: double
                                                                  .infinity,
                                                              constraints:
                                                                  BoxConstraints(
                                                                maxWidth: 700.0,
                                                              ),
                                                              decoration:
                                                                  BoxDecoration(),
                                                              child: Row(
                                                                mainAxisSize:
                                                                    MainAxisSize
                                                                        .max,
                                                                mainAxisAlignment:
                                                                    MainAxisAlignment
                                                                        .center,
                                                                children: [
                                                                  Padding(
                                                                    padding: EdgeInsetsDirectional
                                                                        .fromSTEB(
                                                                            0.0,
                                                                            3.0,
                                                                            0.0,
                                                                            0.0),
                                                                    child:
                                                                        Container(
                                                                      width:
                                                                          50.0,
                                                                      height:
                                                                          50.0,
                                                                      decoration:
                                                                          BoxDecoration(
                                                                        image:
                                                                            DecorationImage(
                                                                          fit: BoxFit
                                                                              .contain,
                                                                          image:
                                                                              Image.asset(
                                                                            'assets/images/bardStars.png',
                                                                          ).image,
                                                                        ),
                                                                      ),
                                                                    ),
                                                                  ),
                                                                  Lottie.asset(
                                                                    'assets/lottie_animations/6652-dote-typing-animation.json',
                                                                    width: 40.0,
                                                                    height:
                                                                        70.0,
                                                                    fit: BoxFit
                                                                        .fitHeight,
                                                                    animate:
                                                                        true,
                                                                  ),
                                                                ],
                                                              ),
                                                            ),
                                                          ),
                                                      ],
                                                    ),
                                                  ),
                                                ),
                                              ],
                                            ),
                                          ),
                                        ],
                                      ),
                                    ),
                                  ),
                                ),
                              ],
                            ),
                          ),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
            ),
          ),
        );
      },
    );
  }
}
