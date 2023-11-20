import '/backend/api_requests/api_calls.dart';
import '/components/no_chats/no_chats_widget.dart';
import '/flutter_flow/flutter_flow_icon_button.dart';
import '/flutter_flow/flutter_flow_theme.dart';
import '/flutter_flow/flutter_flow_util.dart';
import '/flutter_flow/flutter_flow_widgets.dart';
import '/flutter_flow/custom_functions.dart' as functions;
import 'package:flutter/material.dart';
import 'package:google_fonts/google_fonts.dart';
import 'package:provider/provider.dart';
import 'side_menu_model.dart';
export 'side_menu_model.dart';

class SideMenuWidget extends StatefulWidget {
  const SideMenuWidget({
    Key? key,
    String? currentChatRef,
  })  : this.currentChatRef = currentChatRef ?? '0',
        super(key: key);

  final String currentChatRef;

  @override
  _SideMenuWidgetState createState() => _SideMenuWidgetState();
}

class _SideMenuWidgetState extends State<SideMenuWidget> {
  late SideMenuModel _model;

  @override
  void setState(VoidCallback callback) {
    super.setState(callback);
    _model.onUpdate();
  }

  @override
  void initState() {
    super.initState();
    _model = createModel(context, () => SideMenuModel());

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

    return Padding(
      padding: EdgeInsetsDirectional.fromSTEB(12.0, 50.0, 12.0, 50.0),
      child: Column(
        mainAxisSize: MainAxisSize.max,
        children: [
          if (FFAppState().pageSelected != 1)
            Padding(
              padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 30.0),
              child: FFButtonWidget(
                onPressed: () async {
                  context.goNamed(
                    'Landing',
                    extra: <String, dynamic>{
                      kTransitionInfoKey: TransitionInfo(
                        hasTransition: true,
                        transitionType: PageTransitionType.fade,
                      ),
                    },
                  );
                },
                text: 'New Chat',
                icon: Icon(
                  Icons.library_add,
                  size: 16.0,
                ),
                options: FFButtonOptions(
                  width: 150.0,
                  height: 40.0,
                  padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 0.0),
                  iconPadding:
                      EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 0.0),
                  color: Color(0x00AFB5BF),
                  textStyle: FlutterFlowTheme.of(context).titleSmall.override(
                        fontFamily: 'Poppins',
                        color: FlutterFlowTheme.of(context).secondaryText,
                        fontSize: 11.0,
                        fontWeight: FontWeight.normal,
                      ),
                  elevation: 0.0,
                  borderRadius: BorderRadius.circular(18.0),
                  hoverColor: FlutterFlowTheme.of(context).customColor1,
                  hoverTextColor: Colors.white,
                  hoverElevation: 0.0,
                ),
              ),
            ),
          Expanded(
            child: Padding(
              padding: EdgeInsetsDirectional.fromSTEB(0.0, 0.0, 0.0, 35.0),
              child: FutureBuilder<ApiCallResponse>(
                future: GoogleCLPChatGroup.getAllChatsCall.call(
                  token: FFAppState().token,
                ),
                builder: (context, snapshot) {
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
                  final listViewGetAllChatsResponse = snapshot.data!;
                  return Builder(
                    builder: (context) {
                      final chat = GoogleCLPChatGroup.getAllChatsCall
                              .root(
                                listViewGetAllChatsResponse.jsonBody,
                              )
                              ?.toList() ??
                          [];
                      if (chat.isEmpty) {
                        return NoChatsWidget();
                      }
                      return ListView.builder(
                        padding: EdgeInsets.zero,
                        shrinkWrap: true,
                        scrollDirection: Axis.vertical,
                        itemCount: chat.length,
                        itemBuilder: (context, chatIndex) {
                          final chatItem = chat[chatIndex];
                          return Padding(
                            padding: EdgeInsetsDirectional.fromSTEB(
                                0.0, 0.0, 0.0, 8.0),
                            child: InkWell(
                              splashColor: Colors.transparent,
                              focusColor: Colors.transparent,
                              hoverColor: Colors.transparent,
                              highlightColor: Colors.transparent,
                              onTap: () async {
                                context.goNamed(
                                  'Chat',
                                  queryParameters: {
                                    'chatRef': serializeParam(
                                      getJsonField(
                                        chatItem,
                                        r'''$.id''',
                                      ).toString(),
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

                                FFAppState().update(() {
                                  FFAppState().awaitingReply = false;
                                });
                                Navigator.pop(context);
                              },
                              child: Container(
                                width: double.infinity,
                                decoration: BoxDecoration(
                                  color: valueOrDefault<Color>(
                                    getJsonField(
                                              chatItem,
                                              r'''$.id''',
                                            ) ==
                                            widget.currentChatRef
                                        ? Colors.white
                                        : Color(0xACFFFFFF),
                                    Color(0xACFFFFFF),
                                  ),
                                  borderRadius: BorderRadius.circular(10.0),
                                  border: Border.all(
                                    color: valueOrDefault<Color>(
                                      getJsonField(
                                                chatItem,
                                                r'''$.id''',
                                              ) ==
                                              widget.currentChatRef
                                          ? FlutterFlowTheme.of(context).primary
                                          : FlutterFlowTheme.of(context)
                                              .secondaryText,
                                      FlutterFlowTheme.of(context)
                                          .secondaryText,
                                    ),
                                    width: 0.5,
                                  ),
                                ),
                                child: Padding(
                                  padding: EdgeInsetsDirectional.fromSTEB(
                                      10.0, 10.0, 10.0, 10.0),
                                  child: Column(
                                    mainAxisSize: MainAxisSize.max,
                                    mainAxisAlignment: MainAxisAlignment.center,
                                    crossAxisAlignment:
                                        CrossAxisAlignment.start,
                                    children: [
                                      Row(
                                        mainAxisSize: MainAxisSize.max,
                                        children: [
                                          Padding(
                                            padding:
                                                EdgeInsetsDirectional.fromSTEB(
                                                    0.0, 0.0, 3.0, 0.0),
                                            child: ClipRRect(
                                              borderRadius:
                                                  BorderRadius.circular(8.0),
                                              child: Image.asset(
                                                'assets/images/bardStars.png',
                                                width: 15.0,
                                                height: 15.0,
                                                fit: BoxFit.cover,
                                              ),
                                            ),
                                          ),
                                          Expanded(
                                            child: Container(
                                              width: 100.0,
                                              decoration: BoxDecoration(),
                                              child: Text(
                                                valueOrDefault<String>(
                                                  functions.dateTimeFormat(
                                                      getJsonField(
                                                    chatItem,
                                                    r'''$.last_modified_time''',
                                                  )),
                                                  'Just now',
                                                ).maybeHandleOverflow(
                                                  maxChars: 30,
                                                  replacement: '…',
                                                ),
                                                style:
                                                    FlutterFlowTheme.of(context)
                                                        .bodyMedium
                                                        .override(
                                                          fontFamily: 'Poppins',
                                                          fontSize: 10.0,
                                                        ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                      Row(
                                        mainAxisSize: MainAxisSize.max,
                                        children: [
                                          Expanded(
                                            child: Padding(
                                              padding: EdgeInsetsDirectional
                                                  .fromSTEB(0.0, 2.0, 0.0, 0.0),
                                              child: Container(
                                                width: 100.0,
                                                decoration: BoxDecoration(),
                                                child: Text(
                                                  valueOrDefault<String>(
                                                    getJsonField(
                                                      chatItem,
                                                      r'''$.title''',
                                                    ).toString(),
                                                    'New Chat',
                                                  ).maybeHandleOverflow(
                                                    maxChars: 30,
                                                    replacement: '…',
                                                  ),
                                                  style: FlutterFlowTheme.of(
                                                          context)
                                                      .bodyMedium
                                                      .override(
                                                        fontFamily: 'Poppins',
                                                        fontSize: 11.0,
                                                        fontWeight:
                                                            FontWeight.w500,
                                                      ),
                                                ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                      Row(
                                        mainAxisSize: MainAxisSize.max,
                                        children: [
                                          Expanded(
                                            child: Padding(
                                              padding: EdgeInsetsDirectional
                                                  .fromSTEB(0.0, 2.0, 0.0, 0.0),
                                              child: Container(
                                                width: 100.0,
                                                decoration: BoxDecoration(),
                                                child: Padding(
                                                  padding: EdgeInsetsDirectional
                                                      .fromSTEB(
                                                          0.0, 2.0, 0.0, 0.0),
                                                  child: Text(
                                                    valueOrDefault<String>(
                                                      getJsonField(
                                                        chatItem,
                                                        r'''$.llm_type''',
                                                      ).toString(),
                                                      'VertexAI-Chat',
                                                    ).maybeHandleOverflow(
                                                      maxChars: 30,
                                                      replacement: '…',
                                                    ),
                                                    style: FlutterFlowTheme.of(
                                                            context)
                                                        .bodyMedium
                                                        .override(
                                                          fontFamily: 'Poppins',
                                                          color: FlutterFlowTheme
                                                                  .of(context)
                                                              .secondaryText,
                                                          fontSize: 9.0,
                                                          fontWeight:
                                                              FontWeight.w500,
                                                        ),
                                                  ),
                                                ),
                                              ),
                                            ),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                              ),
                            ),
                          );
                        },
                      );
                    },
                  );
                },
              ),
            ),
          ),
          Row(
            mainAxisSize: MainAxisSize.max,
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              FlutterFlowIconButton(
                borderColor: Color(0x004490DB),
                borderRadius: 10.0,
                borderWidth: 1.0,
                buttonSize: 40.0,
                hoverColor: FlutterFlowTheme.of(context).primary,
                hoverIconColor: Colors.white,
                icon: Icon(
                  Icons.exit_to_app_rounded,
                  color: FlutterFlowTheme.of(context).secondaryText,
                  size: 20.0,
                ),
                onPressed: () async {
                  context.goNamed('SignIn');
                },
              ),
            ],
          ),
        ],
      ),
    );
  }
}
