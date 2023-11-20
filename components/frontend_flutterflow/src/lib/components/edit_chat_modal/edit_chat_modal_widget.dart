import '/backend/api_requests/api_calls.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/flutter_flow_widgets.dart';
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'edit_chat_modal_model.dart';
export 'edit_chat_modal_model.dart';

class EditChatModalWidget extends StatefulWidget {
  const EditChatModalWidget({
    Key? key,
    String? chartTitle,
    this.chatRef,
  })  : this.chartTitle = chartTitle ?? 'New Chat',
        super(key: key);

  final String chartTitle;
  final String? chatRef;

  @override
  _EditChatModalWidgetState createState() => _EditChatModalWidgetState();
}

class _EditChatModalWidgetState extends State<EditChatModalWidget> {
  late EditChatModalModel _model;

  @override
  void setState(VoidCallback callback) {
    super.setState(callback);
    _model.onUpdate();
  }

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => EditChatModalModel());

    _model.textController ??= TextEditingController();
    WidgetsBinding.instance.addPostFrameCallback((_) => setState(() {}));
  }

  @override
  void dispose() {
    _model.maybeDispose();

    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    context.watch<FFAppState>();

    return Align(
      alignment: AlignmentDirectional(0.0, 0.0),
      child: Padding(
        padding: EdgeInsetsDirectional.fromSTEB(16.0, 16.0, 16.0, 16.0),
        child: Container(
          width: double.infinity,
          height: 250.0,
          constraints: BoxConstraints(
            maxWidth: 570.0,
          ),
          decoration: BoxDecoration(
            gradient: LinearGradient(
              colors: [Color(0xFFD7CAE5), Color(0xFFA8B9E6)],
              stops: [0.0, 1.0],
              begin: AlignmentDirectional(-0.64, 1.0),
              end: AlignmentDirectional(0.64, -1.0),
            ),
            borderRadius: BorderRadius.circular(12.0),
            border: Border.all(
              color: Color(0x444490DB),
            ),
          ),
          child: Padding(
            padding: EdgeInsetsDirectional.fromSTEB(24.0, 20.0, 24.0, 24.0),
            child: Column(
              mainAxisSize: MainAxisSize.max,
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Align(
                  alignment: AlignmentDirectional(1.0, -1.0),
                  child: Padding(
                    padding:
                        EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 10.0, 30.0),
                    child: InkWell(
                      splashColor: Colors.transparent,
                      focusColor: Colors.transparent,
                      hoverColor: Colors.transparent,
                      highlightColor: Colors.transparent,
                      onTap: () async {
                        Navigator.pop(context);
                      },
                      child: Icon(
                        Icons.close_rounded,
                        color: FlutterFlowTheme.of(context).secondaryText,
                        size: 18.0,
                      ),
                    ),
                  ),
                ),
                Padding(
                  padding: EdgeInsetsDirectional.fromSTEB(8.0, 0.0, 8.0, 0.0),
                  child: TextFormField(
                    controller: _model.textController,
                    autofocus: true,
                    obscureText: false,
                    decoration: InputDecoration(
                      isDense: true,
                      labelText: 'Chat Title',
                      labelStyle:
                          FlutterFlowTheme.of(context).labelMedium.override(
                                fontFamily: 'Poppins',
                                color: FlutterFlowTheme.of(context).primaryText,
                                fontSize: 12.0,
                              ),
                      hintStyle:
                          FlutterFlowTheme.of(context).labelMedium.override(
                                fontFamily: 'Poppins',
                                color: FlutterFlowTheme.of(context).primaryText,
                              ),
                      enabledBorder: OutlineInputBorder(
                        borderSide: BorderSide(
                          color: FlutterFlowTheme.of(context).secondaryText,
                          width: 0.1,
                        ),
                        borderRadius: BorderRadius.circular(20.0),
                      ),
                      focusedBorder: OutlineInputBorder(
                        borderSide: BorderSide(
                          color: FlutterFlowTheme.of(context).primaryText,
                          width: 0.1,
                        ),
                        borderRadius: BorderRadius.circular(20.0),
                      ),
                      errorBorder: OutlineInputBorder(
                        borderSide: BorderSide(
                          color: FlutterFlowTheme.of(context).error,
                          width: 0.1,
                        ),
                        borderRadius: BorderRadius.circular(20.0),
                      ),
                      focusedErrorBorder: OutlineInputBorder(
                        borderSide: BorderSide(
                          color: FlutterFlowTheme.of(context).error,
                          width: 0.1,
                        ),
                        borderRadius: BorderRadius.circular(20.0),
                      ),
                      filled: true,
                      fillColor: Color(0x69FFFFFF),
                      contentPadding: EdgeInsetsDirectional.fromSTEB(
                          20.0, 15.0, 20.0, 15.0),
                    ),
                    style: FlutterFlowTheme.of(context).bodyMedium,
                    validator:
                        _model.textControllerValidator.asValidator(context),
                  ),
                ),
                Padding(
                  padding: EdgeInsetsDirectional.fromSTEB(0.0, 30.0, 0.0, 0.0),
                  child: Row(
                    mainAxisSize: MainAxisSize.max,
                    mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                    children: [
                      FFButtonWidget(
                        onPressed: () async {
                          _model.apiResultm4x =
                              await GoogleCLPChatGroup.updateTitleCall.call(
                            token: FFAppState().token,
                            title: _model.textController.text,
                            chatID: widget.chatRef,
                          );
                          if ((_model.apiResultm4x?.succeeded ?? true)) {
                            Navigator.pop(context);
                          } else {
                            Navigator.pop(context);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(
                                  GoogleCLPChatGroup.updateTitleCall
                                      .apiMessage(
                                        (_model.apiResultm4x?.jsonBody ?? ''),
                                      )
                                      .toString(),
                                  style: TextStyle(
                                    color: FlutterFlowTheme.of(context)
                                        .primaryText,
                                  ),
                                ),
                                duration: Duration(milliseconds: 4000),
                                backgroundColor:
                                    FlutterFlowTheme.of(context).secondary,
                              ),
                            );
                          }

                          setState(() {});
                        },
                        text: 'Save',
                        options: FFButtonOptions(
                          width: 150.0,
                          height: 40.0,
                          padding: EdgeInsetsDirectional.fromSTEB(
                              0.0, 0.0, 0.0, 0.0),
                          iconPadding: EdgeInsetsDirectional.fromSTEB(
                              0.0, 0.0, 0.0, 0.0),
                          color: Color(0x444490DB),
                          textStyle: FlutterFlowTheme.of(context)
                              .titleSmall
                              .override(
                                fontFamily: 'Poppins',
                                color: FlutterFlowTheme.of(context).primaryText,
                                fontSize: 11.0,
                                fontWeight: FontWeight.normal,
                              ),
                          elevation: 0.0,
                          borderSide: BorderSide(
                            color: Color(0x444490DB),
                            width: 0.1,
                          ),
                          borderRadius: BorderRadius.circular(20.0),
                          hoverColor: FlutterFlowTheme.of(context).primary,
                          hoverBorderSide: BorderSide(
                            color: FlutterFlowTheme.of(context).primary,
                            width: 0.1,
                          ),
                          hoverTextColor: Colors.white,
                          hoverElevation: 0.0,
                        ),
                      ),
                      FFButtonWidget(
                        onPressed: () async {
                          var _shouldSetState = false;
                          var confirmDialogResponse = await showDialog<bool>(
                                context: context,
                                builder: (alertDialogContext) {
                                  return AlertDialog(
                                    content: Text(
                                        'Are you sure you\'d like to delete this chat?'),
                                    actions: [
                                      TextButton(
                                        onPressed: () => Navigator.pop(
                                            alertDialogContext, false),
                                        child: Text('Nevermind'),
                                      ),
                                      TextButton(
                                        onPressed: () => Navigator.pop(
                                            alertDialogContext, true),
                                        child: Text('Yes, please'),
                                      ),
                                    ],
                                  );
                                },
                              ) ??
                              false;
                          if (confirmDialogResponse) {
                            _model.apiResultevs =
                                await GoogleCLPChatGroup.deleteChatCall.call(
                              token: FFAppState().token,
                              chatID: widget.chatRef,
                            );
                            _shouldSetState = true;
                            if ((_model.apiResultevs?.succeeded ?? true)) {
                              Navigator.pop(context);
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                    'Chat deleted.',
                                    style: TextStyle(
                                      color: Colors.white,
                                    ),
                                  ),
                                  duration: Duration(milliseconds: 2600),
                                  backgroundColor:
                                      FlutterFlowTheme.of(context).success,
                                ),
                              );

                              context.goNamed(
                                'Landing',
                                extra: <String, dynamic>{
                                  kTransitionInfoKey: TransitionInfo(
                                    hasTransition: true,
                                    transitionType: PageTransitionType.fade,
                                  ),
                                },
                              );

                              if (_shouldSetState) setState(() {});
                              return;
                            } else {
                              ScaffoldMessenger.of(context).showSnackBar(
                                SnackBar(
                                  content: Text(
                                    GoogleCLPChatGroup.deleteChatCall
                                        .apiMessage(
                                          (_model.apiResultevs?.jsonBody ?? ''),
                                        )
                                        .toString(),
                                    style: TextStyle(
                                      color: FlutterFlowTheme.of(context)
                                          .primaryText,
                                    ),
                                  ),
                                  duration: Duration(milliseconds: 4000),
                                  backgroundColor:
                                      FlutterFlowTheme.of(context).alternate,
                                ),
                              );
                            }
                          }
                          if (_shouldSetState) setState(() {});
                        },
                        text: 'Delete Chat',
                        options: FFButtonOptions(
                          width: 150.0,
                          height: 40.0,
                          padding: EdgeInsetsDirectional.fromSTEB(
                              0.0, 0.0, 0.0, 0.0),
                          iconPadding: EdgeInsetsDirectional.fromSTEB(
                              0.0, 0.0, 0.0, 0.0),
                          color: Color(0x52D36679),
                          textStyle: FlutterFlowTheme.of(context)
                              .titleSmall
                              .override(
                                fontFamily: 'Poppins',
                                color: FlutterFlowTheme.of(context).primaryText,
                                fontSize: 11.0,
                                fontWeight: FontWeight.normal,
                              ),
                          elevation: 0.0,
                          borderSide: BorderSide(
                            color: FlutterFlowTheme.of(context).alternate,
                            width: 0.1,
                          ),
                          borderRadius: BorderRadius.circular(20.0),
                          hoverColor: FlutterFlowTheme.of(context).alternate,
                          hoverBorderSide: BorderSide(
                            color: FlutterFlowTheme.of(context).alternate,
                            width: 0.1,
                          ),
                          hoverTextColor: Colors.white,
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
    );
  }
}
